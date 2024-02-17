"""指令生成及处理
1、线路编绎, 并返回编绎后的结果及相关额外参数
2、将1得到的结果进行硬件解析, 并整合所需参数, 最后送入calculator处理
"""

import os
import time
from typing import Any

import numpy as np
from loguru import logger

from vios import dumpv

from .systemq import (Capture, CompilerContext, Waveform, WaveVStack, _compile,
                      _form_signal, assembly_code, get_all_channels, square,
                      stdlib, wave_eval)

cfg = CompilerContext({})  # cfg (CompilerContext): 线路编绎所需配置


def initialize(snapshot, **kwds):
    """初始化编译上下文环境, 即每个线路对应的当前的cfg表. 
    NOTE:对于每个任务, 都会冻结一个cfg快照snapshot, 任务执行时对cfg表的操作不会影响此次任务.

    Args:
        snapshot (_type_): 当前的cfg表

    Returns:
        CompilerContext: 用于编译的上下文环境

    """
    if isinstance(snapshot, int):
        return os.getpid()
    cfg.reset(snapshot)
    cfg.initial = kwds.get('initial', {'restore': []})
    cfg.bypass = kwds.get('bypass', {})
    cfg._keys = kwds.get('keys', [])
    return cfg


def ccompile(sid: int, instruction: dict, circuit: list, **kwds):
    """编绎线路, 生成可执行的指令, 包括波形生成、采集卡参数、触发设置等

    Args:
        sid (int): 任务步数
        instruction (dict): 默认执行步骤, 与编译后的结果(即compiled)合并, 便于扩展额外指令
        circuit (list): 用户定义的线路(@HK)

    Returns:
        tuple: 编绎后的线路, 数据处理所需参数

    >>> from quark import connect
    >>> s = connect('QuarkServer')
    >>> cfg = initialize(s.snapshot())
    >>> circuit = [(('Measure',0),'Q0503')]
    >>> instruction, datamap =ccompile(0,circuit,signal='iq')
    >>> instruction(没有assemble过)
    {'main': [('WRITE', 'Q0503.waveform.DDS', <waveforms.waveform.Waveform at 0x291381b6c80>, ''),
              ('WRITE', 'M5.waveform.DDS', <waveforms.waveform.Waveform at 0x291381b7f40>, ''),
              ('WRITE', 'ADx86_159.CH5.Shot', 1024, ''),
              ('WRITE', 'ADx86_159.CH5.Coefficient', {'start': 2.4000000000000003e-08,
                                                      'stop': 4.0299999999999995e-06,
                                                      'wList': [{'Delta': 6932860000.0,
                                                                  'phase': 0,
                                                                  'weight': 'const(1)',
                                                                  'window': (0, 1024),
                                                                  'w': None,
                                                                  't0': 3e-08,
                                                                  'phi': -0.7873217091999384,
                                                                  'threshold': 2334194991.172387}]}, ''),
              ('WRITE', 'ADx86_159.CH5.TriggerDelay', 7e-07, ''),
              ('WRITE', 'ADx86_159.CH5.CaptureMode', 'alg', ''),
              ('WRITE', 'ADx86_159.CH5.StartCapture', 54328, '')],
     'READ': [('READ', 'ADx86_159.CH5.IQ', 'READ', '')]}
     >>> datamap
    {'dataMap': {'cbits': {0: ('READ.ADx86_159.CH5', 0, 6932860000.0, {'duration': 4e-06,
                                                                    'amp': 0.083,
                                                                    'frequency': 6932860000.0,
                                                                    'phase': [[-1, 1], [-1, 1]],
                                                                    'weight': 'const(1)',
                                                                    'phi': -0.7873217091999384,
                                                                    'threshold': 2334194991.172387,
                                                                    'ring_up_amp': 0.083,
                                                                    'ring_up_waist': 0.083,
                                                                    'ring_up_time': 5e-07,
                                                                    'w': None},
                            3e-08,
                            2.4000000000000003e-08,
                            4.0299999999999995e-06)},
                'signal': 2,
                'arch': 'baqis'}}

    """
    kwds['signal'] = _form_signal(kwds.get('signal'))
    kwds['lib'] = kwds.get('lib', stdlib)

    ctx = kwds.get('ctx', cfg)
    ctx.snapshot().cache = kwds.get('cache', {})

    align_right = kwds.pop('align_right', True)
    waveform_length = kwds.pop('waveform_length', 98e-6)
    if kwds.pop('fillzero', False):  # 是否将所有通道初始化为zero()
        compiled = {'main': [('WRITE', target, 'zero()', '')
                             for target in get_all_channels(ctx)]}
    else:
        compiled = {}

    code = _compile(circuit, cfg=ctx, **kwds)

    if align_right:
        delay = waveform_length - code.end

        code.waveforms = {k: v >> delay for k, v in code.waveforms.items()}
        code.measures = {
            k:
            Capture(v.qubit, v.cbit, v.time + delay, v.signal,
                    v.params, v.hardware, v.shift + delay)
            for k, v in code.measures.items()
        }

    cmds, datamap = assembly_code(code)

    for cmd in cmds:
        ctype = type(cmd).__name__  # WRITE,TRIG,READ
        if ctype == 'WRITE':
            step = 'main'
        else:
            step = ctype
        op = (ctype, cmd.address, cmd.value, 'au')
        if step in compiled:
            compiled[step].append(op)
        else:
            compiled[step] = [op]

    # merge loop body with compiled result
    for step, _cmds in compiled.items():
        if step in instruction:
            instruction[step].extend(_cmds)
        else:
            instruction[step] = _cmds
    assemble(sid, instruction, prep=False, hold=kwds.get('hold', False))
    if sid == 0:
        kwds['restore'] = cfg.initial
        kwds['clear'] = True
    logger.info(f'Step {sid} compiled >>>>>>>>>>>>>')
    return instruction, {'dataMap': datamap} | kwds


