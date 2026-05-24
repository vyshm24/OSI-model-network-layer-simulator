import struct

def bytes_to_mac(mac_bytes: bytes) -> str:
    return ':'.join(f'{byte:02X}' for byte in mac_bytes)

def mac_to_bytes(mac: str) -> bytes:
    return bytes.fromhex(mac.replace(':', ''))

def ip_to_bytes(ip):
    return bytes(map(int, ip.split('.')))

def bytes_to_ip(ip_bytes):
    return '.'.join(map(str, ip_bytes))

class Frame:
    MAX_DATA_SIZE = 1000
    HEADER_FORMAT = '! 6s 6s H'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, 
        src_mac: str,
        dst_mac: str,
        ethertype: int,
        payload: bytes = bytes()
    ):
        if len(payload) > Frame.MAX_DATA_SIZE:
            raise RuntimeError('too much data for one Frame!')
        if len(src_mac.split(':')) != 6:
            raise RuntimeError('invalid source MAC address!')
        if len(dst_mac.split(':')) != 6:
            raise RuntimeError('invalid destination MAC address!')

        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.ethertype = ethertype
        self.payload = payload

    def pack(self):

        self.dst_mac = mac_to_bytes(self.dst_mac)
        self.src_mac = mac_to_bytes(self.src_mac)

        frame_format = f'!6s6sH{len(self.payload)}s'
        return struct.pack(frame_format, self.dst_mac, self.src_mac, self.ethertype, self.payload)

    @staticmethod
    def unpack(raw_data):

        header = raw_data[:Frame.HEADER_SIZE]

        dst_mac, src_mac, eth_type = struct.unpack(
            Frame.HEADER_FORMAT,
            header
        )

        payload = raw_data[Frame.HEADER_SIZE:]

        return Frame(
            bytes_to_mac(src_mac),
            bytes_to_mac(dst_mac),
            eth_type,
            payload
        )

    


class Packet:
    HEADER_FORMAT = '!4s4sBBH'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(
        self,
        src_ip: str,
        dst_ip: str,
        ttl: int,
        protocol: int,
        payload: bytes = bytes()
    ):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.ttl = ttl
        self.protocol = protocol
        self.payload = payload

        self.total_length = len(self.payload) + Packet.HEADER_SIZE

    



    
    def pack(self):
        return struct.pack(
            Packet.HEADER_FORMAT,
            ip_to_bytes(self.src_ip),
            ip_to_bytes(self.dst_ip),
            self.ttl,
            self.protocol,
            self.total_length
        ) + self.payload


    @staticmethod
    def unpack(data):
        header = struct.unpack(Packet.HEADER_FORMAT, data[:Packet.HEADER_SIZE])
        src_ip = bytes_to_ip(header[0])
        dst_ip = bytes_to_ip(header[1])
        ttl = header[2]
        protocol = header[3]
        total_length = header[4]
        payload = data[Packet.HEADER_SIZE:]
        
        return Packet (
            src_ip,
            dst_ip,
            ttl,
            protocol,
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
        src_port: int,
        dst_port: int,
        seq_num: int,
        type: int,
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
        checksum = 0

        # Add header fields
        checksum += self.src_port
        checksum += self.dst_port
        checksum += self.length
        checksum += self.type
        checksum += self.seq_num

        # Add payload bytes
        for byte in self.payload:
            checksum += byte

        # Keep checksum within 16 bits
        checksum = checksum % 65535

        self.checksum = checksum

        return checksum

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
    
    @staticmethod
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
            seq_num,
            seg_type,
            data
        )

        segment.checksum = checksum

        return segment
    






