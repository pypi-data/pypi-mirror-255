"""本模块主要供用户使用
>>> init模块: 提交任务(submit)/获取数据(get_data_by_tid)/回滚参数(rollback)/画图(plot)
>>> demo模块: 一些任务定义的例子
>>> task模块: 从kernel的App兼容而来的各种Scanner(原有使用行为不变)
>>> uapi模块: 与前端进行交互, 如matplotlib画图、数据库查询等, 详见各函数说明. 
"""

import time
from collections import defaultdict
from ipaddress import ip_address
from pathlib import Path
from threading import current_thread

import numpy as np
from loguru import logger
from quark import connect

from vios import Task, startup
from .data import get_config_by_tid, get_dataset_by_tid

from .task import Scan, Scanner

srv = startup['quarkserver']
host, port = srv.get('host', '127.0.0.1'), srv.get('port', 2088)
localhost = True if ip_address(host).is_loopback else False
sp = defaultdict(lambda: connect('QuarkServer', host, port))
_vs = connect('QuarkViewer', port=2086)


def signup(user: str, system: str, **kwds):
    """注册用户, 并绑定到指定的芯片系统

    Args:
        user (str): 用户名
        system (str): 芯片系统名即cfg表名
    """
    s = sp[current_thread().name]
    logger.info(s.adduser(user, system, **kwds))


def login(user: str = 'baqis', verbose: bool = True):
    """登录到server

    Args:
        user (str, optional): 用户名, 与signup中一致. Defaults to 'baqis'.
        verbose (bool, optional): 是否打印登录信息. Defaults to True.

    Returns:
        _type_: 到server的连接
    """
    s = sp[current_thread().name]
    m = s.login(srv.get('user', user))
    if verbose:
        logger.info(m)
    return s


