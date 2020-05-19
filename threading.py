from bingproxy.util import ifNone, checkIfSubClass
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor

class ThreadingPool(object):
    def __init__(self, threadingSize):
        self.__threadingSize = 1
        if threadingSize is not None and type(threadingSize) == 'int' and threadingSize > 0:
            self.__threadingSize = threadingSize
        self.__queue = dict()
        self.__todoList = dict()
        self.__executor = ThreadPoolExecutor(self.__threadingSize)

    __pool = None
    def initialize(poolClass, *args, **kwargs):
        checkIfSubClass(poolClass, ThreadingPool)
        if ThreadingPool.__pool is None:
            ThreadingPool.__pool = poolClass(*args, **kargs)
    
    def getThreadingPool():
        return ifNone(ThreadingPool.__pool)
    
    def addTask(self, prevTasks, threadTask):
        checkIfSubClass(threadTask.__class__, ThreadTask)
        if self.__todoList.get(threadTask) is None:
            self.__todoList[threadTask] = dict()
            self.__todoList[threadTask]["prev_set"] = set()
            self.__todoList[threadTask]["next_set"] = set()
        self.setPrev(prevTasks, threadTask)
        self.push(threadTask)
    
    def setPrev(self, prevTasks, threadTask):
        checkIfSubClass(threadTask.__class__, ThreadTask)
        if self.exists(threadTask):
            if (prevTasks) and len(prevTasks) > 0:
                for prevTask in prevTasks:
                    checkIfSubClass(prevTask.__class__, ThreadTask)
                    if self.exists(prevTask):
                        self.__todoList[prevTask]["next_set"].add(threadTask)
                        self.__todoList[threadTask]["prev_set"].add(prevTask)
    
    def push(self, threadTask):
        for prevTask in self.__todoList[threadTask]["prev_set"]:
            if self.exists(prevTask):
                return
        self.__executor(threadTask.run)
    
    def exists(self, threadTask):
        return threadTask is not None and self.__todoList.get(threadTask) is not None
    
    def remove(self, threadTask):
        return self.__todoList.pop(threadTask)
        
class ThreadTask(object):
    @abstractmethod
    def run(self)
        pass