def assemble(sid: int, instruction: dict[str, list[str, str, Any, str]], **kw):
    """重组编译(ccompile)生成的指令集合(见cccompile), 并生成相应的硬件操作指令

    Args:
        sid (int): 任务步数
        instruction (dict[str, list[str, str, Any, str]]): 编译生成的指令集合(见ccompile), 可能包括额外的操作

    Raises:
        TypeError: srate应为浮点数, 否则设置为-1.0
    """

    try:
        query = kw.get('ctx', cfg).query
    except AttributeError as e:
        query = cfg.query

    for step, operations in instruction.items():
        if not isinstance(operations, list):
            break
        scmd = {}
        for ctype, target, value, unit in operations:
            kwds = {'sid': sid, 'target': target,
                    'track': query('etc.track'),
                    'shared': query('etc.shared'),
                    'filter': query('etc.filter')}
            if 'CH' in target or ctype == 'WAIT':
                _target = target
            else:
                try:
                    # 逻辑通道转为硬件通道并提取相关参数用于后续计算
                    context = query(target.split('.', 1)[0])
                    mapping = query('etc.mapping')
                    _target = decode(target, context, mapping)
                    kwds.update({"context": context})
                except (ValueError, KeyError) as e:
                    continue

                # 获取初始值以在任务结束时恢复仪器设置
                if sid == 0 and not kw.get('hold', False):
                    init = query(target.removesuffix(
                        '.I').removesuffix('.Q'))
                    cfg.initial['restore'].append((ctype, target, init, unit))

            # 从dev中获取设备相应的采样率
            if ctype != 'WAIT':
                dev = _target.split('.', 1)[0]
                kwds['srate'] = query(f'dev.{dev}.srate')
                if not kwds['srate']:
                    logger.critical(f'Failed to get srate for {dev}!')
            cmd = [ctype, value, unit, kwds]

            # 处理多指令共用通道逻辑(如多个波形同一通道)
            try:
                if _target in scmd and 'waveform' in target.lower():
                    if isinstance(scmd[_target][1], str):
                        scmd[_target][1] = wave_eval(scmd[_target][1])
                    if isinstance(cmd[1], str):
                        cmd[1] = wave_eval(cmd[1])
                    scmd[_target][1] += cmd[1]
                else:
                    scmd[_target] = cmd
            except Exception as e:
                logger.warning(f'Channel[{_target}] mutiplexing error: {e}')
                scmd[_target] = cmd
        instruction[step] = scmd

    # 是否进行预处理
    if kw.get('prep', True):
        return preprocess(sid, instruction)


# 设备通道与config表中字段的映射关系
MAPPING = {
    "setting_LO": "LO.Frequency",
    "setting_POW": "LO.Power",
    "setting_OFFSET": "ZBIAS.Offset",
    "waveform_RF_I": "I.Waveform",
    "waveform_RF_Q": "Q.Waveform",
    "waveform_TRIG": "TRIG.Marker1",
    "waveform_DDS": "DDS.Waveform",
    "waveform_SW": "SW.Marker1",
    "waveform_Z": "Z.Waveform",
    "setting_PNT": "ADC.PointNumber",
    "setting_SHOT": "ADC.Shot",
    "setting_TRIGD": "ADC.TriggerDelay"
}


