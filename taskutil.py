import json
from bingdog.util import ifNone, NullPointerException
from bingdog.taskhandler import ConfiguredTaskHandler
import sys

class ConfiguredTaskUtil(object):
    def __init__(self, filePath):
        with open(filePath, "r") as conf:
            self._configJson = json.loads(conf.read())
            classPath = self._configJson.get("class_path")
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

    def getTask(self, taskId):
        task = None
        try:
            className = self._getTaskClassName(taskId)
            taskClass = self._getClassByName(ifNone(className))
            task = ifNone(taskClass)().newInstance(taskId)
            task.statement = self._getStatement(taskId)
        except NullPointerException as e:
            raise TaskExecutionException("Task ID: " + taskId + ". Incorrect Class Name", e)
        finally:
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
            return ifNone(self._getSubTasksJson(taskId)).get("unit_task")
        except NullPointerException as e:
            return None
    
    def getSubListParamKey(self, taskId):
        try:
            return ifNone(self._getSubTasksJson(taskId)).get("list_param_key")
        except NullPointerException as e:
            return None 
    
    def getSubUnitParamKey(self, taskId):
        try:
            return ifNone(self._getSubTasksJson(taskId)).get("unit_param_key")
        except NullPointerException as e:
            return None

    def _getStatement(self, taskId):
        try:
            return ifNone(self._getTaskJson(taskId)).get("statement")
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