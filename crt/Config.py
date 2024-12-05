import json
import sys
import os
import platform

CONF_FILE = "conf/config.json"

class CrtConfig:
    def getConfig(self,filePath):
        seprator = ""
        if platform.system() == "Windows" :
            seprator = "\\"
        else:
            seprator = "/"
        entrancePath = os.path.abspath(filePath)
        entrancePathArr = entrancePath.split(seprator)
        root = seprator.join(entrancePathArr[:-1])
        filePath = root+seprator+CONF_FILE
        return json.load(open(filePath))