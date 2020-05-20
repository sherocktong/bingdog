import logging
from bingproxy.util import equalsIgnoreCase, checkIfSubClass
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
        logging.basicConfig(level=loggingLevel, filename=configurator.getLoggingFilePath(), format=configurator.getLoggingFormat())
        
    def info(self, message):
        logging.info(message)
    
    def warning(self, message):
        logging.warning(message)
    
    def error(self, message):
        logging.error(message)
    
    def exception(self, message):
        logging.exception(message)
    
    def getLogger(loggerClass, *args, **kargs):
        checkIfSubClass(loggerClass, Logger)
        if Logger.__logger is None:
            Logger.__logger = loggerClass(*args, **kargs)
        return Logger.__logger
        
    def getLoggerDefault():
        return Logger.getLogger(Logger)