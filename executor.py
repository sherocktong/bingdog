from bingdog.task import TaskExecutionException
from bingdog.appconfig import Configurator, ConfiguredTaskUtil
import logging

class TaskExecutor():
        
    def execute(self,taskId):
        try:
            taskUtil = ConfiguredTaskUtil(Configurator.configuration['flow_conf_file_path'])
            task = taskUtil.getTask(taskId)
            if (task):
                self.__execute(task)
            else:
                raise TaskExecutionException("None Root Task")
        except TaskExecutionException as e:
            logging.exception("Root TaskExecutionException has Thrown.")
        
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
                logging.exception("TaskExecutionException has Thrown.")
