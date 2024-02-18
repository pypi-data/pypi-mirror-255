# -*- coding: utf-8 -*-
# HuYueyong, 2024

"""ZigZag算法（拐点识别）"""


import sys
import logging
from dataclasses import dataclass
import numpy as np
import pandas as pd
from dramkit.const import (
    SeriesType,
    NumOrNoneType,
    FloatOrNoneType,
    IntOrNoneType
)
from dramkit.gentools import (
    isna,
    catch_error,
    catch_warnings,
    raise_warn
)
from dramkit.logtools import logger_show

_MAX = sys.maxsize


@dataclass
class ZigZagParams(object):
    t_min: IntOrNoneType = 0
    pct_min: FloatOrNoneType = 0.0  # eg. 1/100
    val_min: NumOrNoneType = None
    t_max: IntOrNoneType = _MAX
    pct_max: FloatOrNoneType = None
    val_max: NumOrNoneType = None
    t_min_up: IntOrNoneType = None
    t_min_down: IntOrNoneType = None
    t_max_up: IntOrNoneType = None
    t_max_down: IntOrNoneType = None
    pct_min_up: FloatOrNoneType = None  # eg. 1/100
    pct_min_down: FloatOrNoneType = None  # eg. -1/100
    pct_max_up: FloatOrNoneType = None
    pct_max_down: FloatOrNoneType = None
    val_min_up: NumOrNoneType = None
    val_min_down: NumOrNoneType = None
    val_max_up: NumOrNoneType = None
    val_max_down: NumOrNoneType = None
    zigzag: SeriesType = None
    pct_v00: float = 1.0
    logger: logging.Logger = None
    
    def check(self):
        """参数转化和检查"""
        self.t_min_up = self.t_min if isna(self.t_min_up) else self.t_min_up
        self.t_min_down = self.t_min if isna(self.t_min_down) else self.t_min_down
        self.t_max_up = self.t_max if isna(self.t_max_up) else self.t_max_up
        self.t_max_down = self.t_max if isna(self.t_max_down) else self.t_max_down
        self.pct_min_up = self.pct_min if isna(self.pct_min_up) else self.pct_min_up
        self.pct_max_up = self.pct_max if isna(self.pct_max_up) else self.pct_max_up
        self.val_min_up = self.val_min if isna(self.val_min_up) else self.val_min_up
        self.val_max_up = self.val_max if isna(self.val_max_up) else self.val_max_up
        self.pct_min_down = -1*self.pct_min if (isna(self.pct_min_down) and (not isna(self.pct_min))) else self.pct_min_down
        self.pct_max_down = -1*self.pct_max if (isna(self.pct_max_down) and (not isna(self.pct_max))) else self.pct_max_down
        self.val_min_down = -1*self.val_min if (isna(self.val_min_down) and (not isna(self.val_min))) else self.val_min_down
        self.val_max_down = -1*self.val_max if (isna(self.val_max_down) and (not isna(self.val_max))) else self.val_max_down
        
        # 最小间隔点参数
        for arg in ['t_min', 't_min_up', 't_min_down',]:
            arg_val = eval('self.%s'%arg)
            if isna(arg_val) or arg_val < 0:
                raise_warn('ZigZagParamWarn', '转折点之间的最小间隔点参数将设置为0！')
                exec('self.%s = 0'%arg)
                
        # 最大间隔点参数
        for arg in ['t_max', 't_max_up', 't_max_down']:
            arg_val = eval('self.%s'%arg)
            if isna(arg_val) or arg_val < 0:
                raise_warn('ZigZagParamWarn', '转折点之间的最大间隔点参数将设置为无穷大！')
                exec('self.%s = _MAX'%arg)
                
        # 上涨-长时最小幅度参数
        if not isna(self.pct_min_up) and not isna(self.val_min_up):
            raise_warn('ZigZagParamWarn', '同时设置`pct_min_up`和`val_min_up`，以`pct_min_up`为准！')
            self.val_min_up = -1.0
        elif isna(self.pct_min_up) and isna(self.val_min_up):
            raise_warn('ZigZagParamWarn', '`pct_min_up`和`val_min_up`均未设置！')
            self.pct_min_up = self.val_min_up = -1.0
        elif isna(self.pct_min_up):
            self.pct_min_up = -1.0
        elif isna(self.val_min_up):
            self.val_min_up = -1.0

        # 上涨-短时最大幅度参数
        if not isna(self.pct_max_up) and not isna(self.val_max_up):
            raise_warn('ZigZagParamWarn', '同时设置`pct_max_up`和`val_max_up`，以`pct_max_up`为准！')
            val_max_up = None
        
        # # 下跌-长时最小幅度参数
        # assert not (isna(pct_min_down) and isna(val_min_down)), \
        #     '必须设置`pct_min_down`或`val_min_down`, 若要忽略此参数，可将其设置为正数'
        # if not isna(pct_min_down) and not isna(val_min_down):
        #     logger_show('同时设置`pct_min_down`和`val_min_down`，以`pct_min_down`为准！',
        #                 logger, 'warn')
        #     val_min_down = None
        
        # # 下跌-短时最大幅度参数
        # if not isna(pct_max_down) and not isna(val_max_down):
        #     logger_show('同时设置`pct_max_down`和`val_max_down`，以`pct_max_down`为准！',
        #                 logger, 'warn')
        #     val_max_down = None


