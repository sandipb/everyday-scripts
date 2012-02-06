#!/bin/bash
#
# Add the following lines using `iptables save` if supported, or else
# add them to the end of /etc/rc.local

SHARED_NET="192.168.200.0/24"

# Add one line for each interface that would have the network connection
# to the rest of the Internet.
sudo iptables -t nat -A POSTROUTING -s $SHARED_NET -o eth0  -j MASQUERADE
sudo iptables -t nat -A POSTROUTING -s $SHARED_NET -o wlan0  -j MASQUERADE
