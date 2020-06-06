from bingdog.task import TaskExecutionException
from bingdog.appconfig import Configurator
from bingdog.taskutil import ConfiguredTaskUtil
from bingdog.logger import Logger
from bingproxy.util import implement, trace
from concurrent.futures import ThreadPoolExecutor, ALL_COMPLETED, wait

class TaskExecutor():

    def execute(self,taskId, func = None, callback = None):
        try:
            taskUtil = ConfiguredTaskUtil(Configurator.getConfigurator().flowDiagramPath)
            task = taskUtil.getTask(taskId)
            if (task):
                if func:
                    func(task)
                if callback:
                    callback(task)
                if task.params.get("container_handler__") is None:
                    task.params["container_handler__"] = dict()
                self.__execute(task)
            else:
                raise TaskExecutionException("None Root Task")
        except Exception as e:
            Logger.getLogger(Logger).exception("Root TaskExecutionException has Thrown.")
            raise e

    def __execute(self, task):
        if (task):
            try:
                task.run()
                tSize = task.getThreadingSize()
                if tSize < 2:
                    while task.hasNextChild():
                        childTask = task.getNextChild()
                        self.__execute(childTask)
                else:
                    Logger.getLoggerDefault().debug("Task " + task.taskId + " started multiple threads with size: " + str(tSize))
                    with ThreadPoolExecutor(tSize) as exc:
                        submitList = []
                        while task.hasNextChild():
                            childTask = task.getNextChild()
                            submitList.append(exc.submit(self.__execute, childTask))
                        wait(submitList, return_when=ALL_COMPLETED)
                nextTask = task.getNextTask()
                if (nextTask):
                    self.__execute(nextTask)
            except Exception as e:
                Logger.getLogger(Logger).exception("TaskExecutionException has Thrown.")
            