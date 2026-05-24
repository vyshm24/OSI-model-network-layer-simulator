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
    R1_IF2_MAC
)


def main():


    if len(sys.argv) != 2:

        print("Usage: python main.py <message_size>")

        return

    message_size = int(sys.argv[1])



    data = b'A' * message_size


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


    # Host A knows router interface 1 MAC
    host_a.arp_table = {
        "10.0.1.1": "BB:BB:BB:BB:BB:BB"
    }

    # Host B knows router interface 2 MAC
    host_b.arp_table = {
        "10.0.2.1": "CC:CC:CC:CC:CC:CC"
    }

    # Router knows both hosts
    router.arp_table = {
        "10.0.1.10": "AA:AA:AA:AA:AA:AA",
        "10.0.2.20": "DD:DD:DD:DD:DD:DD"
    }


    # Host A sends to router
    host_a.next_device = router

    # Host B sends to router
    host_b.next_device = router

    # Router interface connections
    router.interface1_device = host_a
    router.interface2_device = host_b


    host_a.send_data(
        data,
        HOST_B_IP
    )


if __name__ == "__main__":
    main()