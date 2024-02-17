
import json
import sqlite3
import sys
from pathlib import Path

import h5py
import numpy as np
from loguru import logger
from quark import loads

from vios import QUARK, startup

sql = sqlite3.connect(QUARK/'checkpoint.db', check_same_thread=False)


def get_dataset_by_tid(tid: int, signal: str, shape: tuple | list = []):
    filename, dataset = get_record_by_tid(tid)[7:9]

    info, data = {}, {}
    with h5py.File(filename) as f:
        group = f[dataset]
        info = loads(dict(group.attrs)['snapshot'])
        if not shape:
            shape = []
            for k, v in info['meta']['axis'].items():
                shape.extend(tuple(v.values())[0].shape)

        for k in group.keys():
            if k != signal or not signal:
                continue
            ds = group[f'{k}']
            data[k] = np.full((*shape, *ds.shape[1:]), 0, ds.dtype)
            data[k][np.unravel_index(np.arange(ds.shape[0]), shape)] = ds[:]
    return info, data


def get_config_by_tid(tid: int = 0):
    try:
        import git

        srv = startup['quarkserver']
        ckpt = '/'.join([srv['home'], 'cfg', srv['checkpoint']])
        file = Path(ckpt).with_suffix('.json')

        repo = git.Repo(file.resolve().parent)
        if not tid:
            tree = repo.head.commit.tree
        else:
            tree = repo.commit(get_record_by_tid(tid)[-1]).tree
        config: dict = loads(tree[file.name].data_stream.read().decode())
        return config
    except Exception as e:
        logger.error(f'Failed to get config: {e}')
        return {}


def get_record_by_tid(tid: int):
    try:
        return sql.execute(f'select * from task where tid="{tid}"').fetchall()[0]
    except Exception as e:
        logger.error(f'Record not found: {e}!')


def get_record_list_by_filter(task: str, start: str, stop: str):
    try:
        return sql.execute(f'select * from task where name like "%{task}%" and created between "{start}" and "{stop}" limit 100').fetchall()
    except Exception as e:
        logger.error(f'Records not found: {e}!')


def get_record_set_by_name():
    try:
        return sql.execute('select distinct task.name from task').fetchall()
    except Exception as e:
        logger.error(f'Records not found: {e}!')
