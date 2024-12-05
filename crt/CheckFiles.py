import os

from error.Error import exitError

def checkFiles(caCrt, sdkCrt, sdkKey):
    if not os.path.exists(caCrt):
        exitError("Can not load file, {}".format(caCrt))
    
    if not os.path.exists(sdkCrt):
        exitError("Can not load file, {}".format(sdkCrt))
    
    if not os.path.exists(sdkKey):
        exitError("Can not load file, {}".format(sdkKey))
