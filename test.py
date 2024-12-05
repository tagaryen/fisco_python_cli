from sslnet.Client import SSLClient
from crt.Config import CrtConfig
from pack.FrameData import FrameData
from error.Error import exitError

import random
import json
import pprint
import sys



config = CrtConfig()
conf = config.getConfig(sys.argv[0])
client = SSLClient(conf["ip"],conf["port"],conf["sdk.crt"],conf["sdk.key"],conf["ca.crt"],conf["privateKey"],"E:/myProject/pythonProject/cli0.2.0/")
client.connect()


res = client.sendAndGetRecv(bytes(packData))

transRes = json.loads(str(res[42:],"utf-8"))

print(transRes)



