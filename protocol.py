import struct

class Frame:
    MAX_DATA_SIZE = 1000
    def __init__(self, 
    src_mac: bytes,
    dst_mac: bytes,
    ethertype: int,
    payload: bytes = bytes()
    ):
    

        if len(payload) > Frame.MAX_DATA_SIZE:
            raise RuntimeError('Too much data for one Frame!')
        if len(src_mac) != 6:
            raise RuntimeError('Invalid source MAC address!')
        if len(dst_mac) != 6:
            raise RuntimeError('Invalid destination MAC address!')


        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.ethertype = ethertype
        self.payload = payload
        
        

    def pack(self):
        frame_format = f'!6s6sH{len(self.payload)}s'
        return struct.pack(frame_format, self.dst_mac, self.src_mac, self.ethertype, self.payload)


