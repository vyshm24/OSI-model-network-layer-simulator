import sys

from devices import Host, Router

from config import (
    HOST_A_NAME,
    HOST_A_IP,
    HOST_A_MAC,

    HOST_B_NAME,
    HOST_B_IP,
    HOST_B_MAC,

    ROUTER_NAME,

    R1_IF1_IP,
    R1_IF1_MAC,

    R1_IF2_IP,
    R1_IF2_MAC,

    HOST_A_ROUTING_TABLE,
    HOST_B_ROUTING_TABLE,
    R1_ROUTING_TABLE
)


# sets up the whole network topology and kicks off the data transfer
def main():

    # make sure the user passed in a message size
    if len(sys.argv) != 2:

        print("Usage: python main.py <message_size>")

        return

    message_size = int(sys.argv[1])

    # generate a dummy payload of the requested size
    data = b'A' * message_size

    # create the two end hosts and the router
    host_a = Host(
        HOST_A_NAME,
        HOST_A_IP,
        HOST_A_MAC
    )

    host_b = Host(
        HOST_B_NAME,
        HOST_B_IP,
        HOST_B_MAC
    )

    router = Router(
        ROUTER_NAME,

        R1_IF1_IP,
        R1_IF1_MAC,

        R1_IF2_IP,
        R1_IF2_MAC
    )

    # arp tables — each device knows the mac address of its next hop
    host_a.arp_table = {
        "10.0.1.1": "BB:BB:BB:BB:BB:BB"
    }

    host_b.arp_table = {
        "10.0.2.1": "CC:CC:CC:CC:CC:CC"
    }

    router.arp_table = {
        "10.0.1.10": "AA:AA:AA:AA:AA:AA",
        "10.0.2.20": "DD:DD:DD:DD:DD:DD"
    }

    # routing tables — tells each device which way to send packets for a given network
    host_a.routing_table = HOST_A_ROUTING_TABLE
    host_b.routing_table = HOST_B_ROUTING_TABLE
    router.routing_table = R1_ROUTING_TABLE

    # wire up the devices — hosts point to the router, router knows which host is on which interface
    host_a.next_device = router
    host_b.next_device = router
    router.interface1_device = host_a
    router.interface2_device = host_b

    # kick off the transfer — host a sends the data to host b
    host_a.send_data(
        data,
        HOST_B_IP
    )


if __name__ == "__main__":
    main()