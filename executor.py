from bingdog.Task import TaskExecutionException
from bingdog.TaskHandler import ConfiguredTaskUtil
from bingdog.ApplicationConfig import Configurator

class TaskExecutor():
        
    def execute(self,taskId):
        taskUtil = ConfiguredTaskUtil(Configurator.configuration['flow_conf_file_path'])
        task = taskUtil.getTask(taskId)
        if (task):
            self.__execute(task)
        else:
            raise TaskExecutionException("None Root Task")
    def __execute(self, task):
        if (task):
            try:
                task.run()
                while task.hasNextChild():
                    self.__execute(task.getNextChild())
                nextTask = task.getNextTask()
                if (nextTask):
                    self.__execute(nextTask)
            except TaskExecutionException as e:
                print(e)
