from bingdog.task import TaskExecutionException
from bingdog.appconfig import Configurator
from bingdog.taskutil import ConfiguredTaskUtil
from bingdog.logger import Logger

class TaskExecutor():
        
    def execute(self,taskId):
        try:
            taskUtil = ConfiguredTaskUtil(Configurator.getConfigurator().flowDiagramPath)
            task = taskUtil.getTask(taskId)
            if (task):
                self.__execute(task)
            else:
                raise TaskExecutionException("None Root Task")
        except TaskExecutionException as e:
            Logger.getLogger(Logger).exception("Root TaskExecutionException has Thrown.")
        
    def __execute(self, task):
        if (task):
            try:
                task.run()
                while task.hasNextChild():
                    childTask = task.getNextChild()
                    self.__execute(childTask)
                nextTask = task.getNextTask()
                if (nextTask):
                    self.__execute(nextTask)
            except TaskExecutionException as e:
                Logger.getLogger(Logger).exception("TaskExecutionException has Thrown.")
