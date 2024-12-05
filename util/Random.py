import random
from error.Error import exitError
from .Hex import byteToHex

def randomBigHexInt(bitNum):
    mod = bitNum%4
    r = 0
    if mod == 0:
        r = int(bitNum/4)
    else :
        r = int(bitNum/4) + 1
    hexStr = ""
    for i in range(0, r):
        hexStr += byteToHex[random.randint(0,15)]
    return hexStr

def randomBigInt(bitNum):
    mod = bitNum%4
    binHex,hexStr = "", ""
    for i in range(0, 4-mod):
        binHex += '1'
    
    for i in range(mod,bitNum+mod): 
        bit = random.randint(0,128)%2
        if i > 0 and i%4 == 0:
            h = binaryStrToHexMap(binHex)
            hexStr += h
            binHex = ""
        binHex += str(bit)
    return hexStr

def binaryStrToHexMap(binStr):
    if binStr == "0000":
        return '0'
    if binStr == "0001":
        return '1'
    if binStr == "0010":
        return '2'
    if binStr == "0011":
        return '3'
    if binStr == "0100":
        return '4'
    if binStr == "0101":
        return '5'
    if binStr == "0110":
        return '6'
    if binStr == "0111":
        return '7'
    if binStr == "1000":
        return '8'
    if binStr == "1001":
        return '9'
    if binStr == "1010":
        return 'a'
    if binStr == "1011":
        return 'b'
    if binStr == "1100":
        return 'c'
    if binStr == "1101":
        return 'd'
    if binStr == "1110":
        return 'e'
    if binStr == "1111":
        return 'f'
    exitError("Invalid byte string, {}".format(binStr))