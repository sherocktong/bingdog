import json
from bingproxy.util import ifNone, NullPointerException, equalsIgnoreCase, trace
from bingdog.taskhandler import ConfiguredTaskHandler
from bingdog.logger import Logger
import sys

class ConfiguredTaskUtil(object):
    _configJson = None
    def __init__(self, filePath):
        if ConfiguredTaskUtil._configJson is None:
            with open(filePath, "r") as conf:
                ConfiguredTaskUtil._configJson = json.loads(conf.read())
                classPath = ConfiguredTaskUtil._configJson.get("class_path")
                if (classPath) :
                    for i in range(len(classPath.split(","))):
                        if (classPath.split(",")[i]):
                            sys.path.append(classPath.split(",")[i])
            
    def __getModuleClassName(self, fullName):
        if len(fullName.split("|")) < 2:
            raise Task.TaskExecutionException("Invalid Class Name")
        else:
            objModule = fullName.split("|")[0]
            objName = fullName.split("|")[1]
        return objModule, objName
    
    def _getParameters(self, taskId):
        return self._getTaskProperty(taskId, "parameters")
    
    def _getClassByName(self, fullName):
        objModule, objName = self.__getModuleClassName(fullName)
        tokens = objName.split(".")
        module = __import__(objModule)
        for token in tokens:
            module = getattr(module, token)
        return module
    
    def _getTaskHandlerName(self, taskId):
        try:
            subTaskJson = ifNone(self._getSubTasksJson(taskId))
            return ifNone(subTaskJson.get('handler'))
        except NullPointerException as e:
            return None

    def getParameters(self, taskId):
        return self._getParameters(taskId)

    def getTask(self, taskId):
        task = None
        try:
            className = self._getTaskClassName(taskId)
            taskClass = self._getClassByName(ifNone(className))
            task = ifNone(taskClass)().newInstance(taskId)
            keys = self._getKeys()
            for key in keys:
                value = self._getTaskProperty(taskId, key)
                if value:
                    task.params["__" + key + "__"] = value
        except Exception as e:
            Logger.getLoggerDefault().exception("Task ID: " + taskId + ". Incorrect Class Name")
            raise TaskExecutionException("Task ID: " + taskId + ". Incorrect Class Name", e)
        finally:
            return task

    def _getKeys(self):
        return ["statement", "source_file", "dist_file", "content", "bean", "write_mode", "text", "encoding", "sheet_index", "sub_task_list", "next_task", "class_name", "mapping", "data_object", "sheet_name", "container"]

    def getNextTaskId(self, taskId):
        return self._getTaskProperty(taskId, 'next_task')
    
    def getSubTasksJsonList(self, taskId):
        try:
            return ifNone(self._getSubTasksJson(taskId)).get('list')
        except NullPointerException as e:
            return None
    
    def getSubUnitTaskId(self, taskId):
        try:
            return ifNone(self._getSubTasksJson(taskId)).get("unit_task")
        except NullPointerException as e:
            return None
    
    def getSubUnitParamKey(self, taskId):
        try:
            return ifNone(self._getSubTasksJson(taskId)).get("unit_param_key")
        except NullPointerException as e:
            return None

    def _getTaskProperty(self, taskId, key):
        return ifNone(self._getTaskJson(taskId)).get(key)

    def getTaskHandlerClass(self, taskId):
        try:
            className = self._getTaskHandlerName(taskId)
            if className:
                return self._getClassByName(className)
            else:
                return ConfiguredTaskHandler
        except Exception as e:
            Logger.getLoggerDefault().exception("Task ID: " + taskId + ". Incorrect Task Handler Class Name")
            raise e

    def _getTaskClassName(self, taskId):
        return self._getTaskProperty(taskId, "class_name")

    def _getTaskJson(self, taskId):
        return ifNone(ConfiguredTaskUtil._configJson).get(taskId)
    
    def getThreadingSize(self, taskId):
        try:
            subTaskJson = self._getSubTasksJson(taskId)
            return int(ifNone(ifNone(subTaskJson).get("threading_size")))
        except NullPointerException as e:
            return 1
    
    def _getSubTasksJson(self, taskId):
        return self._getTaskProperty(taskId, "sub_task_list")
        
    def getSubTaskFieldMapping(self, taskId):
        return self._getTaskProperty(taskId, "mapping")