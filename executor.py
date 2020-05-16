from bingdog.task import TaskExecutionException
from bingdog.appconfig import Configurator, ConfiguredTaskUtil

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
                print("task started: -------" + task.taskId)
                task.run()
                print("task finished: ------" + task.taskId)
                while task.hasNextChild():
                    childTask = task.getNextChild()
                    self.__execute(childTask)
                nextTask = task.getNextTask()
                if (nextTask):
                    self.__execute(nextTask)
            except TaskExecutionException as e:
                print(e)
