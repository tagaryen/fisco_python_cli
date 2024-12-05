from error.Error import exitError
from algorythm.Keccak256 import keccak256Hash
from util.Hex import (
    hexStrToBytes,
    bytesToHexStr,
    hexToNum,
    numToBytes,
    numToHex,
    bytesToNum
)

def parseParams(params):
    try:
        inputTypes = []
        inputValues = []
        outputTypes = []
        flag = True
        for item in params:
            if item == "-o":
                flag = False
                continue
            if flag:
                i1 = item.find("[")
                i2 = item.find("]")
                if i1 != 0 or i2 < 0:
                    exitError("Invalid input paramters, {}".format(item))
                inputTypes.append(item[1:i2])
                inputValues.append(item[i2+1:])
            else:
                outputTypes.append(item)
        return inputTypes,inputValues,outputTypes
    except Exception as e:
        exitError("Parse input paramters error.")

def encodeFunction(methodName, inputTypes,inputValues):
    if len(inputTypes) != len(inputValues):
        exitError("Invalid number of paramters.")
    try:
        sig = methodName+"("
        for Type in inputTypes:
            sig += Type+","
        sig = sig[:-1]
        sig += ")"
        hashResult = keccak256Hash(bytes(sig, "utf-8"))
        methodId = '0x'+hashResult[0:8]
        encodedParams = encodeParams(inputTypes,inputValues)
        return methodId+encodedParams
    except Exception as e:
        exitError("Encode function error.")

def encodeParams(inputTypes,inputValues):
    try:
        if len(inputTypes) != len(inputValues):
            exitError("Invalid number of paramters.")
        
        result = ""
        dynamicOffset = len(inputTypes)*32
        dynamicEncoded = ""
        for i in range(0, len(inputTypes)):
            encoded = encodeType(inputTypes[i],inputValues[i])
            if inputTypes[i].find("string") == 0 :  #dynamic types
                offsetEncoded = encodeType("int",dynamicOffset)
                result += offsetEncoded
                dynamicEncoded += encoded
                dynamicOffset += (len(encoded)>>1)
            else :
                result += encoded
        return result + dynamicEncoded
    except Exception as e:
        exitError("Encode params error.")



def encodeType(Type, Value):
    if Type.find("int") >= 0:
        value = int(Value)

        neg = False
        if value < 0:
            value = -value
            neg = True
        
        vBytes = numToBytes(value)
        padBytes = []
        pad = 32 - len(vBytes) 
        for i in range(0,pad):
            if neg:
                padBytes.append(0xff)
            else:
                padBytes.append(0)
        vBytes = concatBytes(padBytes,vBytes)
        return bytesToHexStr(vBytes)
    if Type.find("string") == 0:
        value = str(Value)
        valueBs = bytes(value,"utf-8")
        length = len(valueBs)
        pad = 32- length%32
        vBytes = []
        for i in range(0,32):
            vBytes.append(0)
        index = 31
        while length > 0:
            vBytes[i] = length&0b11111111
            index -= 1
            length = length>>8
        for b in valueBs:
            vBytes.append(b)
        # for i in range(0, pad):
        #     vBytes.append(0)
        
        return bytesToHexStr(vBytes)
    if Type.find("address") == 0:
        value = str(Value)
        return encodeType("int",hexToNum(value))
    if Type.find("bytes") == 0:
        valueBs = bytes(Value)
        length = len(valueBs)
        if length > 32:
            exitError("Invalid bytes value, {}".format(Value))
        pad = 32 - length
        vBytes = []
        for i in range(0,pad):
            vBytes.append(0)
        vBytes = concatBytes(valueBs,vBytes)
        return bytesToHexStr(vBytes)

def concatBytes(bs, extend):
    result = []
    for b in bs:
        result.append(b)
    for b in extend:
        result.append(b)
    return result


def decodeOutputs(outputTypes, rawOutput):
    status = rawOutput[:10]
    if hexToNum(status) != 0:
        rawOutput = rawOutput[10:]
    if not isinstance(outputTypes, list):
        exitError("outputTypes must be list.")
    try:
        outputBytes = hexStrToBytes(rawOutput)
        paramsCount = len(outputTypes)
        if paramsCount == 0:
            return []
        offset = 0
        outputs = []
        outputTypes.append("end")
        for typ in outputTypes:
            if typ == "end":
                break
            
            msg = outputBytes[offset:offset+32]
            offset += 32
            num = bytesToNum(msg)
            
            if typ.find("int") >= 0:
                outputs.append(num)
            if typ.find("string") == 0:
                dynmOffset = num
                l = bytesToNum(outputBytes[dynmOffset:dynmOffset+32])
                pad = 0
                if l%32 > 0:
                    pad = 32 - l%32
                strBytes = outputBytes[dynmOffset+32:dynmOffset+32+l]
                outputs.append(str(bytes(strBytes),"utf-8"))
            if typ.find("bytes") == 0:
                index = 31
                for i in range(1,33):
                    if msg[32-i] != 0:
                        index = 32-i
                        break
                outputs.append(bytes(msg[:index]))
            if typ.find("address") == 0:
                addr = numToHex(num)
                if len(addr) != 40:
                    exitError("Invalid address, {}".format(addr))
                outputs.append(addr)
            if typ.find("bool") == 0:
                boolV = "false"
                if num == 1:
                    boolV = "true"
                elif num == 0:
                    boolV = "false"
                else:
                    exitError("Invalid bool, {}".format(num))
                outputs.append(boolV)
        return outputs
    except Exception as e:
        exitError("Decode outputs error, {}".format(rawOutput))
                        


