from abc import abstractmethod

from bingproxy.proxy import InvocationHandler
from bingproxy.util import ifNone, NullPointerException, equalsIgnoreCase, implement, fetchDict, trace
from bingdog.logger import Logger
import json
import xlrd
import csv
     
class TaskHandler(object):

    def __init__(self, nestedObj):
        super().__init__()
        self._childIndex = 0
        self._nestedObj = nestedObj
        
    def run(self):
        Logger.getLoggerDefault().debug("Executing Task: " + self._nestedObj.taskId)
        self._nestedObj.prepare()
        self._nestedObj.run()
    
    def getNextTask(self):
        task = self._getNextTask()
        self._passParams(task)
        return task
        
    def _getNextTask(self):
        return None
        
    def prepare(self):
        return self._nestedObj.prepare()
        
    def hasNextChild(self):
        if self._childIndex < self._getSubTaskListSize():
            return True
        else:
            return False
            
    def getThreadingSize(self):
        return 0
    
    def getNextChild(self):
        subTask = self._fetchNextSubTask()
        self._passParams(subTask)
        self._childIndex = self._childIndex + 1
        return subTask
    
    def _passParams(self, task):
        if (task):
            task.params.update(fetchDict(self._nestedObj.params))
    
    def _fetchNextSubTask(self):
        return None
    
    def _getSubTaskListSize(self):
        return 0

class ConfiguredTaskHandler(TaskHandler):
    def __init__(self, nestedObj, configuredUtil):
        super().__init__(nestedObj)
        self._configuredUtil = configuredUtil
    
    def _getNextTask(self):
        nextTaskId = self._configuredUtil.getNextTaskId(self._nestedObj.taskId)
        if nextTaskId is not None:
            return self._configuredUtil.getTask(nextTaskId)
        else:
            return None
    
    def _fetchNextSubTask(self):
        subTaskJsonList = self._configuredUtil.getSubTasksJsonList(self._nestedObj.taskId)
        return self._configuredUtil.getTask(ifNone(subTaskJsonList)[self._childIndex])
    
    def getThreadingSize(self):
        return self._configuredUtil.getThreadingSize(self._nestedObj.taskId)
    
    def _getSubTaskListSize(self):
        try:
            jsonList = self._configuredUtil.getSubTasksJsonList(self._nestedObj.taskId)
            return len(ifNone(jsonList))
        except NullPointerException as e:
            return 0

class FileWriterTaskHandler(ConfiguredTaskHandler):
    def __init__(self, nestedObj, configuredUtil):
        super().__init__(nestedObj, configuredUtil)
        self._distFile = None
        
    def run(self):
        super().run()
        filePath = self._nestedObj.params.get("__dist_file__")
        if (filePath):
            self._distFile = open(filePath, self._getWriteMode(), encoding=self._getEncoding())
            self._nestedObj.params[filePath] = self._distFile
            
    def _close(self):
        if (self._distFile):
            self._distFile.close()
            self._nestedObj.params.pop(self._nestedObj.params["__dist_file__"])
            
    def _getEncoding(self):
        charset = self._nestedObj.params.get("__encoding__")
        if charset is None:
            return "utf-8"
        else:
            return charset

    def _getWriteMode(self):
        mode = self._nestedObj.params.get("__write_mode__")
        if mode is None:
            return "a"
        else:
            return mode
            
    def hasNextChild(self):
        if self._childIndex < self._getSubTaskListSize():
            return True
        else:
            self._close()
            return False

class DynamicConfiguredTaskHandler(FileWriterTaskHandler):

    def _fetchNextSubTask(self):
        subTask = self._configuredUtil.getTask(self._configuredUtil.getSubUnitTaskId(self._nestedObj.taskId))
        unitKey = self._configuredUtil.getSubUnitParamKey(self._nestedObj.taskId)
        subTask.params[ifNone(unitKey)] = self._getRawRecord()
        return subTask

    def _getRawRecord(self):
        return self._nestedObj.params[ifNone(self._nestedObj.params["__content__"])][self._childIndex]
    
class SpreadSheetTaskHandler(DynamicConfiguredTaskHandler):
    def __init__(self, nestedObj, configuredUtil):
        super().__init__(nestedObj, configuredUtil)
        self._sheet = None
        self._childIndex = 1
        
    def _initTable(self):
        if self._sheet is None:
            try:
                data = xlrd.open_workbook(self._nestedObj.params["__source_file__"])
                index = int(self._nestedObj.params["__index__"])
                if index is None:
                    index = 0
                self._sheet = data.sheet_by_index(index)
            except (FileNotFoundError, xlrd.XLRDError) as e:
                Logger.getLoggerDefault().exception("Empty or Abscent data spreadsheet: " + self._nestedObj.params["__source_file__"])
                raise NullPointerException()
                
    def run(self):
        super().run()
        self._initTable()
        
    def _getSubTaskListSize(self):
        return self._sheet.nrows
    
    def _getRawRecord(self):
        return self._sheet.row_values(self._childIndex)
    
class CsvTaskHandler(DynamicConfiguredTaskHandler):
    def __init__(self, nestedObj, configuredUtil):
        super().__init__(nestedObj, configuredUtil)
        self._file = None
        self._content = None
        self._record = None 
        
    def hasNextChild(self):
        try:
            self._record = next(self._content)
            return True
        except StopIteration as e:
            try:
                self._file.close()
            finally:
                try:
                    self._close()
                finally:
                    return False

    def run(self):
        super().run()
        self._file = open(self._nestedObj.params["__source_file__"], "r")
        self._content = csv.reader(self._file)
        self._record = next(self._content)
    
    def _getSubTaskListSize(self):
        return 0
    
    def _getRawRecord(self):
        return self._record
    
class JsonListTaskHandler(DynamicConfiguredTaskHandler):
    def _getSubTaskListSize(self):
        return len(self._nestedObj.params[self._nestedObj.params["__content__"]])