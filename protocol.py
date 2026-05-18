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
            raise RuntimeError('too much data for one Frame!')
        if len(src_mac) != 6:
            raise RuntimeError('invalid source MAC address!')
        if len(dst_mac) != 6:
            raise RuntimeError('invalid destination MAC address!')

        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.ethertype = ethertype
        self.payload = payload

    def pack(self):
        frame_format = f'!6s6sH{len(self.payload)}s'
        return struct.pack(frame_format, self.dst_mac, self.src_mac, self.ethertype, self.payload)
    def unpack(self):
        pass

    def mac_to_bytes(self, mac: str) -> bytes:
        pass


class Packet:
    HEADER_FORMAT = '!4s4sBBH'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

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

        self.total_length = len(self.payload) + Packet.HEADER_SIZE

    
    def ip_to_bytes(self, ip):
        return bytes(map(int, ip.split('.')))

    def bytes_to_ip(self, ip_bytes):
        return '.'.join(map(str, ip_bytes))


    
    def pack(self):
        return struct.pack(
            Packet.HEADER_FORMAT,
            self.ip_to_bytes(self.src_ip),
            self.ip_to_bytes(self.dst_ip),
            self.ttl,
            self.protocol,
            self.total_length
        ) + self.payload



    def unpack(self, data):
        header = struct.unpack(Packet.HEADER_FORMAT, data[:Packet.HEADER_SIZE])
        src_ip = self.bytes_to_ip(header[0])
        dst_ip = self.bytes_to_ip(header[1])
        ttl = header[2]
        protocol = header[3]
        total_length = header[4]
        payload = data[Packet.HEADER_SIZE:]
        
        return Packet (
            src_ip,
            dst_ip,
            ttl,
            protocol,
            total_length,
            payload
        ) 
        # this is now payload of frame when you do Packet.pack()

   

class Segment:

    HEADER_FORMAT = '! H H H H B B'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    ACK = 1
    DATA = 0

    def __init__(
        self,
        src_port: bytes,
        dst_port: bytes,
        seq_num: bytes,
        type: bytes,
        payload: bytes = bytes()
    ):
        self.src_port = src_port
        self.dst_port = dst_port
        self.seq_num = seq_num
       
        self.type = type
        self.checksum = 0
        self.payload = payload

        self.length = Segment.HEADER_SIZE + len(payload)
        
    def compute_checksum(self):
        pass
    def verify_checksum(self):

        old_checksum = self.checksum

        self.compute_checksum()

        return old_checksum == self.checksum

    def pack(self):
        
        self.compute_checksum()

        header = struct.pack(
            Segment.HEADER_FORMAT,
            self.src_port,
            self.dst_port,
            self.length,
            self.checksum,
            self.type,
            self.seq_num
        )

        return header + self.payload
    

    def unpack(raw_data):

        header = raw_data[:Segment.HEADER_SIZE]

        src_port, dst_port, length, checksum, seg_type, seq_num = struct.unpack(
            Segment.HEADER_FORMAT,
            header
        )

        data = raw_data[Segment.HEADER_SIZE:length]

        segment = Segment(
            src_port,
            dst_port,
            seg_type,
            seq_num,
            data
        )

        segment.checksum = checksum

        return segment
    






