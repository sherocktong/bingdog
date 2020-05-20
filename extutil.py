from bingdog.logger import Logger
from bingproxy.util import trace
import subprocess

class ExtProcessShellUtil(object):

    def execute(self, statement):
        self.__print("Executing: " + statement)
        statusCode, responseText = subprocess.getstatusoutput(statement)
        if statusCode != 0:
            raise ExtExecutionException() 
        else:
            self.__print("Response Text: " + responseText)
        return responseText

    def __print(self, text):
        if len(text) <= 500:
            Logger.getLogger(Logger).info(text)
            
class ExtExecutionException(Exception):
    
    def __init__(self):
        super().__init__("External execution error.")