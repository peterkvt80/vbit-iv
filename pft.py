#!/usr/bin/env python3

# PAGES FROM TEEFAX
# Copyright (c) 2021 Peter Kwan
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
# Pages from Teefax PFT.
# A remote controller for vbit.py
# that goes through pages according to a list
# pft.config has a very simple format
# each line is a page number, a space and a time in seconds.
# 104 15
# 105 15
# The page units can be a wild card * and all pages 0 to 9 will be shown.
# 10* 15
# 11* 15

import zmq
import time

print("Connecting to vbit-iv")
context = zmq.Context()
host = "tcp://127.0.0.1:7777"
socket = context.socket(zmq.REQ)
socket.connect(host)

class Reader:
    def __init__(self, filename):
        # initialise stuff in here
        self.line = ""
        self.state = 0
        self.filename = filename
        with open(filename) as f:
            self.content = f.readlines()
        self.count = len(self.content)
        self.pageIndex = self.count
        self.magazine_number = 1
        self.page_number_units = 0
        self.page_number_tens = 0
        self.page_wildcard = 0
        self.page_timing = 20


reader = Reader("pft.config")
while True:
    socket.send_string(reader.step())
    message = socket.recv()
    print("Received reply" + str(message[0]))