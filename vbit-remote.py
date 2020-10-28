#!/usr/bin/env python3

#   Remote control client
#   Connects REQ socket to tcp://localhost:5558
#   Sends remote control commands to vbit-vi

# pip3 install readchar
# pip3 install pyzmq
#
import sys
import zmq
import time
import readchar

print("Connecting to vbit-iv")

context = zmq.Context()

#  Socket to talk to server
host = "tcp://localhost:7777"
host = "tcp://192.168.1.85:7777"
socket = context.socket(zmq.REQ)
socket.connect(host)

#  main loop. Get character, send request to vbit-i
ch = '?'

while True:
    ch = readchar.readchar()
    if ord(ch) == 3 or ch == 'q':
        exit()
    print("Sending request " + str(ord(ch))) #str(key))
    socket.send_string(ch)
    #  Get the reply.
    print("Sent request. Awaiting reply")
    message = socket.recv()
    print("Received reply" + str(message[0]))
