import os
import logging
from logging import Handler, FileHandler, StreamHandler
import time
import inspect
import threading
import sys


class Singleton(object):
    # 线程锁
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(Singleton, "_instance"):
            with Singleton._instance_lock:
                if not hasattr(Singleton, "_instance"):
                    Singleton._instance = object.__new__(cls)
        return Singleton._instance


class LogMaker(Singleton):
    # 日志级别关系映射
    level_relations = {
        'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 'WARNING': logging.WARNING,
        'ERROR': logging.ERROR, 'CRITICAL': logging.CRITICAL
    }

    # traceback输出限制
    traceback_limit = None

    def __init__(self):
        pass

    @classmethod
    def set_logger(self, filename=None, level='INFO', log_dir='log',
                   format='%(asctime)s - 【%(levelname)s】: %(message)s'):
        self.logger = logging.getLogger(filename)  # 获得日志对象
        self.filename = self.get_filename(filename)  # 获得日志文件名

        self.directory = log_dir  # 设置日志所在目录

        self.format_str = self.format(format)  # 设置日志格式，只设置%(asctime)s/%(levelname)s/%(message)s
        self.set_level(level)  # 设定日志级别
        self.stream_handler = logging.StreamHandler()  # 日志控制台handler
        self.file_handler = PathFileHandler(path=self.directory, filename=self.filename, mode='a')  # 日志文件handler
        self.__add_handler(self.stream_handler)
        self.__add_handler(self.file_handler)

    @classmethod
    def __get_call_info(self):
        '''
        获取log信息所在的具体位置(所在文件、函数、行号)，作为message的前缀信息
        :return: 具体位置信息( XXX.py in function <funcXXX> 【line:XXX】)
        '''

        log_time = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))
        stack = inspect.stack()

        # 栈中的各项参数
        frame = stack[-2][0]
        filename = stack[-2][1]  # 获取文件名
        filename = os.path.basename(filename)
        lineno = stack[-2][2]  # 获取所在行号
        function = stack[-2][3]  # 获取函数名称
        code_context = stack[-2][4]
        index = stack[-2][5]
        str = '{} in function <{}> 【line:{}】: '.format(filename, function, lineno)
        # return filename, function,lineno
        return str

    @classmethod
    def get_filename(self, filename):
        '''
        获取日志文件名
        :param filename:指定文件名，filename为None时（默认），以时间（年_月_日_时_分_秒）为日志文件名。
        :return: 文件名.log（默认为'year_month_day_HOUR_MINUTE_SECOND.log'）
        '''
        if filename is not None and filename.split('.')[-1] == 'log':
            return filename
        elif filename is not None and filename.split('.')[-1] != 'log':
            filename = filename + '.log'
            return filename
        else:
            filename = '{}.log'.format(time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time())))
            return filename

    @classmethod
    def format(self, format):
        '''
        设置日志格式。
        :param format:格式信息
        :return:
        '''
        format = '-' * 100 + '\n' + format
        return logging.Formatter(format)

    @classmethod
    def __add_handler(self, handler):
        '''
        添加handler。
        :param handler:
        :return:
        '''
        handler.setFormatter(self.format_str)
        self.logger.addHandler(handler)

    @classmethod
    def set_level(self, level):
        '''
        设置日志级别，只能从self.level_relations中的debug/info/warning/error/critical中选择。
        :param level:
        :return:
        '''
        self.logger.setLevel(self.level_relations.get(str.upper(level)))  # 设置日志级别

    @classmethod
    def debug(self, *args):
        ''' log.debug '''
        message = ""
        for arg in args:
            message += str(arg) + " "
        message = self.__get_call_info() + ' {message}'.format(message=message)
        self.logger.debug(message)

    @classmethod
    def info(self, *args):
        ''' log.info '''
        message = ""
        for arg in args:
            message += str(arg) + " "
        message = self.__get_call_info() + ' {message}'.format(message=message)
        self.logger.info(message)

    @classmethod
    def warning(self, *args):
        ''' log.warning '''
        message = ""
        for arg in args:
            message += str(arg) + " "
        message = self.__get_call_info() + ' {message}'.format(message=message)
        self.logger.warning(message)

    @classmethod
    def error(self, *args):
        ''' log.error '''
        message = ""
        for arg in args:
            message += str(arg) + " "
        message = self.__get_call_info() + ' {message}'.format(message=message)
        self.logger.error(message)

    @classmethod
    def critical(self, *args):
        ''' log.critical '''
        message = ""
        for arg in args:
            message += str(arg) + " "
        message = self.__get_call_info() + ' {message}'.format(message=message)
        self.logger.critical(message)

    @classmethod
    def exception(self, *args):
        ''' log.exception '''
        message = ""
        for arg in args:
            message += str(arg) + " "
        message = self.__get_call_info() + ' {message}'.format(message=message)
        self.logger.error(message)

    @classmethod
    def excepthook(self, type, value, traceback):
        '''用于隐藏控制台的traceback打印'''
        pass

    @classmethod
    def check_error(self, condition, message="", level='INFO'):
        '''

        判断错误条件，并确定错误等级和信息
        :param condition:判断错误条件
        :param level:错误等级
        :param message: 记录信息
        :return:
        '''
        if not condition:
            self.func = getattr(LogMaker, str.lower(level))
            self.func(message)
            sys.excepthook = self.excepthook  # 隐藏控制台的traceback
            raise ValueError(message)


class PathFileHandler(FileHandler):
    '''
    对logging.FileHandler进行了继承，log日志文件的存储为【模块所在目录/log/xxxx.log】
    '''

    def __init__(self, path, filename, mode='a', encoding='utf-8', delay=False):

        filename = os.fspath(filename)
        if not os.path.exists(path):
            os.mkdir(path)
        self.baseFilename = os.path.join(path, filename)
        self.mode = mode
        self.encoding = encoding
        self.delay = delay
        if delay:
            Handler.__init__(self)
            self.stream = None
        else:
            StreamHandler.__init__(self, self._open())

    def save_path(self, path, filename):
        self.baseFilename = os.path.join(path, filename)