def submit(app: dict | Scan | Scanner, block: bool = False,
           shot: int = 0, reset: list = [], fillzero: bool = False,
           preview: list = [], title: list[tuple] = [], interval: float = 2.0, **kwds):
    """转换继承自App的任务为server可执行任务

    Args:
        app (dict | Scan | Scanner): 任务基类, 必须实现circuits方法.
        block (bool, optional): 是否阻塞任务, 用于多个任务顺序执行.
        shot (int, optional): 任务开始前设置shot, 一般不需要.
        reset (bool, optional): 任务开始前执行，重置设备指令列表, 如[('WRITE','Q0.waveform.Z','zero()','au')].
        fillzero (bool, optional): 是否在编译前将所有通道初始化为zero().
        preview (list, optional): 需要实时显示的波形, 对应etc.preview.filter.
        title (list[tuple], optional): 画图所显示的标题, 如不指定则由任务生成.
        interval (float, optional): 画图刷新频率. 默认2秒.

    Kwds:
        plot (bool): 是否需要实时显示结果(1D或2D), 默认为False.
        dry_run (bool): 如果为True则跳过设备但波形正常计算并显示, 默认为False.

    Raises:
        TypeError: _description_

    任务字典整体分两个字段:
    >>> metainfo (dict):
      > name (str): filename:/s21, filename表示数据将存储于filename.hdf5中, s21为实验名字, 以:/分隔
      > user (str): 实验者代号. 默认为usr. 
      > tid (int): 任务id, 全局唯一, 如不指定, 则由系统生成. 
      > priority (int): 优先级, 任务同时提交时, 优先级数值小的先执行. 默认为0. 
      > other (dict): 其他参数, 如shots、signal等, 作为kwds传递给ccompile(见envelope.assembler)
    >>> taskinfo (dict):
      > STEP (dict): 大写, 描述任务执行的变量(即for循环变量)与执行步骤(即for循环体)
      > CIRQ (list | str): 大写, 描述任务线路, 长度等于STEP中for循环变量长度. 可为空. 
      > INIT (list): 大写, 任务初始化设置. 可为空. 
      > RULE (list): 大写, 变量关系列表, 可为表达式或空, 如[f'<gate.rfUnitary.{q}.params.frequency>=<freq.{q}>']. 可为空. 
      > LOOP (dict): 大写, 定义循环执行所用变量, 与STEP中main的值对应, STEP中main所用变量为LOOP的子集
    """

    ss = login(verbose=False)
    if preview:
        ss.update('etc.preview.filter', preview)  # 待预览波形

    if reset:
        ss.feed(0, 0, {'reset': reset})  # 任务提交前的设置

    if isinstance(app, dict):
        t = Task(app)
        t.server = ss
        t.plot = plot if kwds.get('plot', False) else False
        t.timeout = 1e9 if block else None
        t.run()
        return t

    app.toserver = 'ready'
    app.run(dry_run=True, quiet=True)
    time.sleep(3)

    filepath = Path.cwd()/f'circuit/{app.name.replace(".", "_")}.cirq'
    filepath.parent.mkdir(parents=True, exist_ok=True)
    qubits, circuits = app.dumps(filepath, localhost)

    # loops = app.variables()
    loops, deps = app.resolve()
    sample = ss.query('station.sample')
    trigger = ss.query('station.triggercmds')

    init = [(f'{t.split(".")[0]}.CH1.Shot', app.shots, 'any')
            for t in trigger] if shot else []

    if ss.query('etc.username').startswith('Failed'):
        ss.update('etc.username', 'baqis')

    t = Task({'metainfo': {'name': f'{sample}:/{filepath.stem}',
                           #    'user': ss.query('etc.username'),
                           'tid': app.id,
                           'priority': app.task_priority,
                           'other': {'shots': app.shots,
                                     'signal': app.signal,
                                     #  'lib': app.lib, # WindowsPath error on Mac
                                     'align_right': app.align_right,  # 波形对齐方式
                                     'waveform_length': app.waveform_length,  # 波形长度
                                     'fillzero': fillzero,
                                     'autorun': not kwds.get('dry_run', False),
                                     'hold': app.runtime.keep_last_status,
                                     'timeout': 1000.0}  # 编译超时
                           },

              'taskinfo': {'STEP': {'main': ['WRITE', tuple(loops)],  # 主循环，写波形等设置
                                    'trigger': ['WRITE', 'trig'],  # 触发
                                    # 'wait':['WAIT',0.5],
                                    'READ': ['READ', 'read'],  # 读取
                                    },
                           'INIT': init,  # 任务开始前的初始化
                           'RULE': deps,
                           'CIRQ': circuits if circuits else str(filepath.resolve()),
                           'LOOP': loops | {'trig': [(t, 0, 'au') for t in trigger]}
                           }
              }
             )

    t.server = ss
    t.timeout = 1e9 if block else None
    t.plot = plot if kwds.get('plot', False) else False

    t.app = app
    t.title = title if title else qubits
    app.toserver = t
    app.run()
    app.bar(interval)


def rollback(tid: int):
    """将cfg表回滚至指定的任务id

    Args:
        tid (int): 任务id,与submit中tid相同
    """
    from vios import get_config_by_tid

    _s = login(verbose=False)

    try:
        config = get_config_by_tid(tid)
        _s.clear()
        for k, v in config.items():
            _s.create(k, v)
    except Exception as e:
        logger.error(f'Failed to rollback: {e}')


def get_data_by_tid(tid: int, signal: str, shape: tuple | list = [], **kwds):
    """根据任务id从hdf5获取数据

    Args:
        tid (int): 任务id
        signal (str): 指定需要画的数据.
        shape (tuple|list): data shape, 如果不指定尝试从记录中推出,形如(*sweeps, *(shots, qubits))

    Kwds:
        plot (bool, optional): 是否需要实时显示结果(1D或2D).

    Returns:
        tuple: 数据体、元信息、cfg表
    """
    from vios import get_dataset_by_tid
    info, data = get_dataset_by_tid(tid, signal, shape)

    if kwds.get('plot', False) and signal:
        task = Task({'metainfo': info['meta']})
        task.meta = info['meta']
        task.data = {signal: data[signal]}
        task.index = len(data[signal]) + 1
        plot(task)

    return {'data': data, 'meta': info['meta']}


