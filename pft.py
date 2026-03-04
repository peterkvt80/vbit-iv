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
# 11* 20

import zmq
import time

print("Connecting to vbit-iv")
context = zmq.Context()
host = "tcp://127.0.0.1:7777"
socket = context.socket(zmq.REQ)
socket.connect(host)


def send_digit(ch):
    socket.send_string(ch)
    socket.recv()


def send_page(page_str):
    for ch in page_str:
        send_digit(ch)
        time.sleep(0.05)  # small delay between digits


class Reader:
    def __init__(self, filename):
        self.filename = filename
        with open(filename) as f:
            self.content = [line.strip() for line in f.readlines()]
        # Remove blank lines and comments
        self.content = [l for l in self.content if l and not l.startswith('#')]
        self.count = len(self.content)
        self.pageIndex = -1  # will advance to 0 on first step
        self.page_wildcard = False
        self.page_number_units = 0
        self.current_page_base = ""  # e.g. "13" for "13*"
        self.page_timing = 20

    def step(self):
        # If we're mid-wildcard cycle, advance to next unit
        if self.page_wildcard:
            self.page_number_units += 1
            if self.page_number_units > 9:
                self.page_wildcard = False  # done, fall through to next config line
            else:
                time.sleep(self.page_timing)
                return self.current_page_base + str(self.page_number_units)

        # Move to next config line
        self.pageIndex = (self.pageIndex + 1) % self.count
        line = self.content[self.pageIndex]

        parts = line.split()
        page_str = parts[0]
        self.page_timing = int(parts[1]) if len(parts) > 1 else 20

        if page_str[2] == '*':
            # Wildcard: cycle units 0-9
            self.current_page_base = page_str[0:2]
            self.page_wildcard = True
            self.page_number_units = 0
            time.sleep(self.page_timing)
            return self.current_page_base + "0"
        else:
            self.page_wildcard = False
            time.sleep(self.page_timing)
            return page_str  # e.g. "200", "692", "104"


reader = Reader("pft.config")
while True:
    page = reader.step()
    print("Navigating to page: " + page)
    send_page(page)