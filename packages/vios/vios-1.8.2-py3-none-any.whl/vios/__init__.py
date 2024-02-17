"""vios(Virtual Input and Output System)包含以下功能模块:

1. app: 用户函数或任务定义
2. driver: 设备驱动. NOTE: 如发生改动, 需要重启server
    (1) 所有驱动继承自BaseDriver，类名统一为Driver，并要求实现open/close/read/write四个方法。样板见VirtualDevice
    (2) 以设备或厂家为名新建文件夹(并于其内新建__init__.py文件)放于driver/common内，将厂家提供的底层库(若有)置于其内

3. envelope: 执行流程，见各模块说明. NOTE: 如发生改动, 需要重启server
4. systemq: 与systemq进行交互的接口
"""


import asyncio
import inspect
import json
import string
import sys
import time
from collections import defaultdict
from functools import cached_property
from multiprocessing.shared_memory import SharedMemory
from pathlib import Path
from threading import current_thread

import numpy as np
from loguru import logger

QUARK = Path.home()/'quark'

try:
    with open(QUARK/'startup.json', 'r') as f:
        startup = json.loads(f.read())
        SYSTEMQ = str(Path(startup['site']).resolve())
        if SYSTEMQ.lower() not in sys.path:
            sys.path.append(SYSTEMQ)
except Exception as e:
    logger.error(str(e))
    startup = {}


def debug(circuit: list = [(('Measure', 0), 'Q1001')], tid: int = 0):
    from .app import get_config_by_tid
    from .envelope import ccompile, initialize
    initialize(get_config_by_tid(tid))
    return ccompile(0, {}, circuit, signal='iq')


TABLE = string.digits+string.ascii_uppercase


def basen(number: int, base: int, table: str = TABLE):
    mods = []
    while True:
        div, mod = divmod(number, base)
        mods.append(mod)
        if div == 0:
            mods.reverse()
            return ''.join([table[i] for i in mods])
        number = div


def baser(number: str, base: int, table: str = TABLE):
    return sum([table.index(c)*base**i for i, c in enumerate(reversed(number))])


def dumpv(value):
    # print('ccccccccccccccccccccccc', value)
    # if type(value).__name__ in ['Waveform', 'WaveVStack']:
    #     sl = ShareableList([dump(value)])
    #     result = ('ShareableList', sl.shm.name)
    if isinstance(value, np.ndarray):
        sm = SharedMemory(create=True, size=value.nbytes)
        buf = np.ndarray(value.shape, dtype=value.dtype, buffer=sm.buf)
        buf[:] = value[:]
        result = sm, ('SharedMemory', sm.name, buf.shape, buf.dtype.str)
        # sm.close()
    else:
        result = '', value
    return result


def loadv(value):
    if isinstance(value, tuple) and value[0] == 'SharedMemory':
        name, shape, dtype = value[1:]
        shm = SharedMemory(name=name)
        buf = np.ndarray(shape=shape, dtype=dtype, buffer=shm.buf)
        return shm, buf
    else:
        return '', value


try:
    from IPython import get_ipython

    shell = get_ipython().__class__.__name__
    if shell == 'ZMQInteractiveShell':
        from tqdm.notebook import tqdm  # jupyter notebook or qtconsole
    else:
        # ipython in terminal(TerminalInteractiveShell)
        # None(Win)
        # Nonetype(Mac)
        from tqdm import tqdm
except Exception as e:
    # not installed or Probably IDLE
    from tqdm import tqdm


class Progress(tqdm):
    """兼容JupyterProgressBar接口(from kernel)的实现
    """
    bar_format = '{desc} {percentage:3.0f}%|{bar}|{n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]'

    def __init__(self, desc='test', total=100, postfix='running', disable: bool = False):
        super().__init__([], desc, total, ncols=None, colour='blue',
                         bar_format=self.bar_format, position=0, postfix=postfix, disable=disable)

    @property
    def max(self):
        return self.total

    @max.setter
    def max(self, value: int):
        self.reset(value)

    def goto(self, index: int):
        self.n = index
        self.refresh()

    def finish(self, success: bool = True):
        self.colour = 'green' if success else 'red'
        # self.set_description_str(str(success))


