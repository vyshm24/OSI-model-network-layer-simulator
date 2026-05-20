
class Device:
    def __init__(self, name, ip, mac):
        self.name = name
        self.ip = ip
        self.mac = mac

        self.routing_table = {}
    
    def log(self, layer, message):
        print(f"{self.name}: Layer {layer}: {message}")

    def send_frame(self, frame, next_device):
        pass
    def receive_frame(self, frame):
        pass

    def send_packet(self, packet):
        pass

    def receive_packet(self, packet):
        pass

    def send_segment(self, segment, dst_ip):
        pass

    def receive_segment(self, segment):
        pass







