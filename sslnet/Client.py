import socket
import ssl
import json
import sys
import os


from crt.CheckFiles import checkFiles
from pathlib import Path
from .Address import check_address
from error.Error import exitError
from pack.FrameData import FrameData

from .Function import (
    parseParams,
    encodeFunction,
    decodeOutputs,
    encodeParams
)

from util.Hex import (
    numToHex
)

from .Transaction import *

def read(curPath,relativeFilePath):
    curPathLen = len(curPath)
    if curPath[curPathLen - 1] != os.sep:
        curPath += os.sep
    
    f = Path(relativeFilePath)
    dstFile = relativeFilePath
    if not f.exists() or not f.is_file():
        if relativeFilePath[0] == '.' and relativeFilePath[1] == os.sep :
            dstFile = curPath + relativeFilePath[1:]
        elif relativeFilePath[0] == os.sep:
            exitError("Can not found {}".format(relativeFilePath))
        else:
            dstFile = curPath + relativeFilePath
    l = len(dstFile)
    if dstFile[l-4:l] != ".sol":
        exitError("Input file must be '.sol'")
    
    dstFile = dstFile[:l-4]+".bin"
    f = Path(dstFile)
    if f.exists() and f.is_file():
        return f.read_bytes()
    exitError("Can not found {}".format(dstFile))



def checkNull(value, name):
    if value == None or value == "":
        exitError("Invalid input paramter, {} is required.".format(name))

def parseAndPrintOutput(res,outputs):
    print("{")
    print("    status:",res["status"])
    print("    transactionHash:",res["transactionHash"])
    print("    blockNumber:",res["blockNumber"])
    print("    outputs:",outputs)
    print("}")
    sys.exit(0)

def parseAndPrintDeploy(res):
    print("{")
    print("    status:",res["status"])
    if "statusMsg" in res:
        print("    statusMsg:",res["statusMsg"])
    print("    transactionHash:",res["transactionHash"])
    print("    blockNumber:",res["blockNumber"])
    print("    contractAddress:",res["contractAddress"])
    print("}")
    sys.exit(0)


