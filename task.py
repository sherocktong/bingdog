from abc import abstractmethod
from bingdog.util import ExtProcessShellUtil, ifNone, NullPointerException
from bingproxy.proxy import ProxyDecorator
from bingdog.taskproxy import FlowedInvocationHandler
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
        
    def hasNextChild(self):
        return False
    
    def getNextChild(self):
        return None
        
    def _processStatement(self,statement):
        if (statement):
            for key in self.params:
                statement = statement.replace("$" + str(key), str(self.params[key]))
            return statement
        else:
            return None

@ProxyDecorator(FlowedInvocationHandler)
class ShellExecutionTask(Task):
    def __init__(self, taskId):
        super().__init__(taskId)
        self.statement = None
        self._extUtil = ExtProcessShellUtil()
    
    def run(self):
        try:
            self._extUtil.execute(self._processStatement(ifNone(self.statement)))
        except NullPointerException as e:
            raise TaskExecutionException("None statement")

class TaskExecutionException(Exception):
    def __init__(self, message, exception = None):
        super().__init__(message + " has thrown an execution exception.")
        self.__nestedException = exception
