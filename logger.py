import logging
from bingproxy.util import equalsIgnoreCase, checkIfSubClass, trace
from bingdog.appconfig import Configurator

class Logger(object):
    __logger = None

    def __init__(self):
        loggingLevel = None
        configurator = Configurator.getConfigurator()
        if equalsIgnoreCase("info", configurator.getLoggingLevel()):
            loggingLevel = logging.INFO
        elif equalsIgnoreCase("debug", configurator.getLoggingLevel()):
            loggingLevel = logging.DEBUG
        elif equalsIgnoreCase("warning", configurator.getLoggingLevel()):
            loggingLevel = logging.WARNING
        elif equalsIgnoreCase("error", configurator.getLoggingLevel()):
            loggingLevel = logging.ERROR
        elif equalsIgnoreCase("critical", configurator.getLoggingLevel()):
            loggingLevel = logging.CRITICAL
        filePath = configurator.getLoggingFilePath()
        if filePath:
            logging.basicConfig(level=loggingLevel, filename=filePath, format=configurator.getLoggingFormat())
        else:
            logging.basicConfig(level=loggingLevel, format=configurator.getLoggingFormat())
        
    def info(self, message, *args, **kwargs):
        logging.info(message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        logging.warning(message, *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        logging.error(message, *args, **kwargs)
        
    def debug(self, message, *args, **kwargs):
        logging.debug(message, *args, **kwargs)
    
    def exception(self, message, *args, **kwargs):
        logging.exception(message, *args, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        logging.critical(message, *args, **kwargs)
    
    def getLogger(loggerClass, *args, **kargs):
        checkIfSubClass(loggerClass, Logger)
        if Logger.__logger is None:
            Logger.__logger = loggerClass(*args, **kargs)
        return Logger.__logger
        
    def getLoggerDefault():
        return Logger.getLogger(Logger)