class SSLClient:
    ip = ""
    port = 0
    crtPath = ""
    keyPath = ""
    caPath = ""
    curPath = ""
    groupId = 0

    client = None

    def __init__(self,ip,port,crtPath,keyPath,caPath,privateKey,curPath, groupId):
        checkNull(ip,"ip")
        checkNull(port,"port")
        checkNull(crtPath,"crtPath")
        checkNull(keyPath,"keyPath")
        checkNull(caPath,"caPath")
        checkNull(privateKey,"privateKey")
        checkNull(groupId,"groupId")

        checkFiles(caPath, crtPath, keyPath)

        self.ip = ip
        self.port = port
        self.crtPath = crtPath
        self.keyPath = keyPath
        self.caPath = caPath
        self.privateKey = privateKey
        self.curPath = curPath
        self.groupId = groupId
    
    def connect(self):
        try:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            context.check_hostname = False
            context.load_verify_locations(self.caPath)
            context.load_cert_chain(self.crtPath, self.keyPath)
            context.set_ecdh_curve("secp256k1")
            context.verify_mode = ssl.CERT_REQUIRED

            sock = socket.create_connection((self.ip, self.port))
            self.client = context.wrap_socket(sock)
        except Exception as e:
            exitError("Cannot connect to "+self.ip+":"+str(self.port)+", {}".format(e))

    def sendAndGetRecv(self,byteArr:bytes):
        try:
            self.client.send(byteArr)
            recv =  self.client.recv(1024*1024)
            tryTimes = 0
            while tryTimes < 3 and len(recv) == 0:
                recv =  self.client.recv(1024*1024)
            return recv
        except Exception as e:
            exitError("Receving message from "+self.ip+":"+str(self.port)+" error, {}".format(e))

    def jsonRpcPackData(self, func, paramStr):
        return "{\"jsonrpc\":\"2.0\",\"method\":\""+func+"\",\"params\":"+paramStr+",\"id\":1}"

    def doFunc(self, func, params):
        if func == "deploy":
            solFile = params[0]
            binStr = str(read(self.curPath, solFile),'ascii')
            params = params[1:]
            inputTypes,inputValues,outputTypes = parseParams(params)
            data = encodeParams(inputTypes, inputValues)
            
            blockLimit = self.getBlockLimit()
            trans = genTansactionDict(blockLimit,"",binStr+data,str(self.groupId))
            print(trans)

            signedTrans = "0x"+signTransaction(trans, self.privateKey)
            transParams = ('['+str(self.groupId)+',"'+signedTrans+'"]')
            transRpc = self.jsonRpcPackData("sendRawTransaction",transParams)
            transFrame = FrameData(bytes(transRpc, "utf-8"))

            transRcev = self.sendAndGetRecv(transFrame.genFrameData())
            transRes = json.loads(str(transRcev[42:],"utf-8"))
            if "result" not in transRes:
                exitError(transRes["error"])
            txhash = transRes["result"]
            repParams = ('[1,"'+txhash+'"]')
            repRpc = self.jsonRpcPackData("getTransactionReceipt",repParams)
            repFrame = FrameData(bytes(repRpc, "utf-8"))
            recvMsg = self.sendAndGetRecv(repFrame.genFrameData())
            jsonRes = json.loads(str(recvMsg[42:],"utf-8"))
            if "contractAddress" in jsonRes :
                self.client.close()
                parseAndPrintDeploy(jsonRes)
            if "result" in jsonRes:
                if jsonRes["result"] is not None:
                    self.client.close()
                    parseAndPrintDeploy(jsonRes["result"])
                else:
                    recv = self.client.recv(1024*1024)
                    results = {}
                    try:
                        results = json.loads(str(recv[42:],"utf-8"))
                    except Exception as e:
                        rest = self.client.recv(1024*1024)
                        final = []
                        for b in recv:
                            final.append(b)
                        for b in rest:
                            final.append(b)
                        results = json.loads(str(bytes(final[42:]),"utf-8"))
                    self.client.close()
                    parseAndPrintDeploy(results)
            elif "error" in jsonRes:
                self.client.close()
                exitError(jsonRes["error"])
            else:
                self.client.close()
                exitError(jsonRes)
        elif func == "call":
            to = check_address(params[0])
            method = params[1]
            params = params[2:]

            inputTypes,inputValues,outputTypes = parseParams(params)
            data = encodeFunction(method, inputTypes, inputValues)

            blockLimit = self.getBlockLimit()
            trans = genTansactionDict(blockLimit,to,data, str(self.groupId))
            print(trans)
    
            signedTrans = "0x"+signTransaction(trans, self.privateKey)
            transParams = ('['+str(self.groupId)+',"'+signedTrans+'"]')
            transRpc = self.jsonRpcPackData("sendRawTransaction",transParams)
            transFrame = FrameData(bytes(transRpc, "utf-8"))

            transRcev = self.sendAndGetRecv(transFrame.genFrameData())
            transRes = json.loads(str(transRcev[42:],"utf-8"))
            if "result" not in transRes:
                exitError(transRes["error"])

            txhash = transRes["result"]
            repParams = ('[1,"'+txhash+'"]')
            repRpc = self.jsonRpcPackData("getTransactionReceipt",repParams)
            repFrame = FrameData(bytes(repRpc, "utf-8"))
            recvMsg = self.sendAndGetRecv(repFrame.genFrameData())
            jsonRes = json.loads(str(recvMsg[42:],"utf-8"))
            
            if "output" in jsonRes :
                self.client.close()
                outputs = decodeOutputs(outputTypes, jsonRes["output"])
                parseAndPrintOutput(jsonRes,outputs)
            if "result" in jsonRes:
                if jsonRes["result"] is not None:
                    self.client.close()
                    outputs = decodeOutputs(outputTypes, jsonRes["output"])
                    parseAndPrintOutput(jsonRes["result"],outputs)
                else:
                    recv =  self.client.recv(1024*1024)
                    self.client.close()
                    results = json.loads(str(recv[42:],"utf-8"))
                    outputs = decodeOutputs(outputTypes, results["output"])
                    parseAndPrintOutput(results,outputs)
            elif "error" in jsonRes:
                self.client.close()
                exitError(jsonRes["error"])
            else:
                self.client.close()
                exitError(jsonRes)
        else:
            paramStr = json.dumps(params)
            jsonrpcData = self.jsonRpcPackData(func,paramStr)
            frame = FrameData(bytes(jsonrpcData, "utf-8"))

            recvMsg = self.sendAndGetRecv(frame.genFrameData())
            jsonRes = json.loads(str(recvMsg[42:],"utf-8"))
            
            if "result" in jsonRes:
                if jsonRes["result"] is not None:
                    self.client.close()
                    exitError(jsonRes["result"])
                else:
                    recv =  self.client.recv(1024*1024)
                    self.client.close()
                    exitError(jsonRes["result"])
            elif "error" in jsonRes:
                self.client.close()
                exitError(jsonRes["error"])
            else:
                self.client.close()
                exitError(jsonRes)


    def getBlockLimit(self):
        blockNumber = self.getBlockNumber()
        blockLimit = blockNumber+500
        return numToHex(blockLimit)

    def getBlockNumber(self):
        jsonrpcData = self.jsonRpcPackData("getBlockNumber",'[1]')
        frame = FrameData(bytes(jsonrpcData, "utf-8"))
        recvMsg = self.sendAndGetRecv(frame.genFrameData())
        
        resStr = str(recvMsg[42:], encoding="utf-8")
        jsonRes = json.loads(resStr)
        if "result" not in jsonRes:
            self.client.close()
            if "error" in jsonRes:
                exitError(jsonRes["error"])
            if "message" in jsonRes:
                exitError(jsonRes["message"])
            exitError("Unknown error.")
        result = jsonRes["result"]
        result = result[2:]
        num = hexToNum(result)
        return num

