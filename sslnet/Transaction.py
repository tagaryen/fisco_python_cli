from util.Hex import *

from algorythm.Keccak256 import keccak256Hash
from algorythm.Ecdsa import ecdsa_raw_sign
from util.Random import randomBigHexInt

OFFSET_SHORT_STRING = 0x80
OFFSET_LONG_STRING = 0xb7
OFFSET_SHORT_LIST = 0xc0
OFFSET_LONG_LIST = 0xf7

def encodeField(bs, offset):
    if len(bs) == 1 and offset == OFFSET_SHORT_STRING and bs[0] >= 0x00 and bs[0] <= 0x7f :
        return bs
    elif len(bs) <= 55:
        result = [(offset+len(bs))&0b11111111]
        return concatBytes(result, bs)
    else :
        l = len(bs)
        lenBytes = []
        if (l>>24) != 0:
            lenBytes.append(len>>24)
        if (l>>16)&0b11111111 != 0:
            lenBytes.append((l>>16)&0b11111111)
        if (l>>8)&0b11111111 != 0:
            lenBytes.append((l>>8)&0b11111111)
        if l&0b11111111 != 0:
            lenBytes.append(l&0b11111111)

        result = []
        result.append((len(lenBytes) + offset + 0x37)&0b11111111)
        result = concatBytes(result, lenBytes)
        result = concatBytes(result, bs)
        return result

def encodeTransaction(trans,vrs: tuple):
    bs = []
    randomIdBytes = encodeField(getFieldsBytes(trans["randomId"]),OFFSET_SHORT_STRING)
    bs = concatBytes(bs, randomIdBytes)
    priceBytes = encodeField(getFieldsBytes(trans["gasPrice"]),OFFSET_SHORT_STRING)
    bs = concatBytes(bs, priceBytes)
    limitBytes = encodeField(getFieldsBytes(trans["gasLimit"]),OFFSET_SHORT_STRING)
    bs = concatBytes(bs, limitBytes)
    blockLimitBytes = encodeField(getFieldsBytes(trans["blockLimit"]),OFFSET_SHORT_STRING)
    bs = concatBytes(bs, blockLimitBytes)
    toBytes = encodeField(getFieldsBytes(trans["to"], True),OFFSET_SHORT_STRING)
    bs = concatBytes(bs, toBytes)
    valueBytes = encodeField(getFieldsBytes(trans["value"]),OFFSET_SHORT_STRING)
    bs = concatBytes(bs, valueBytes)
    dataBytes = encodeField(getFieldsBytes(trans["data"]),OFFSET_SHORT_STRING)
    bs = concatBytes(bs, dataBytes)
    chainIdBytes = encodeField(getFieldsBytes(trans["chainId"]),OFFSET_SHORT_STRING)
    bs = concatBytes(bs, chainIdBytes)
    groupIdBytes = encodeField(getFieldsBytes(trans["groupId"]),OFFSET_SHORT_STRING)
    bs = concatBytes(bs, groupIdBytes)
    extraDataBytes = encodeField(getFieldsBytes(""),OFFSET_SHORT_STRING)
    bs = concatBytes(bs, extraDataBytes)

    if vrs != None and len(vrs) == 3:
        bs = concatVRS(bs, vrs)
    return bs

def getFieldsBytes(field, ignoreZero = False):
    numBytes = hexStrToBytes(field)
    if len(numBytes) == 0:
        return []
    if not ignoreZero:
        index = 0
        while numBytes[0] == 0:
            index += 1
        numBytes = numBytes[index:]
    return numBytes


def concatBytes(bs, extend):
    result = []
    for b in bs:
        result.append(b)
    for b in extend:
        result.append(b)
    return result

def concatVRS(bs:list, vrsList:tuple):
    v, r, s = vrsList
    rb = numToBytes(r)
    while rb[0] == 0:
        rb = rb[1:]
    sb = numToBytes(s)
    while sb[0] == 0:
        sb = sb[1:]
    vBytes = [v+27]
    rBytes = encodeField(rb,OFFSET_SHORT_STRING)
    sBytes = encodeField(sb,OFFSET_SHORT_STRING)

    result = []
    result = concatBytes(result, bs)
    result = concatBytes(result, vBytes)
    result = concatBytes(result, rBytes)
    result = concatBytes(result, sBytes)
    return result
    

def signTransaction(trans,privateKey):
    encodedBytes = encodeField(encodeTransaction(trans,None),OFFSET_SHORT_LIST)
    hashResult = keccak256Hash(bytes(encodedBytes))
    v,r,s = ecdsa_raw_sign(bytes(hexStrToBytes(hashResult)),bytes(hexStrToBytes(privateKey)))
    signedTransBytes = encodeField(encodeTransaction(trans,(v,r,s)), OFFSET_SHORT_LIST)
    return bytesToHexStr(signedTransBytes)

def genTansactionDict(blockLimit,to,data, groupId):
    randomId = randomBigHexInt(250)
    return {
        "randomId":randomId,
        "gasPrice":"419ce0",
        "gasLimit":"51f4d5c00",
        "blockLimit":blockLimit,
        "to":to,
        "value":"0",
        "data":data,
        "groupId":groupId,
        "chainId":"1",
        "extraData":""
    }