def update_remote_wheel(filenames: list[str], host: str = '127.0.0.1'):
    """更新远端设备的库

    Args:
        filename (list[str]): 本地库文件名
        host (str, optional): 远端设备ip地址. Defaults to '127.0.0.1'.

    Returns:
        str: 更新信息(失败或成功)
    """
    wheel = {}
    for filename in filenames:
        with open(filename, 'rb') as f:
            wheel[filename] = f.read()
    rs = connect('QuarkRemote', host=host, port=2087)
    print(rs.install(wheel))


def plot(task: Task, append: bool = False):
    """实时画图

    Args:
        append (bool, optional): 绘图方法, 首次画图(False)或增量数据画图(True).

    NOTE: 子图数量不宜太多(建议最大6*6), 单条曲线数据点亦不宜过多(建议不超过5000)

    使用说明:
    - 输入的数据为[[dict]]结构, 即二维的list, 其中每个元素均为dict
    - 外层list表示每行子图数
    - 内层list表示每列子图数
    - 每个dict存储子图数据, 可为一维(可以多条曲线)或二维
    - 每条曲线或二维图的属性(颜色/线宽等)与matplotlib中名称一致(大多情况下)
    """
    if 'population' in str(task.meta['other']['signal']):
        signal = 'population'
    else:
        signal = str(task.meta['other']['signal']).split('.')[-1]
    raw = np.asarray(task.data[signal][task.last:task.index])

    if signal == 'iq':
        state = {0: 'b', 1: 'r', 2: 'g'}  # 012态颜色
        label = []
        xlabel, ylabel = 'real', 'imag'
        append = False
    else:
        raw = np.abs(raw)

        axis = task.meta['axis']
        label = tuple(axis)
        if len(label) == 1:
            xlabel, ylabel = label[0], 'Any'
            # xdata = axis[xlabel][xlabel][task.last:task.index]
            if not hasattr(task, 'xdata'):
                task.xdata = np.asarray(list(axis[xlabel].values())).T
            xdata = task.xdata[task.last:task.index]
            ydata = raw
        elif len(label) == 2:
            xlabel, ylabel = label
            # xdata = axis[xlabel][xlabel]
            if not hasattr(task, 'xdata'):
                task.xdata = np.asarray(list(axis[xlabel].values())).T
                task.ydata = np.asarray(list(axis[ylabel].values())).T
            # ydata = axis[ylabel][ylabel]
            xdata = task.xdata
            ydata = task.ydata
            zdata = raw
        if len(label) > 3:  # 画图最多二维
            return

    uname = f'{task.name}_{xlabel}'
    if task.last == 0:
        if uname not in task.counter or len(label) == 2 or signal == 'iq':
            _vs.clear()  # 清空画板
            task.counter.clear()  # 清空任务历史
        else:
            task.counter[uname] += 1
        _vs.info(task.task)

    col = 4
    div, mod = divmod(raw.shape[-1], col)
    row = div if mod == 0 else div+1
    time.sleep(0.1)  # 防止刷新过快导致卡顿
    try:
        data = []  # 外层list
        for r in range(row):
            rd = []  # 内层list
            for c in range(col):
                idx = r*col+c

                try:
                    _name = task.app.name.split('.')[-1]
                    _title = f'{_name}_{task.app.record_id}_{task.title[idx][1]}'
                except Exception as e:
                    _title = f'{r}_{c}'

                # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                cell = {}  # 子图数据
                line = {}

                if signal == 'iq':  # 散点图
                    try:
                        for i, iq in enumerate(raw[..., idx]):
                            si = i + task.last
                            cell[si] = {'xdata': iq.real.squeeze(),
                                        'ydata': iq.imag.squeeze(),
                                        'xlabel': xlabel,
                                        'ylabel': ylabel,
                                        'title': _title,
                                        'linestyle': 'none',
                                        'marker': 'o',
                                        'markersize': 5,
                                        'markercolor': state[si]}
                    except Exception as e:
                        continue

                if len(label) == 1:  # 一维图
                    try:
                        line['xdata'] = xdata[..., idx].squeeze()
                        line['ydata'] = ydata[..., idx].squeeze()
                        if task.last == 0:
                            line['linecolor'] = 'r'  # 线条颜色
                            line['linewidth'] = 2  # 线条宽度
                            line['fadecolor'] = (int('5b', 16), int(
                                'b5', 16), int('f7', 16))  # RGB渐变色, 16进制转10进制
                    except Exception as e:
                        continue

                if len(label) == 2:  # 二维图
                    try:
                        if task.last == 0:
                            line['xdata'] = xdata[..., idx]
                            line['ydata'] = ydata[..., idx]
                            line['colormap'] = 'RdBu'  # 二维图配色, 见matplotlib
                        line['zdata'] = zdata[..., idx]
                    except Exception as e:
                        continue

                if task.last == 0:
                    line['title'] = _title
                    line['xlabel'] = xlabel
                    line['ylabel'] = ylabel
                cell[f'{uname}{task.counter[uname]}'] = line
                # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

                rd.append(cell)
            data.append(rd)
        if not append:
            _vs.plot(data)  # 直接画图
        else:
            _vs.append(data)  # 增量数据画图
    except Exception as e:
        logger.error(f'Failed to update viewer: {e}')