@catch_warnings()
@catch_error()
def find_zigzag(high: SeriesType,
                low: SeriesType,
                *args,
                **kwargs
                ) -> SeriesType:
    """ZigZag转折点
    
    条件1：转折点之间的间隔点数大于等于t_max（默认参数为不满足）
    条件2：转折点之间的间隔点数大于等于t_min（默认参数为满足）
    条件3：转折点之间变化幅度大于等于pct_min或val_min（默认参数为满足）
    条件4：转折点之间变化幅度大于等于pct_max或val_max（默认参数为不满足）
    转折点确认条件：
        条件1 or (条件2 and 条件3) or ((not 条件2) and 条件4)

    Parameters
    ----------        
    high : SeriesType
        high序列数据
    low : SeriesType
        low序列数据
    t_min : int
        转折点之间的最小时间距离（间隔点的个数）
    pct_min : float
        在满足t_min参数设置的条件下，转折点和上一个转折点的最小变化百分比
        （应为正数，如1/100）
    val_min : float
        在满足t_min参数设置的条件下，转折点和上一个转折点的最小变化绝对值
        （若pct_min设置，则此参数失效）
    t_max : int
        转折点之间的最大时间距离若超过t_max，即视为满足转折条件
    pct_max : float
        在不满足t_min参数设置的条件下，转折点和上一个转折点的变化百分比若超过此参数值，则视为满足转折条件
    val_max : float
        在不满足t_min参数设置的条件下，转折点和上一个转折点的变化绝对值若超过此参数值，则视为满足转折条件
        （若pct_max设置，则此参数失效）
    t_min_up : int
        同 `t_min` ，只控制上涨
    t_min_down : int
        同 `t_min` ，只控制下跌
    t_max_up : int
        同 `t_max` ，只控制上涨
    t_max_down : int
        同 `t_max` ，只控制下跌
    pct_min_up : float
        同 `pct_min` ，只控制上涨
    pct_min_down : float
        同 `pct_min` ，只控制下跌（应为负数，如-1/100）
    pct_max_up : float
        同 `pct_max` ，只控制上涨
    pct_max_down : float
        同 `pct_max` ，只控制下跌
    val_min_up : float
        同 `val_min` ，只控制上涨
    val_min_down : float
        同 `val_min` ，只控制下跌
    val_max_up : float
        同 `val_max` ，只控制上涨
    val_max_down : float
        同 `val_max` ，只控制下跌
    zigzag : SeriesType
        可传入已有的zigzag结果，会寻找最近一个转折点确定的位置，然后增量往后计算
    pct_v00 : float
        计算百分比时分母为0指定结果
    logger : logging.Logger
        日志记录器

    Returns
    -------
    zigzag : SeriesType
        返回zigzag标签序列，其中1|-1表示确定的高|低点；0.5|-0.5表示未达到偏离条件而不能确定的高低点。
    """
    params = ZigZagParams(*args, **kwargs)
    params.check()
    
    
if __name__ == "__main__":
    params = ZigZagParams(2, pct_min=-1/100, pct_max=2/100, t_max=100)
    params.check()
    params = ZigZagParams(2, pct_max=2/100, t_max=100, logger=None)
    params.check()
    # print(params)
    
    a = find_zigzag(1, 2)
