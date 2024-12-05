from error.Error import exitError


byteToHex = ('0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f')

hexToByte = {
    '0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,
    '8':8,'9':9,'a':10,'b':11,'c':12,'d':13,'e':14,'f':15
}

def bytesToHexStr(byteArr):
    hexStr = ""
    for b in byteArr:
        b1 = byteToHex[(b>>4)&0b1111]
        b2 = byteToHex[b&0b1111]
        hexStr += b1+b2
    return hexStr

def hexStrToBytes(hexStr):
    if len(hexStr) == 0 or hexStr == "0":
        return []
    hexStr = hexStr.lower()
    if len(hexStr) > 1 and hexStr[0] == '0' and hexStr[1] == 'x':
        hexStr = hexStr[2:]
    
    if len(hexStr)%2 == 1:
        hexStr = "0"+hexStr
    bs = []
    count = 0
    b1,b2 = 0,0
    for c in hexStr:
        if not c in hexToByte:
            exitError("Invalid hex string, {}".format(hexStr))
        if count == 0:
            b1 = hexToByte[c]
            count = 1
        else:
            b2 = hexToByte[c]
            bs.append((b1<<4)|b2)
            count = 0
    return bs

def hexToNum(hexStr):
    hexStr = hexStr.lower()
    if len(hexStr) > 1 and hexStr[0] == '0' and hexStr[1] == 'x':
        hexStr = hexStr[2:]
    num = 0
    for i in range(0, len(hexStr)):
        num = num*16 + hexToByte[hexStr[i]]
    return num

def numToHex(num):
    hexStr = ""
    while num > 0:
        b = num&0b1111
        hexStr = byteToHex[b]+hexStr
        num = num>>4
    return hexStr

def numToBytes(num):
    bs = []
    while num > 0:
        bs.append(num&0b11111111)
        num = num>>8
    bs.reverse()
    return bs

def bytesToNum(byteArr):
    num, l = 0, len(byteArr)
    for i in range(0,l):
        num = num*256+byteArr[i]
    return num