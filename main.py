from sslnet.Client import SSLClient
from crt.Config import CrtConfig
from error.Error import exitError

import sys
import os

func = sys.argv[1]
params = []
length = len(sys.argv)
curPath = os.getcwd()

for i in range(2, length) :
    try :
        params.append(int(sys.argv[i]))
    except Exception as e:
        params.append(sys.argv[i])
if len(params) > 0:
    if params[len(params)-1] == "true":
        params[len(params)-1] = True
    elif params[len(params)-1] == "false":
        params[len(params)-1] = False

config = CrtConfig()
conf = config.getConfig(sys.argv[0])

if "ip" not in conf:
    exitError("ip is not configured.")
    
if "port" not in conf:
    exitError("port is not configured.")
    
if "sdk.crt" not in conf:
    exitError("sdk.crt is not configured.")
    
if "sdk.key" not in conf:
    exitError("sdk.key is not configured.")
    
if "ca.crt" not in conf:
    exitError("ca.crt is not configured.")
    
if "privateKey" not in conf:
    exitError("privateKey is not configured.")
    
if "groupId" not in conf:
    exitError("groupId is not configured.")

client = SSLClient(conf["ip"],conf["port"],conf["sdk.crt"],conf["sdk.key"],conf["ca.crt"],conf["privateKey"],curPath, conf["groupId"])
client.connect()
client.doFunc(func,params)