def network():
    nodes = {}
    for i in range(5):
        for j in range(6):
            nodes[f'{i+1:02d}{j+1:02d}'] = {'index': (i*3, j*3),
                                            'color': (0, 255, 255, 255),
                                            'size': 2,
                                            'value': np.random.random(1)[0]+5}
    edges = {(i, i+1): (255, 0, 255, 180, 21) for i in range(24)}

    _vs.graph(dict(nodes=nodes, edges=edges))


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def plotdemo():
    """实时画图demo, 详细说明见plot

    >>> iq scatter
    _vs.clear()
    iq = np.random.randn(1024)+np.random.randn(1024)*1j
    _vs.plot([[
            {'i':{'xdata':iq.real-3,'ydata':iq.imag,'linestyle':'none','marker':'o','markersize':15,'markercolor':'b'},
            'q':{'xdata':iq.real+3,'ydata':iq.imag,'linestyle':'none','marker':'o','markersize':5,'markercolor':'r'},
            'hist':{'xdata':np.linspace(-3,3,1024),'ydata':iq.imag,"fillvalue":0, 'fillcolor':'r'}
            }
            ]]
            )

    >>> hist
    _vs.clear()
    vals = np.hstack([np.random.normal(size=500), np.random.normal(size=260, loc=4)])
    ## compute standard histogram
    # len(y)+1 = len(x)
    y,x = np.histogram(vals, bins=np.linspace(-3, 8, 40))

    data = [[{'hist':{'xdata':x,'ydata':y,'step':'center','fillvalue':0,'fillcolor':'g','linewidth':0}}]]
    _vs.plot(data)
    """
    row = 3  # 每行子图数
    col = 3  # 每列子图数
    # _vs.clear() # 清空画布
    for i in range(10):  # 步数
        time.sleep(.2)  # 防止刷新过快导致卡顿
        try:
            data = []
            for r in range(row):
                rd = []
                for c in range(col):
                    cell = {}
                    for j in range(1):
                        line = {}
                        line['xdata'] = np.arange(i, i+1)*1e8
                        line['ydata'] = np.random.random(1)*1e8

                        # line['xdata'] = np.arange(-9,9)*1e-6
                        # line['ydata'] = np.arange(-10,10)*1e-8
                        # line['zdata'] = np.random.random((18,20))

                        line['linewidth'] = 2
                        line['marker'] = 'o'
                        line['fadecolor'] = (255, 0, 255)
                        line['title'] = f'aabb{r}_{c}'
                        line['legend'] = 'test'
                        line['xlabel'] = f'add'
                        line['ylabel'] = f'yddd'
                        # random.choice(['r', 'g', 'b', 'k', 'c', 'm', 'y', (31, 119, 180)])
                        line['linecolor'] = (31, 119, 180)
                        cell[f'test{j}2'] = line
                    rd.append(cell)
                data.append(rd)
            if i == 0:
                _vs.plot(data)
            else:
                _vs.append(data)
        except Exception as e:
            print(e)
