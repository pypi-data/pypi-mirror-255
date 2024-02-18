# -*- coding: utf-8 -*-

import sys
import platform
import numpy as np
import pandas as pd
from beartype.typing import NewType, Union, List

#%%
# 操作系统
SYSTEM = platform.system().lower()
WIN_SYS = 'windows' in SYSTEM
LINUX_SYS = 'linux' in SYSTEM

# python版本
PY_VERSION = sys.version.split(' ')[0]
PY_VERSION2 = '.'.join([x.zfill(2) for x in sys.version.split(' ')[0].split('.')])

# windows中文件命名不允许的字符替换字符
WIN_NOT_ALLOW_FILE_STR = {
    '\\': '_bslsh_', # 反斜杠
    '/': '_slsh_', # 斜杠,
    ':': '_cln_', # 英文冒号
    '*': '_astrsk_', # 星号
    '?': '_qmrk_', # 英文问号
    '"': '_dqmrk_', # 英文双引号
    '<': '_labrkt_', # 左尖括号
    '>': '_rabrkt_', # 右尖括号
    '|': '_vl_' # 竖线
    }

#%%
NumType = NewType('NumType', Union[float, int])
NumOrNoneType = NewType('NumOrNoneType', Union[None, float, int])
FloatOrNoneType = NewType('FloatOrNoneType', Union[None, float])
IntOrNoneType = NewType('IntOrNoneType', Union[None, int])


SeriesType = NewType('SeriesType',
                     Union[pd.Series, np.ndarray, List[NumType]])

#%%
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
}

#%%