# 指令过滤
SUFFIX = ('Waveform', 'Shot', 'Coefficient', 'TriggerDelay')


def decode(target: str, context: dict, mapping: dict = MAPPING):
    """Qubit等属性与硬件通道之间的映射转换

    Args:
        target (str): 待解析对象, 如Q0.setting.LO
        context (dict): 对象所在cfg的字段
        mapping (dict, optional): 通道和硬件属性的映射关系. Defaults to MAPPING.

    Raises:
        KeyError: 通道映射不存在
        ValueError: 通道不存在

    Returns:
        str: 通道, 如AD.CH1.TraceIQ
    """
    try:
        mkey = target.split('.', 1)[-1].replace('.', '_')
        chkey, quantity = mapping[mkey].split('.', 1)
    except KeyError as e:
        raise KeyError(f'{e} not found in mapping!')

    try:
        channel = context.get('channel', {})[chkey]
    except KeyError as e:
        raise KeyError(f'{chkey} not found!')

    if channel is None:
        raise ValueError('ChannelNotFound')
    elif not isinstance(channel, str):
        raise TypeError(
            f'Wrong type of channel of {target}, string needed got {channel}')
    elif 'Marker' not in channel:
        channel = '.'.join((channel, quantity))

    return channel


WINDOW = square(500e-3) >> 150e-3


def equal(a, b):
    if isinstance(a, WaveVStack) or isinstance(b, WaveVStack):
        return False
    if isinstance(a, Waveform) and isinstance(b, Waveform):
        return (a*WINDOW) == (b*WINDOW)
    try:
        return a == b
    except Exception as e:
        # logger.warning(f'Failed to compare {e}')
        return False


def preprocess(sid: int, instruction: dict[str, dict[str, list[str, Any, str, dict]]]):
    """预处理,包括过滤/参数查取等, 处理完毕送往calculator进行采样等计算. 

    Args:
        sid (int):任务步数
        instruction (dict):指令集合, 形如{step: {target: [ctype, value, unit, kwds]}}

    >>> instruction具体含义如下
    - step (str): 执行步骤, 如main/step1/step2
    - target (str): 设备通道属性, 如AWG.CH1.Waveform、AD.CH2.TraceIQ
        - ctype (str): 操作类型, 共三种, 分别为READ/WRITE/WAIT
        - value (Any): 待操作值, READ无值, WAIT为浮点数单位为秒, WRITE值任意, 详见driver
        - unit (str): 指令单位, 暂无作用
        - kwds (dict): 来自assemble, 主要包括以下内容
            - sid (int): 任务步数
            - track (list): 指定要保留中间执行过程详细的步数
            - target (str): 原始指令如Q0101.waveform.Z
            - filter (list): calculator中波形是否采样并显示到canvas
            - srate (float): 对应设备采样率,来自dev
            - context (dict): cfg表中字段, 如Q0101
    """
    if sid == 0:
        cfg.bypass.clear()
    bypass = cfg.bypass

    shared = []
    for step, operations in instruction.items():
        if not isinstance(operations, dict):
            break
        scmd = {}
        for target, cmd in operations.items():
            try:
                kwds = cmd[-1]
                # 重复指令缓存比较, 如果与上一步相同, 则跳过执行
                if target in bypass and target.endswith(SUFFIX) and equal(bypass[target][0], cmd[1]):
                    continue
                bypass[target] = (cmd[1], kwds['target'])

                # context设置, 用于calculator.calculate
                context = kwds.pop('context', {})  # 即cfg表中的Qubit、Coupler等
                if context:
                    kwds['LEN'] = context['waveform']['LEN']
                    kwds['calibration'] = context['calibration']

                # if isinstance(cmd[1], Waveform):
                #     cmd[1].sample_rate = kwds['srate']
                #     cmd[1].start = 0
                #     cmd[1].stop = 1e-3  # kwds['LEN']
                #     cmd[1] = cmd[1].sample()

                if kwds['shared']:
                    sm, value = dumpv(cmd[1])
                    if sm:
                        shared.append(sm)
                        cmd[1] = value
            except Exception as e:
                logger.error(f'Failed to preprocess {target}, {e}!')
            scmd[target] = cmd
        instruction[step] = scmd

    return shared


# %%
if __name__ == "__main__":
    import doctest
    doctest.testmod()
