import struct

class Frame:
    MAX_DATA_SIZE = 1000
    def __init__(self, 
    src_mac: bytes,
    dst_mac: bytes,
    ethertype: bytes,
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


class Packet:
    def __init__(
        self,
        src_ip: bytes,
        dst_ip: bytes,
        ttl: bytes,
        protocol: bytes,
        length: bytes,
        payload: bytes = bytes()
    ):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.ttl = ttl
        self.protocol = protocol
        self.length = length
        self.payload = payload

class Segment:
        def __init__(
            self,
            src_port: bytes,
            dst_port: bytes,
            seq_num: bytes,
            length: bytes,
            type: bytes,
            checksum: bytes,
            payload: bytes = bytes()
        ):
            self.src_port = src_port
            self.dst_port = dst_port
            self.seq_num = seq_num
            self.length = length
            self.type = type
            self.checksum = checksum
            self.payload = payload

