from bingdog.task import TaskExecutionException
from bingdog.appconfig import Configurator
from bingdog.taskutil import ConfiguredTaskUtil
from bingdog.logger import Logger
from bingdog.threading import ThreadingPool, ThreadTask
from bingproxy.util import implement, trace

class TaskExecutor():

    def execute(self,taskId):
        try:
            taskUtil = ConfiguredTaskUtil(Configurator.getConfigurator().flowDiagramPath)
            task = taskUtil.getTask(taskId)
            if (task):
                ThreadingPool.getThreadingPool().addTask(None, FlowThreadTask(task))
            else:
                raise TaskExecutionException("None Root Task")
        except TaskExecutionException as e:
            Logger.getLogger(Logger).exception("Root TaskExecutionException has Thrown.")

@implement(ThreadTask)
class FlowThreadTask(object):
    
    def __init__(self, task):
        self.__task = task
        self.__exception = None

    @property
    def task(self):
        return self.__task
    
    def run(self):
        if (self.__task):
            try:
                Logger.getLoggerDefault().info("Task running: " + self.__task.taskId)
                self.__task.run()
            except TaskExecutionException as e:
                self.__exception = e
                Logger.getLoggerDefault().exception("TaskExecutionException has Thrown.")
    
    def callback(self, future):
        ThreadingPool.getThreadingPool().remove(self)
        if (self.__task) and self.__exception is None:
            nextPrevTasks = []
            prevTask = None
            nextPrevTasks.append(self)
            while self.__task.hasNextChild():
                childTask = FlowThreadTask(self.__task.getNextChild())
                Logger.getLoggerDefault().info("Got child task: " + childTask.task.taskId)
                ThreadingPool.getThreadingPool().addTask([self, prevTask], childTask)
                Logger.getLoggerDefault().info("Added child task: " + childTask.task.taskId)
                if not self.__task.asynchronized():
                    Logger.getLoggerDefault().info("Not Asynchronized: " + self.__task.taskId)
                    prevTask = childTask
                Logger.getLoggerDefault().info("After Asynchronized: " + self.__task.taskId)
                nextPrevTasks.append(childTask)
            Logger.getLoggerDefault().info("After While: " + self.__task.taskId)
            nextTask = FlowThreadTask(self.__task.getNextTask())
            if (nextTask.task):
                Logger.getLoggerDefault().info("Got next task: " + nextTask.task.taskId)
                ThreadingPool.getThreadingPool().addTask(nextPrevTasks, nextTask)
                Logger.getLoggerDefault().info("Added next task: " + nextTask.task.taskId)
            