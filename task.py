from abc import abstractmethod
from bingproxy.util import ifNone, NullPointerException, equalsIgnoreCase
from bingdog.extutil import ExtProcessShellUtil
from bingproxy.proxy import ProxyDecorator
from bingdog.taskproxy import FlowedInvocationHandler
from bingdog.logger import Logger

class Task(object):
    
    def __init__(self, taskId):
        self.params = dict()
        self._taskId = taskId
    
    @property
    def taskId(self):
        return self._taskId
    
    @abstractmethod
    def run(self):
        pass

    def getNextTask(self):
        return None
        
    def getThreadingSize(self):
        return 0
        
    def hasNextChild(self):
        return False
    
    def getNextChild(self):
        return None
        
    def _processStatement(self,statement, params=None):
        if params is None:
            params = self.params
        if (statement):
            for key in params:
                statement = statement.replace("$" + str(key), str(params[key]))
            return statement
        else:
            return None

    def _processDoubleStatement(self, statement):
        if self.params.get("__bean__") is not None:
            statement = self._processStatement(statement, self.params[self.params["__bean__"]])
        statement = self._processStatement(statement)
        return statement
        
@ProxyDecorator(FlowedInvocationHandler)
class BlankTask(Task):
    pass

@ProxyDecorator(FlowedInvocationHandler)
class ShellExecutionTask(Task):
    def __init__(self, taskId):
        super().__init__(taskId)
        self._extUtil = ExtProcessShellUtil()
    
    def run(self):
        try:
            self._extUtil.execute(self._processDoubleStatement(ifNone(self.params.get("__statement__"))))
        except Exception as e:
            statement = self.params.get("__statement__")
            if statement is not None:
                statement = "Executing " + statement
            else:
                statement = "None statement"
            Logger.getLoggerDefault().exception(statement)
            raise TaskExecutionException(statement)

@ProxyDecorator(FlowedInvocationHandler)
class TaskExecutionException(Exception):
    def __init__(self, message, exception = None):
        super().__init__(message + " has thrown an execution exception.")
        self.__nestedException = exception

class FileTask(Task):
    def _getEncoding(self):
        charset = self.params.get("__encoding__")
        if charset is None:
            return "utf-8"
        else:
            return charset

    def _getWriteMode(self):
        mode = self.params.get("__write_mode__")
        if mode is None:
            return "a"
        else:
            return mode

@ProxyDecorator(FlowedInvocationHandler)
class FileCopyTask(FileTask):
    def run(self):
        with open(self._processDoubleStatement(self.params["__source_file__"]), "r") as f:
            with open(self._processDoubleStatement(self.params["__dist_file__"]), self._getWriteMode(), encoding = self._getEncoding()) as d:
                for line in f:
                    d.write(self._processDoubleStatement(line))

@ProxyDecorator(FlowedInvocationHandler)
class FileReaderTask(FileTask):
    def run(self):
        with open(self._processDoubleStatement(self.params["__source_file__"]), "r") as f:
            self.params[self.params["__content__"]] = self._processDoubleStatement(f.read())

@ProxyDecorator(FlowedInvocationHandler)
class FileWriterTask(FileTask):
    def run(self):
        writeMode = self._getWriteMode()
        if not writeMode.startswith("a") and not writeMode.startswith("w"):
            raise TaskExecutionException("Invalid writting mode")
        with open(self._processDoubleStatement(self.params["__dist_file__"]), writeMode, encoding = self._getEncoding()) as f:
            f.write(self._processDoubleStatement(self.params[self.params["__content__"]]))

@ProxyDecorator(FlowedInvocationHandler)
class ContentReplacementTask(Task):
    def run(self):
        self.params[self.params["__content__"]] = self._processDoubleStatement(self.params["__text__"])
