ETHERNET_IPV4 = 0x0800
IP_PROTOCOL_UDP = 17
DEFAULT_TTL = 100
MAX_SEGMENT_DATA_SIZE = 500

HOST_A_NAME = "Host A"
HOST_A_IP = "10.0.1.10"
HOST_A_MAC = "AA:AA:AA:AA:AA:AA"
HOST_A_PORT = 5000

HOST_B_NAME = "Host B"
HOST_B_IP = "10.0.2.20"
HOST_B_MAC = "DD:DD:DD:DD:DD:DD"
HOST_B_PORT = 80

ROUTER_NAME = "Router R1"


R1_IF1_NAME = "Interface 1"
R1_IF1_IP = "10.0.1.1"
R1_IF1_MAC = "BB:BB:BB:BB:BB:BB"


R1_IF2_NAME = "Interface 2"
R1_IF2_IP = "10.0.2.1"
R1_IF2_MAC = "CC:CC:CC:CC:CC:CC"

NETWORK_1 = "10.0.1.0/24"
NETWORK_2 = "10.0.2.0/24"

HOST_A_ARP_TABLE = {
    "10.0.1.1": "BB:BB:BB:BB:BB:BB"
}

HOST_B_ARP_TABLE = {
    "10.0.2.1": "CC:CC:CC:CC:CC:CC"
}

R1_ARP_TABLE = {
    "10.0.1.10": "AA:AA:AA:AA:AA:AA",
    "10.0.2.20": "DD:DD:DD:DD:DD:DD"
}

HOST_A_ROUTING_TABLE = {
    NETWORK_2: {
        "next_hop": "10.0.1.1",
        "interface": "Interface 1"
    }
}


# Host B:
# Anything outside local subnet goes to router IF2
HOST_B_ROUTING_TABLE = {
    NETWORK_1: {
        "next_hop": "10.0.2.1",
        "interface": "Interface 2"
    }
}


# Router R1:
# Directly connected routes
R1_ROUTING_TABLE = {
    NETWORK_1: {
        "next_hop": None,
        "interface": "Interface 1"
    },

    NETWORK_2: {
        "next_hop": None,
        "interface": "Interface 2"
    }
}