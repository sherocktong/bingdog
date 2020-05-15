from abc import abstractmethod
import bingdog.Task 
from bingdog.Proxy import InvocationHandler
from bingdog.ApplicationConfig import Configurator
from bingdog.Util import ifNone, NullPointerException
import json

class MappedInvocationHandler(InvocationHandler):
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

class FlowedInvocationHandler(InvocationHandler):
    def __init__(self):
        super().__init__()
        self.__configuredUtil = ConfiguredTaskUtil(Configurator.configuration['flow_conf_file_path'])
        self._taskObjMap = {}
        
    def invoke(self, proxy, func, nestedObj, *args, **kwargs):
        taskHandler = self._getTaskHandler(proxy, nestedObj, *args, **kwargs)
        if (taskHandler):
            return getattr(taskHandler, func.__name__)(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    def _getTaskHandler(self, proxy, nestedObj, *args, **kwargs):
        if self._taskObjMap.get(proxy) is None:
            handlerClass = self.__configuredUtil.getTaskHandlerClass(nestedObj.taskId)
            if handlerClass is None:
                return None
            else:
                self._taskObjMap[proxy] = handlerClass(nestedObj, self.__configuredUtil, *args, **kwargs)
        return self._taskObjMap[proxy]

class ConfiguredTaskUtil(object):
    def __init__(self, filePath):
        with open(filePath, "r") as conf:
            self._configJson = json.loads(conf.read())
            
    def __getModuleClassName(self, fullName):
        if len(fullName.split(".")) < 2:
            raise Task.TaskExecutionException("Invalid Class Name")
        else:
            objName = fullName.split(".")[len(fullName.split(".")) - 1]
            objModule = ""
            for i in range(len(fullName.split(".")) - 1):
                objModule = objModule + fullName.split(".")[i]
        return objModule, objName
    
    def _getClassByName(self, fullName):
        moduleName, className = self.__getModuleClassName(fullName)
        module = __import__(moduleName)
        return getattr(module, className)
    
    def _getTaskHandlerName(self, taskId):
        try:
            subTaskJson = ifNone(self._getSubTasksJson(taskId))
            return ifNone(subTaskJson.get('handler'))
        except NullPointerException as e:
            return None

    def getTask(self, taskId):
        task = None
        try:
            task = ifNone(self._getClassByName(ifNone(self._getTaskClassName(taskId)))).newInstance(taskId)
            task.statement = ifNone(self._getStatement(taskId))
        except NullPointerException as e:
            return task

    def getNextTaskId(self, taskId):
        try:
            return ifNone(self._getTaskJson(taskId)).get('next_task')
        except NullPointerException as e:
            return None
    
    def getSubTasksJsonList(self, taskId):
        try:
            return ifNone(self._getSubTasksJson(taskId)).get('list')
        except NullPointerException as e:
            return None
    
    def getSubUnitTaskId(self, taskId):
        try:
            ifNone(self._getSubTasksJson(taskId)).get("unit_task")
        except NullPointerException as e:
            return None
    
    def getSubListParamKey(self, taskId):
        try:
            ifNone(self._getSubTasksJson(taskId)).get("list_param_key")
        except NullPointerException as e:
            return None 
    
    def getSubUnitParamKey(self, taskId):
        try:
            ifNone(self._getSubTasksJson(taskId)).get("unit_param_key")
        except NullPointerException as e:
            return None

    def _getStatement(self, taskId):
        try:
            return ifNone(ifNone(self._getTaskJson(taskId)).get("statement"))
        except NullPointerException as e:
            return None

    def getTaskHandlerClass(self, taskId):
        try:
            return ifNone(self._getClassByName(ifNone(self._getTaskHandlerName(taskId))))
        except NullPointerException as e:
            return ConfiguredTaskHandler

    def _getTaskClassName(self, taskId):
        try:
            return ifNone(self._getTaskJson(taskId)).get("class_name")
        except NullPointerException as e:
            return None

    def _getTaskJson(self, taskId):
        try:
            return ifNone(self._configJson).get(taskId)
        except NullPointerException as e:
            return None
            
    def _getSubTasksJson(self, taskId):
        try:
            return ifNone(self._getTaskJson(taskId)).get('sub_task_list')
        except NullPointerException as e:
            return None
        
class TaskHandler(object):

    def __init__(self, nestedObj):
        super().__init__()
        self._childIndex = 0
        self._nestedObj = nestedObj
        
    def run(self):
        self._nestedObj.run()
        
    def getNextTask(self):
        task = self._getNextTask()
        if (task):
            task.params.update(self._nestedObj.params)
        return task
        
    def _getNextTask(self):
        return None
        
    def hasNextChild(self):
        if self._childIndex < self._getSubTaskListSize():
            return True
        else:
            return False
    
    def getNextChild(self):
        subTask = self._fetchNextSubTask()
        subTask.params.update(self._nestedObj.params)
        self._childIndex = self._childIndex + 1
        return subTask
    
    def _fetchNextSubTask(self):
        return None
    
    def _getSubTaskListSize(self):
        return 0

class ConfiguredTaskHandler(TaskHandler):
    def __init__(self, nestedObj, configuredUtil):
        super().__init__(nestedObj)
        self._configuredUtil = configuredUtil
    
    def _getNextTask(self):
        try:
            return ifNone(self._configuredUtil.getTask(self._configuredUtil.getNextTaskId(self._nestedObj.taskId)))
        except NullPointerException as e:
            return None
    
    def hasNextChild(self):
        if self._childIndex < self._getSubTaskListSize():
            return True
        else:
            return False
    
    def _fetchNextSubTask(self):
        subTaskClassList = self._configuredUtil.getSubTasksJsonList(self._nestedObj.taskId)
        if (subTaskClassList):
            return self._configuredUtil.getTask(subTaskClassList[self._childIndex])
        else:
            return self._configuredUtil.getTask(self._configuredUtil.getSubUnitTaskId(self._nestedObj.taskId))
    
    def getNextChild(self):
        subTask = self._fetchNextSubTask()
        try:
            self._nestedObj.params[ifNone(self._configuredUtil.getSubUnitParamKey(self._nestedObj.taskId))] = self._nestedObj.params[ifNone(self._configuredUtil.getSubListParamKey(self._nestedObj.taskId))][self._childIndex]
        finally:
            subTask.params.update(self._nestedObj.params)
            self._childIndex = self._childIndex + 1
            return subTask
    
    def _getSubTaskListSize(self):
        try:
            return len(ifNone(self._configuredUtil.getSubTasksJsonList(self._nestedObj.taskId)))
        except NullPointerException as e:
            try:
                return len(self._nestedObj.params[ifNone(self._configuredUtil.getSubListParamKey(self._nestedObj.taskId))])
            except NullPointerException as e:
                return 0
