# -*- coding: utf-8 -*-

import os
import logging
import traceback
import datetime
from pandas import isna


formatter = logging.Formatter(
'''%(message)s
    [%(levelname)s: %(asctime)s]''')
    
    
def __get_caller_pos_info(stacklevel: int):
    """获取调用此函数的语句来源于哪个Python脚本的哪一行
    """
    tgt = traceback.extract_stack()[-int(stacklevel)]
    fname, lineno, line = tgt.filename, tgt.lineno, tgt.line
    return fname, lineno, line


def __set_pos_fmt(logger):
    """临时改变logger中handlers的formatter"""
    fname, lineno, line = __get_caller_pos_info(4)
    pos_fmt = logging.Formatter(
'''DrmKtLog at {}, line: {}:
  {}
%(message)s
    [%(levelname)s: %(asctime)s]'''.format(fname, lineno, line))
    for h in logger.handlers:
        h.setFormatter(pos_fmt)
        
        
def __reset_fmt(logger):
    """恢复默认formatter"""
    for h in logger.handlers:
        h.setFormatter(formatter)


def logger_show(log_str, logger=None, level='info',
                err_exc_info=True, flush=False, show_pos=False,
                **kwargs):
    """显示|记录日志信息

    Parameters
    ----------
    log_str : str
        日志内容字符串
    logger : logging.Logger, None, nan, False
        - 若为False，则不显示|记录日志信息
        - 若为None或nan，则用print打印log_str
        - 若为logging.Logger对象，则根据level设置进行日志显示|记录
    level : str
        支持'info', 'warn', 'error'三个日志级别
    err_exec_info : bool
        显示错误信息时是否写入错误信息
        注：若log_str中已经包含了错误信息，可将其设置为False以避免重复记录错误日志
    flush : bool
        是否滚动显示，只有logger为None时才生效
    show_pos : bool
        是否显示log语句出现的位置
        
    Examples
    --------
    >>> from dramkit.logtools import simple_logger
    >>> logger = simple_logger('./_test/_test_logger_show.log')
    >>> logger_show('print', level='info')
    >>> logger_show('print', level='info', show_pos=True)
    >>> logger_show('info', logger, level='info')
    >>> logger_show('info', logger, level='info', show_pos=True)
    >>> logger_show('warn', logger, level='warn')
    >>> logger_show('warn', logger, level='warn', show_pos=True)
    >>> a = '1'*100
    >>> logger_show(a, logger, level='warn', show_pos=True)
    >>> logger_show('error', logger, level='err')
    >>> logger_show('error', logger, level='err', show_pos=True)
    >>> try:
    ...     raise ValueError('value error')
    ... except:
    ...     logger_show('show value error', logger, level='err')
    ...     logger_show('show value error', logger, level='err', show_pos=True)
    >>> logger_show('error1', logger, level='err1', show_pos=True)
    >>> import time
    >>> for k in range(100):
    ...     logger_show('{} / 100, ...'.format(k), flush=True)
    ...     #logger_show('{} / 100, ...'.format(k), logger, flush=True)
    ...     time.sleep(0.01)


    .. todo::
        - 添加更多level和设置
    """
    if isna(logger):
        if show_pos:
            fname, lineno, line = __get_caller_pos_info(3)
        if not flush:
            if show_pos:                
                print('DrmKtPrint at {}, line: {}:'.format(fname, lineno))
                print('  ' + line)
            print(log_str)
            print('    [time: {}]'.format(
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
        else:
            if show_pos:                
                print('DrmKtPrint at {}, line: {}:'.format(fname, lineno))
                print('  ' + line)
            print_str = str(log_str) + ' - [time: {}]'.format(
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
            print('\r', print_str, end='', flush=True)
    elif logger is False:
        return
    elif isinstance(logger, logging.Logger):
        if show_pos:
            __set_pos_fmt(logger)
        try:
            if level == 'info':
                logger.info(log_str, **kwargs)
            elif level in ['warn', 'warning']:
                logger.warning(log_str, **kwargs)
            elif level in ['error', 'err']:
                logger.error(log_str, exc_info=err_exc_info, **kwargs)
            else:
                raise ValueError('未识别的日志级别设置！')
            if show_pos:
                __reset_fmt(logger)
        except:
            if show_pos:
                __reset_fmt(logger)
            raise
    else:
        raise ValueError('未识别的logger！')


def close_log_file(logger):
    """关闭日志记录器logger中的文件流，返回logger"""
    if isna(logger) or logger is False:
        return logger
    for h in logger.handlers:
        if isinstance(h, logging.FileHandler):
            h.close()
    return logger


def remove_handlers(logger):
    """关闭并移除logger中已存在的handlers，返回logger

    .. note::
        貌似必须先把FileHandler close并remove之后，再remove其它handler
        才能完全remove所有handlers，原因待查（可能由于FileHandler
        是StreamHandler的子类的缘故？）
    """
    # 逐个移除
    for h in logger.handlers:
        if isinstance(h, logging.FileHandler):
            h.close()
            logger.removeHandler(h)
    for h in logger.handlers:
        logger.removeHandler(h)
    # 直接清空
    logger.handlers = []
    return logger


def _get_level(level=None):
    """获取显示级别"""
    if level in [None, 'debug', 'DEBUG', logging.DEBUG]:
        return logging.DEBUG
    elif level in ['info', 'INFO', logging.INFO]:
        return logging.INFO
    elif level in ['warning', 'WARNING', 'warn', 'WARN', logging.WARNING]:
        return logging.WARNING
    elif level in ['error', 'ERROR', 'err', 'ERR', logging.ERROR]:
        return logging.ERROR
    elif level in ['critical', 'CRITICAL', logging.CRITICAL]:
        return logging.CRITICAL
    else:
        raise ValueError('level参数设置有误，请检查！')


def set_level(logger, level=None):
    """设置日志显示基本"""
    logger.setLevel(_get_level(level))
    return logger


def _pre_get_logger(fpath, screen_show, logname, level):
    if fpath is None and not screen_show:
        raise ValueError('`fpath`和`screen_show`必须至少有一个为真！')
    # 准备日志记录器logger
    if logname is None:
        logger = logging.getLogger(__name__)
    else:
        logger = logging.getLogger(logname)
    # 显示级别
    logger = set_level(logger, level=level)
    # 预先删除logger中已存在的handlers
    logger = remove_handlers(logger)
    return logger
        
        
def make_path_dir(fpath):
    """若fpath所指文件夹路径不存在，则新建之"""
    if isna(fpath):
        return
    dir_path = os.path.dirname(fpath)
    if not os.path.exists(dir_path) and len(dir_path) > 0:
        os.makedirs(dir_path)
