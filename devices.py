
from protocol import Frame, Packet, Segment
from config import ETHERNET_IPV4, DEFAULT_TTL, IP_PROTOCOL_UDP

class Device:


    def __init__(self, name, ip, mac):
        self.name = name
        self.ip = ip
        self.mac = mac

        self.routing_table = {}
        self.arp_table = {}
        self.next_device = None
    
    def log(self, layer, message):
        print(f"{self.name}: Layer {layer}: {message}")

    
    def receive_frame(self, raw_frame):

        self.log(2, "Frame received")

        frame = Frame.unpack(raw_frame)

        self.log(2,f"Source MAC learned: {frame.src_mac}")

        self.log(2,"Packet delivered to Network Layer")

        packet = Packet.unpack(frame.payload)

        self.receive_packet(packet)



    def send_frame(self, frame, next_device):
        self.log(2,f"Frame sent: SRC_MAC={frame.src_mac}, DST_MAC={frame.dst_mac}")

        raw_frame = frame.pack()

        next_device.receive_frame(raw_frame)


            
    def send_packet(self, packet, next_hop_ip):

        self.log(3,f"Destination IP read: {packet.dst_ip}")

        self.log(3,"Routing table lookup performed")

        self.log(3,f"Next-hop IP determined: {next_hop_ip}")

        self.log(3,"Packet forwarded to Data Link Layer")


        self.log(2,"Packet received from Network Layer")

        dst_mac = self.arp_table[next_hop_ip]

        self.log(2,f"Destination MAC lookup for next-hop IP ({next_hop_ip}) → {dst_mac}")

        frame = Frame(
            src_mac=self.mac,
            dst_mac=dst_mac,
            ethertype=ETHERNET_IPV4,
            payload=packet.pack()
        )

        self.log(2,f"Frame created: SRC_MAC={self.mac}, DST_MAC={dst_mac}")

        self.send_frame(frame, self.next_device)

    def receive_packet(self, packet):

        self.log(3,
            f"Packet received from Data Link Layer: "
            f"SRC_IP={packet.src_ip}, "
            f"DST_IP={packet.dst_ip}, "
            f"TTL={packet.ttl}"
        )

        self.log(3,f"Destination IP read: {packet.dst_ip}")


        if packet.dst_ip == self.ip:

            self.log(3,"Packet identified as local delivery")

            self.log(3,"Segment delivered to Transport Layer")

            segment = Segment.unpack(packet.payload)

            self.receive_segment(segment)

            return

        old_ttl = packet.ttl
        packet.ttl -= 1

        self.log(3,f"TTL decremented: {old_ttl} → {packet.ttl}")

        if packet.ttl <= 0:

            self.log(3,"Packet dropped due to TTL expiry")

            return

        self.log(3,"Routing table lookup performed")

        if packet.dst_ip.startswith("10.0.2."):

            next_hop_ip = packet.dst_ip

            self.log(3,f"Next-hop IP determined: {next_hop_ip}")

            self.log(3,"Outgoing interface selected (Interface 2)")

        else:

            next_hop_ip = packet.dst_ip

            self.log(3,f"Next-hop IP determined: {next_hop_ip}")

            self.log(3,"Outgoing interface selected (Interface 1)")

        self.log(3,"Packet forwarded to Data Link Layer")


        self.send_packet(packet, next_hop_ip)

    def send_segment(self, segment, dst_ip):

        self.log(4,"Checksum computed")

        segment.compute_checksum()

        segment_type = "ACK" if segment.type == Segment.ACK else "DATA"

        self.log(4,
            f"Segment created by adding transport layer header "
            f"({segment_type}, seq={segment.seq_num}) "
            f"(encapsulation)"
        )

        self.log(4,"Segment sent to Network Layer")

        # Encapsulate into Layer 3 packet
        packet = Packet(
            src_ip=self.ip,
            dst_ip=dst_ip,
            ttl=DEFAULT_TTL,
            protocol=IP_PROTOCOL_UDP,
            payload=segment.pack()
        )

        self.log(3,
            f"Segment received from Transport Layer: "
            f"SRC_IP={packet.src_ip}, "
            f"DST_IP={packet.dst_ip}, "
            f"TTL={packet.ttl}"
        )

        # Determine next hop
        if dst_ip.startswith("10.0.2."):
            next_hop_ip = "10.0.1.1"

        else:
            next_hop_ip = "10.0.2.1"

        self.send_packet(packet, next_hop_ip)


    def receive_segment(self, segment):

        self.log(4,"Segment received from Network Layer")


        if segment.verify_checksum():

            self.log(4,"Checksum verified")

        else:

            self.log(4,"Segment discarded due to checksum error")

            return

        if segment.type == Segment.ACK:

            self.log(4,f"ACK received: seq={segment.seq_num}")

            return


        self.log(4,
            f"DATA segment delivered to Application Layer. "
            f"Data size={len(segment.payload)}"
        )

        ack_segment = Segment(
            src_port=segment.dst_port,
            dst_port=segment.src_port,
            seq_num=segment.seq_num,
            type=Segment.ACK,
            payload=b''
        )

        self.log(4,
            f"Segment created by adding transport layer header "
            f"(ACK, seq={segment.seq_num})"
        )

        self.log(4,"Segment sent to Network Layer")

        self.send_segment(
            ack_segment,
            self.last_sender_ip
        )



class Host(Device):

    def __init__(self, name, ip, mac):

        super().__init__(name, ip, mac)

   
        self.current_seq = 0


        self.expected_seq = 0

    def send_data(self, data, dst_ip):

        self.log(4,f"Data received from Application Layer. Data size={len(data)}")

        segment = Segment(
            src_port=5000,
            dst_port=80,
            seq_num=self.current_seq,
            type=Segment.DATA,
            payload=data
        )

        self.send_segment(segment, dst_ip)

        # Alternate bit
        self.current_seq = 1 - self.current_seq





class Router(Device):

    def __init__(
        self,
        name,
        interface1_ip,
        interface1_mac,
        interface2_ip,
        interface2_mac
    ):

        super().__init__(name, interface1_ip, interface1_mac)

        self.interface1_ip = interface1_ip
        self.interface1_mac = interface1_mac

        self.interface2_ip = interface2_ip
        self.interface2_mac = interface2_mac

        self.interface1_device = None
        self.interface2_device = None
    
    def send_packet(self, packet, next_hop_ip):

        self.log(3, f"Destination IP read: {packet.dst_ip}")

        self.log(3, "Routing table lookup performed")

        self.log(3, f"Next-hop IP determined: {next_hop_ip}")

    

        if packet.dst_ip.startswith("10.0.2."):

            outgoing_mac = self.interface2_mac
            next_device = self.interface2_device

            self.log(
                3,
                "Outgoing interface selected (Interface 2)"
            )

        else:

            outgoing_mac = self.interface1_mac
            next_device = self.interface1_device

            self.log(
                3,
                "Outgoing interface selected (Interface 1)"
            )

        self.log(3, "Packet forwarded to Data Link Layer")

        self.log(2, "Packet received from Network Layer")

        dst_mac = self.arp_table[next_hop_ip]

        self.log(
            2,
            f"Destination MAC lookup for next-hop IP "
            f"({next_hop_ip}) → {dst_mac}"
        )

        frame = Frame(
            src_mac=outgoing_mac,
            dst_mac=dst_mac,
            ethertype=ETHERNET_IPV4,
            payload=packet.pack()
        )

        self.log(
            2,
            f"Frame created: SRC_MAC={outgoing_mac}, DST_MAC={dst_mac}"
        )

        self.send_frame(frame, next_device)