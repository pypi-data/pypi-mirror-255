#!/usr/bin/python3

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

class LocalLogger:
    def __init__(self, log_file, log_name, loglevel='warning', max_bytes=200000, max_files=10):
        """
        Python Logger: This script was made for logging as fast and simple as possible. Make sure you have write permission for your log file.
        It's reccommended that you use an absolute route for your log file.
        Multiple instances of this logger can be used (With same or different log_name)
        Usage:
        
        from pythonlogger.logger import LocalLogger
        log = LocalLogger(str(Path(__file__).resolve().parent) + '/log.log', 'Some-logger')
        log.debug('mensaje debug')
        log.info('mensaje info')
        log.warning('mensaje warning')
        log.error('mensaje error')
        log.critical('mensaje critical')
        
        By default, it logs from WARNING to CRITICAL messages. If you want to change it, you can call SetLevel('debug') to log every message.
        
        Made by Juan Ignacio De Nicola. Feel free to redistribute or modify it as you wish.
        """
        
        self.__logger = logging.getLogger(log_name)
        fh = RotatingFileHandler(log_file, max_bytes, max_files)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        fh.setFormatter(formatter)
        self.__logger.addHandler(fh)
        self.SetLevel(loglevel)

    
    def SetLevel(self, level):
        if level.lower() == "debug":
            self.__logger.setLevel(logging.DEBUG)
        if level.lower() == "info":
            self.__logger.setLevel(logging.INFO)
        if level.lower() == "warning":
            self.__logger.setLevel(logging.WARNING)
        if level.lower() == "error":
            self.__logger.setLevel(logging.ERROR)
        if level.lower() == "critical":
            self.__logger.setLevel(logging.CRITICAL)

    def debug(self, message):
        self.__logger.debug(message)
    
    def info(self, message):
        self.__logger.info(message)

    def warning(self, message):
        self.__logger.warning(message)

    def error(self, message):
        self.__logger.error(message)

    def critical(self, message):
        self.__logger.critical(message)
