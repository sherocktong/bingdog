from bingdog.logger import Logger

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
            Logger.getLogger(Logger).infor(text)