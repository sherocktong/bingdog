from bingproxy.proxy import InvocationHandler
from bingproxy.util import implement
from bingdog.appconfig import Configurator
from bingdog.taskutil import ConfiguredTaskUtil
from bingdog.logger import Logger

@implement(InvocationHandler)
class MappedInvocationHandler(object):
    def __init__(self):
        self._taskMap = {}
        self._taskObjMap = {}
        
    def _fetchTaskMap(self):
        if len(self._taskMap) == 0:
            self._taskMap = Configurator.configuration['taskMap']

    def _getTaskHandler(self, proxy, nestedObj, *args, **kwargs):
        if self._taskObjMap.get(proxy) is None:
            handlerClass = self._taskMap.get(nestedObj.__module__ + "." + nestedObj.__class__.__name__)
            if handlerClass is None:
                return None
            else:
                self._taskObjMap[proxy] = handlerClass(nestedObj, *args, **kwargs)
        return self._taskObjMap[proxy]
    
    def invoke(self, proxy, func, nestedObj, *args, **kwargs):
        self._fetchTaskMap()
        taskHandler = self._getTaskHandler(proxy, nestedObj, *args, **kwargs)
        if (taskHandler):
            return getattr(taskHandler, func.__name__)(*args, **kwargs)
        else:
            return func(*args, **kwargs)

@implement(InvocationHandler)
class FlowedInvocationHandler(object):
    def __init__(self):
        super().__init__()
        self.__configuredUtil = ConfiguredTaskUtil(Configurator.getConfigurator().flowDiagramPath)
        self._taskObjMap = {}
        
    def invoke(self, proxy, func, nestedObj, *args, **kwargs):
        taskHandler = self._getTaskHandler(proxy, nestedObj, *args, **kwargs)
        if (taskHandler):
            return getattr(taskHandler, func.__name__)(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    def asynchronized(self):
        return self.__configuredUtil.getSubTaskAsynchronized()

    def _getTaskHandler(self, proxy, nestedObj, *args, **kwargs):
        if self._taskObjMap.get(proxy) is None:
            handlerClass = self.__configuredUtil.getTaskHandlerClass(nestedObj.taskId)
            if handlerClass is None:
                return None
            else:
                self._taskObjMap[proxy] = handlerClass(nestedObj, self.__configuredUtil, *args, **kwargs)
        return self._taskObjMap[proxy]