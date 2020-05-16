from abc import abstractmethod

from bingproxy.proxy import InvocationHandler
from bingdog.util import ifNone, NullPointerException
import json
        
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
            return ifNone(self._configuredUtil.getTask(ifNone(self._configuredUtil.getNextTaskId(self._nestedObj.taskId))))
        except NullPointerException as e:
            return None
    
    def hasNextChild(self):
        if self._childIndex < self._getSubTaskListSize():
            return True
        else:
            return False
    
    def _fetchNextSubTask(self):
        subTaskJsonList = self._configuredUtil.getSubTasksJsonList(self._nestedObj.taskId)
        if (subTaskJsonList):
            return self._configuredUtil.getTask(subTaskJsonList[self._childIndex])
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
            jsonList = self._configuredUtil.getSubTasksJsonList(self._nestedObj.taskId)
            return len(ifNone(jsonList))
        except NullPointerException as e:
            try:
                listKey = self._configuredUtil.getSubListParamKey(self._nestedObj.taskId)
                return len(self._nestedObj.params[ifNone(listKey)])
            except NullPointerException as e:
                return 0
