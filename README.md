# Mini Internet Protocol Stack Simulator (Python)

## How it works
This project simulates how data travels across a small network, from one computer, through a router, to another computer by following the rules of the OSI model across three layers.

When Host A sends a message, it gets broken into chunks if it's too big. Each chunk gets encasulated layer by layer, first the transport layer adds reliability info like a sequence number and checksum, then the network layer adds source and destination IP addresses, then the data link layer wraps the whole thing with MAC addresses for the next hop. This encapsulated data is what gets handed off to the next device.

When the router receives it, it strips off the outer MAC wrapper, looks at the destination IP, figures out which of its two interfaces to forward it out of, rewraps it with new MAC addresses, and sends it on to Host B.

Host B then unwraps everything in reverse order and passes the raw data up to the application layer which is the final step.

## How to run
Run main.py from the terminal and pass in a message size (in bytes) as an argument. 
e.g.  python3 main.py 10 sends a 10-byte message.
to test segmentation of large messages try: python3 main.py 1200
