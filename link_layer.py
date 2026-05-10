import struct

class Frame:
    MAX_DATA_SIZE = 1000
    def __init__(self, data: bytes = bytes()):
    
        self.len = len(data)
        if self.len > Frame.MAX_DATA_SIZE:
            raise RuntimeError('Too much data for one Frame!')
        
        self.data = data

    def pack(self):
        return struct.pack('! H {}s'.format(self.len),
        self.len, self.data)
        