class Task(object):
    """适用于大量任务连续提交(如量子云), 获取任务状态、结果、进度等.
    """

    handles = {}
    counter = defaultdict(lambda: 0)
    server = None

    def __init__(self, task: dict, timeout: float | None = None, plot: bool = False) -> None:
        """_summary_

        Args:
            task (dict): 任务描述，详见submit函数
            timeout (float | None, optional): 阻塞任务最大时间. Defaults to None.
            plot (bool, optional): 是否实时画图. 默认为False.
        """
        self.task = task
        self.timeout = timeout
        self.plot = plot

        self.data: dict[str, np.ndarray] = {}  # 从server取回的数据
        self.meta = {}  # 坐标轴等描述类信息
        self.index = 0  # 当前已取回的数据数量
        self.last = 0  # 上一次获取的数据量

        self.thread = current_thread().name

    @cached_property
    def name(self):
        return self.task['metainfo'].get('name', 'Unknown')

    @cached_property
    def ctx(self):
        return self.step(-9, 'ctx')

    def run(self):
        self.stime = time.time()  # start time
        try:
            circuit = self.task['taskinfo']['CIRQ']
            if isinstance(circuit, list) and callable(circuit[0]):
                circuit[0] = inspect.getsource(circuit[0])
        except Exception as e:
            logger.error(f'Failed to get circuit: {e}')
        self.tid = self.server.submit(self.task)

    def cancel(self):
        self.server.cancel(self.tid)
        # self.clear()

    def result(self):
        meta = True if not self.meta else False
        res = self.server.fetch(self.tid, start=self.index, meta=meta)

        if isinstance(res, str):
            return self.data
        elif isinstance(res, tuple):
            if isinstance(res[0], str):
                return self.data
            data, self.meta = res
        else:
            data = res
        self.last = self.index
        self.index += len(data)
        # data.clear()
        self.process(data)

        if callable(self.plot):
            self.plot(self, not meta)
            # self.plot(not meta)

        return self.data

    def status(self, key: str = 'runtime'):
        if key == 'runtime':
            return self.server.track(self.tid)
        elif key == 'compile':
            return self.server.apply('status', user='task')
        else:
            return 'supported arguments are: {rumtime, compile}'

    def report(self):
        return self.server.report(self.tid)

    def step(self, index: int, stage: str = 'raw'):
        """获取任务中某一步的详细信息

        Args:
            index (int): 步数.
            stage (str, optional): 任务执行所经历的阶段. Defaults to 'raw'.包括:
                > ini: 编译生成的指令.
                > raw: 映射为硬件通道后的指令及收集好的相关参数.
                > ctx: 编译所用的上下文环境(ctx).
                > debug: 由设备返回的原始数据.
                > trace: 每个指令执行所用时间.

        Returns:
            _type_: _description_
        """
        if stage in ['ini', 'raw', 'ctx']:
            return self.server.review(self.tid, index)[stage]
        elif stage in ['debug', 'trace']:
            return self.server.track(self.tid, index)[stage]

    def process(self, data: list[dict]):
        """处理从server取回的数据

        Args:
            data (list[dict]): 一维数组, 其中每个元素均为dict, 即envelope.process函数返回值.
        """
        for dat in data:
            for k, v in dat.items():
                if k in self.data:
                    self.data[k].append(v)
                else:
                    self.data[k] = [v]

    def update(self):
        try:
            self.result()
        except Exception as e:
            logger.error(f'Failed to fetch result: {e}')

        status = self.status()['status']

        if status in ['Failed', 'Canceled']:
            self.stop(self.tid, False)
            return True
        elif status in ['Running']:
            self.progress.goto(self.index)
            return False
        elif status in ['Finished', 'Archived']:
            self.progress.goto(self.progress.max)
            if hasattr(self, 'app'):
                self.app.save()
            self.stop(self.tid)
            self.result()
            return True

    def clear(self):
        self.counter.clear()
        for tid, handle in self.handles.items():
            self.stop(tid)

    def stop(self, tid: int, success: bool = True):
        try:
            self.progress.finish(success)
            self.handles[tid].cancel()
        except Exception as e:
            pass

    def bar(self, interval: float = 2.0, disable: bool = False):
        """任务进度信息. 如果timeout非零, 则同步阻塞执行, 否则异步.
        NOTE: 如果结果获取不到或者不全, 可能是save清空导致,可减小interval增加取数频率.

        Args:
            interval (float, optional): 进度刷新时间间隔, 不宜也不必过快. Defaults to 2.0.

        Raises:
            TimeoutError: 如果任务超过了认定的最大时间还未完则停止.
                实际还在执行, 只是Task不再获取数据及进度.如不需要执行, 可cancel任务.
        """
        while True:
            try:
                status = self.status()['status']
                if status in ['Pending']:
                    time.sleep(interval)
                    continue
                elif status == 'Canceled':
                    return 'Task canceled!'
                else:
                    self.progress = Progress(desc=self.name,
                                             total=self.report()['size'],
                                             postfix=self.thread, disable=disable)
                    break
            except Exception as e:
                logger.error(
                    f'Failed to get status: {e},{self.report()}')

        if isinstance(self.timeout, float):
            while True:
                if self.timeout > 0 and (time.time() - self.stime > self.timeout):
                    msg = f'Timeout: {self.timeout}'
                    logger.warning(msg)
                    raise TimeoutError(msg)
                time.sleep(interval)
                if self.update():
                    break
        else:
            self.progress.clear()
            self.refresh(interval)
        self.progress.close()

    def refresh(self, interval: float = 2.0):
        """异步获取数据并刷新进度, 不会阻塞notebook。

        Args:
            interval (float, optional): 刷新时间间隔. Defaults to 2.0.
        """
        self.progress.display()
        if self.update():
            self.progress.display()
            return
        self.handles[self.tid] = asyncio.get_running_loop(
        ).call_later(interval, self.refresh, *(interval,))
