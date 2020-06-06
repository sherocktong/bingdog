from bingproxy.util import ifNone, checkIsInstance, checkIfSubClass, trace
from bingdog.logger import Logger
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from bingdog.appconfig import Configurator

class ThreadingPool(object):
    def __init__(self, threadingSize):
        self.__threadingSize = 1
        if threadingSize is not None and type(threadingSize) == 'int' and threadingSize > 0:
            self.__threadingSize = threadingSize
        self.__queue = dict()
        self.__todoList = dict()
        self.__executor = ThreadPoolExecutor(self.__threadingSize)

    __pool = None
    def initialize(poolClass):
        if ThreadingPool.__pool is None:
            checkIfSubClass(poolClass, ThreadingPool)
            ThreadingPool.__pool = poolClass(Configurator.getConfigurator().getThreadingSize())
    
    def getThreadingPool():
        ThreadingPool.initialize(ThreadingPool)
        return ifNone(ThreadingPool.__pool)
    
    def addTask(self, prevTasks, threadTask):
        checkIsInstance(threadTask, ThreadTask)
        if self.__todoList.get(threadTask) is None:
            self.__todoList[threadTask] = dict()
            self.__todoList[threadTask]["prev_set"] = set()
            self.__todoList[threadTask]["next_set"] = set()
        self.setPrev(prevTasks, threadTask)
        self.push(threadTask)
    
    def setPrev(self, prevTasks, threadTask):
        checkIsInstance(threadTask, ThreadTask)
        if self.exists(threadTask):
            if (prevTasks) and len(prevTasks) > 0:
                for prevTask in prevTasks:
                    checkIsInstance(prevTask, ThreadTask)
                    if self.exists(prevTask):
                        self.__todoList[prevTask]["next_set"].add(threadTask)
                        self.__todoList[threadTask]["prev_set"].add(prevTask)
    
    def push(self, threadTask):
        for prevTask in self.__todoList[threadTask]["prev_set"]:
            if self.exists(prevTask):
                return
        future = self.__executor.submit(threadTask.run)
        future.add_done_callback(threadTask.callback)
    
    def exists(self, threadTask):
        return threadTask is not None and self.__todoList.get(threadTask) is not None
    
    def remove(self, threadTask):
        taskDict = self.__todoList.pop(threadTask)
        for nextTask in taskDict["next_set"]:
            self.addTask(None, nextTask)
        
class ThreadTask(object):
    @abstractmethod
    def run(self):
        pass