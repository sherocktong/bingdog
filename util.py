import subprocess
from abc import abstractmethod
import logging

class ExtExecutionException(Exception):
    
    def __init__(self):
        super().__init__("External execution error.")

class ExtProcessUtil(object):

    @abstractmethod
    def execute(self, statement):
        pass
        
    
class ExtProcessShellUtil(ExtProcessUtil):

    def execute(self, statement):
        self.__print("Executing: " + statement)
        statusCode, responseText = subprocess.getstatusoutput(statement)
        if statusCode == -1:
            raise ExtExecutionException() 
        else:
            self.__print("Response Text: " + responseText)
        return responseText

    def __print(self, text):
        if len(text) <= 500:
            logging.info(text)
            
def ifNone(obj) :
    if obj is None:
        raise NullPointerException()
    else:
        return obj
    
class NullPointerException(Exception):
    pass