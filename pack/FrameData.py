import uuid
import random

class FrameData :
    data = None

    def __init__(self, data):
        if isinstance(data, list) or isinstance(data, bytes):
            self.data = data
        else:
            raise Exception("帧数据参数类型错误")
            exit(0)

    def genFrameData(self):
        length = 42+len(self.data)

        dataBytes = [length>>24,(length>>16)&0b11111111,(length>>8)&0b11111111,length&0b11111111,0,18]
        for b in range(0,32):
            dataBytes.append(random.randint(0,128))
        for b in [0,0,0,0]:
            dataBytes.append(b)
        for b in self.data:
            dataBytes.append(b)
        return bytes(dataBytes)