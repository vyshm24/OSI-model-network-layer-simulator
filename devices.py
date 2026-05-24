
from protocol import Frame, Packet, Segment
from config import ETHERNET_IPV4, DEFAULT_TTL, IP_PROTOCOL_UDP

# base class for all network devices — hosts and routers both build on this.
# handles all the layer-by-layer processing: frames at l2, packets at l3, segments at l4.
class Device:


    # sets up the device's identity and initializes all the tables and state it needs
    def __init__(self, name, ip, mac):
        self.name = name
        self.ip = ip
        self.mac = mac

        self.routing_table = {}
        self.arp_table = {}
        self.next_device = None
        self.expected_seq = 0
        self.last_ack_seq = None
        self.last_sender_ip = None
    
    # checks the routing table to find a matching route for the destination ip
    def lookup_route(self, dst_ip):
        for network, route in self.routing_table.items():
            net_prefix = network.split('/')[0].rsplit('.', 1)[0]
            if dst_ip.startswith(net_prefix + '.'):
                return route
        return None

    # prints a formatted log message showing which device and layer the event came from
    def log(self, layer, message):
        print(f"{self.name}: Layer {layer}: {message}")

    
    # called when a raw frame arrives — unpacks it and passes the packet up to layer 3
    def receive_frame(self, raw_frame, sender=None):

        self.log(2, "Frame received")

        frame = Frame.unpack(raw_frame)

        self.log(2,f"Source MAC learned: {frame.src_mac}")
        self.log(2,"Packet delivered to Network Layer")

        packet = Packet.unpack(frame.payload)
        self.receive_packet(packet)



    # packs the frame into bytes and hands it off to the next device
    def send_frame(self, frame, next_device):
        raw_frame = frame.pack()
        self.log(2, "Frame sent")
        next_device.receive_frame(raw_frame, sender=self)


            
    # wraps a packet in a frame and sends it out — looks up the destination mac first
    def send_packet(self, packet, next_hop_ip):

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

    # handles an incoming packet — delivers it locally if it's for us, or forwards it if not
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

            self.last_sender_ip = packet.src_ip

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

        route = self.lookup_route(packet.dst_ip)
        next_hop_ip = route["next_hop"] if route["next_hop"] else packet.dst_ip

        self.log(3,f"Next-hop IP determined: {next_hop_ip}")
        self.log(3,f"Outgoing interface selected ({route['interface']})")
        self.log(3,"Packet forwarded to Data Link Layer")


        self.send_packet(packet, next_hop_ip)

    # takes a segment, computes its checksum, wraps it in a packet, and sends it down through the layers
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

        # encapsulate into layer 3 packet
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

        route = self.lookup_route(dst_ip)
        next_hop_ip = route["next_hop"] if route["next_hop"] else dst_ip

        self.log(3, f"Destination IP read: {dst_ip}")

        self.log(3, "Routing table lookup performed")

        self.log(3, f"Next-hop IP determined: {next_hop_ip}")

        self.log(3, "Outgoing interface selected")

        self.log(3, "Packet forwarded to Data Link Layer")

        self.send_packet(packet, next_hop_ip)


    # processes an incoming segment — verifies the checksum, handles acks, and deals with duplicates
    def receive_segment(self, segment):

        self.log(4,"Segment received from Network Layer")

        if segment.verify_checksum():
            self.log(4,"Checksum verified")
        else:
            self.log(4,"Segment discarded due to checksum error")
            return

        if segment.type == Segment.ACK:
            self.ack_received = True
            self.ack_seq = segment.seq_num
            self.log(4,f"ACK received: seq={segment.seq_num}")
            return

        if segment.seq_num != self.expected_seq:
            self.log(4,"Duplicate segment received, re-sending last ACK")
            ack_segment = Segment(
                src_port=segment.dst_port,
                dst_port=segment.src_port,
                seq_num=self.last_ack_seq,
                type=Segment.ACK,
                payload=b''
            )
            self.send_segment(ack_segment, self.last_sender_ip)
            return

        self.log(4,
            f"DATA segment delivered to Application Layer. "
            f"Data size={len(segment.payload)}"
        )

        self.last_ack_seq = segment.seq_num
        self.expected_seq = 1 - self.expected_seq

        ack_segment = Segment(
            src_port=segment.dst_port,
            dst_port=segment.src_port,
            seq_num=segment.seq_num,
            type=Segment.ACK,
            payload=b''
        )

        self.send_segment(ack_segment, self.last_sender_ip)



# represents an end host — the thing actually sending and receiving data
class Host(Device):

    # sets up host-specific state on top of the base device init
    def __init__(self, name, ip, mac):

        super().__init__(name, ip, mac)
   
        self.current_seq = 0
        self.ack_received = False
        self.ack_seq = None

    # splits data into 500-byte chunks and sends each one using stop-and-wait
    # waits for the correct ack before moving on, retransmits if something goes wrong
    def send_data(self, data, dst_ip):

        for i in range(0, len(data), 500):
            chunk = data[i:i + 500]

            self.log(4,f"Data received from Application Layer. Data size={len(chunk)}")

            segment = Segment(
                src_port=5000,
                dst_port=80,
                seq_num=self.current_seq,
                type=Segment.DATA,
                payload=chunk
            )

            while True:
                self.ack_received = False
                self.send_segment(segment, dst_ip)
                if self.ack_received and self.ack_seq == self.current_seq:
                    self.current_seq = 1 - self.current_seq
                    break
                else:
                    self.log(4,"Segment retransmitted due to incorrect ACK")






# a router with two interfaces — its job is to forward packets between networks
class Router(Device):

    # sets up both interfaces with their ips, macs, and placeholders for connected devices
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
    
    # picks the right outgoing interface based on the routing table, then builds and sends the frame
    def send_packet(self, packet, next_hop_ip):

        route = self.lookup_route(packet.dst_ip)
        if route["interface"] == "Interface 2":
            outgoing_mac = self.interface2_mac
            next_device = self.interface2_device
        else:
            outgoing_mac = self.interface1_mac
            next_device = self.interface1_device

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

    # figures out which interface the frame came in on, then unpacks and passes it up
    def receive_frame(self, raw_frame, sender=None):

        if sender == self.interface1_device:
            interface = "Interface 1"
        else:
            interface = "Interface 2"

        self.log(2, f"Frame received on {interface}")
        frame = Frame.unpack(raw_frame)
        self.log(2, f"Source MAC learned: {frame.src_mac} on {interface}")
        self.log(2, "Packet delivered to Network Layer")
        packet = Packet.unpack(frame.payload)
        self.receive_packet(packet)

    # works out which interface to forward on, then sends the frame out that way
    def send_frame(self, frame, next_device):
        if next_device == self.interface2_device:
            interface = "Interface 2"
        else:
            interface = "Interface 1"
            
        raw_frame = frame.pack()
        self.log(2, f"Frame forwarded on {interface}")
        next_device.receive_frame(raw_frame, sender=self)