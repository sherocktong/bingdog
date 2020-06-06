import yaml
from bingproxy.util import ifNone, NullPointerException, checkIfSubClass

class Configurator(object):
    __configurator = None
    
    def __init__(self, confPath = "bingdog.conf"):
        self._config = None
        self.__flowDiagramPath = None
        with open(confPath, "r") as f:
            self._config = yaml.load(f.read())
    
    def initialize(confClass, *args, **kwargs):
        checkIfSubClass(confClass, Configurator)
        if Configurator.__configurator is None:
            Configurator.__configurator = confClass(*args, **kwargs)
    
    def getConfigurator():
        return ifNone(Configurator.__configurator)
    
    @property
    def flowDiagramPath(self):
        if self.__flowDiagramPath is None:
            application = self._config.get("application")
            task = ifNone(application).get("task")
            self.__flowDiagramPath = ifNone(task).get("flow_file_path")
        return self.__flowDiagramPath
        
    @flowDiagramPath.setter    
    def flowDiagramPath(self, path):
        self.__flowDiagramPath = path
    
    def getThreadingSize(self):
        try:
            application = self._config.get("application")
            task = ifNone(application).get("task")
            threadingSize = ifNone(task).get("working_threads")
            return ifNone(threadingSize)
        except NullPointerException as e:
            return 1
    
    def getLoggingLevel(self):
        try:
            application = self._config.get("application")
            logger = ifNone(application).get("logger")
            return ifNone(logger).get("level")
        except NullPointerException as e:
            return "info"
    
    def getLoggingFormat(self):
        try:
            application = self._config.get("application")
            logger = ifNone(application).get("logger")
            return ifNone(logger).get("format")
        except NullPointerException as e:
            return "%(levelname)s:%(asctime)s:%(message)s"
            
    def getLoggingFilePath(self):
        try:
            application = self._config.get("application")
            logger = ifNone(application).get("logger")
            return ifNone(logger).get("log_file_path")
        except NullPointerException as e:
            return "bingdog.log"
    