#!/usr/bin/env python3

# Teletext In-vision viewer
#
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
#
#
# Accesses a vbit2 installation on Linux and display teletext pages.
# It enables you to view teletext services with exactly the same inconvenience as a
# dumb TV picking up a broadcast teletext transmission.

import subprocess
from vbitconfig import Config

import zmq
import readchar
context = zmq.Context()

#  Remote control socket to talk to server
host = "tcp://127.0.0.1:7777"
# host = "tcp://192.168.1.85:7777"
socket = context.socket(zmq.REQ)
socket.connect(host)

# Find out what the current service is called
config = Config()

print("The currently configured service is " + config.service)
launch = config.launch

try:
    streamIn = subprocess.Popen(config.service_stream, shell=True, stdout=subprocess.PIPE, stdin=None)
    streamOut = subprocess.Popen(config.render, shell=True, stdin=streamIn.stdout)
    
    #  main loop. Get character, send request to vbit-i
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
        
          
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    print("Innervision Keyboard interrupt")    

except Exception as inst:
    print("some innervision error") 
    print(type(inst)) 
    print(inst.args) 
    print(inst) 

finally:
    print("clean up")           



#print(' $HOME/vbit2/vbit2 --dir /home/peterk/.teletext-services/Teefax | ./vbit-iv.py 1 0')