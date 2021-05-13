#!/usr/bin/env python3

# Copyright (c) 2020 Peter Kwan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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

#  Socket to talk to server. TODO: Make the IP address and port a command line parameter
# Default to local host. If you want to control vbit-iv from another computer then
# set the host address to your vbit-iv machine
host = "tcp://127.0.0.1:7777"
#host = "tcp://192.168.1.85:7777"
socket = context.socket(zmq.REQ)
socket.connect(host)

#  main loop. Get character, send request to vbit-i
# Characters that the server accepts:
# Page numbers 0 to 9
# h - hold
# r - reveal
# d - toggle double height
# + - next page
# - - previous page
# u - red button
# i - green button
# o - yellow button
# p - cyan button


# This client can be terminated with
# q or ctrl-c

ch = '?'

while True:
    ch = readchar.readchar()
    if ord(ch) == 3 or ch == 'q':
        socket.send_string(ch)
        exit()
    #print("Sending request " + str(ord(ch))) #str(key))
    socket.send_string(ch)
    #  Get the reply.
    #print("Sent request. Awaiting reply")
    message = socket.recv()
    #print("Received reply" + str(message[0]))
