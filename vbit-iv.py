#!/usr/bin/env python3

# Teletext Stream to Invision decoder
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
print('VBIT-iv System started')

import sys
import time
from ttxpage import TTXpage
import zmq


# Globals
packetSize=42 # The input stream packet size. Does not include CRI and FC

# buffer stuff
head=0
tail=0

# decoder state
currentMag=1#4
currentPage=0x00#0x70
capturing = False
elideRow = 0
seeking = True # True while seeking a new page to display
lastPacket = b"AB0123456789012345678901234567890123456789"
holdMode = False
revealMode = False # hidden

# remote
pageNum = "100"

ttx = TTXpage()

print(sys.argv)

# Accept mag and page eg. .vbitvid 1 29
if int(sys.argv[1])>0:
    currentMag = int(sys.argv[1]) % 8
print ("mag = "+str(currentMag))
if int(sys.argv[2])>0:
    currentPage = int(sys.argv[2], 16)
print ("page = "+str(currentPage))

def clearPage():
    return # kill the console print 
    print("\033[2J", end='') # clear screen  
    

def printRow(packet, row=-1, col=-1, pagenum=''):
    return # Kill the console print  
    if row>-1 or col>-1:
        if row == -1:
            row = 0
        if col == -1:
            col = 0  
        print("\033[" + str(row) + ";" + str(col) + "f", end ='')  
    for i in range(2, 42):
        x = packet[i] & 0x7f
        if x < 0x020:
            print ('.', end='')
        else:
            print ( chr(packet[i] & 0x7f), end = '' )
    if pagenum != '':
        print("\033[" + str(row) + ";" + str(col) + "f" + pagenum, end ='')  
    print()

def deham(value):
    # Deham with NO checking! @todo Parity and error correction
    b0 = (value & 0x02) >> 1
    b1 = (value & 0x08) >> 2
    b2 = (value & 0x20) >> 3
    b3 = (value & 0x80) >> 4
    return b0+b1+b2+b3

def mrag(v1, v2):
    rowlsb = deham(v1)
    mag = rowlsb % 8
    if mag==0:
        mag = 8

    row = deham(v2) << 1
    if (rowlsb & 0x08)>0:
        row = row + 1
    return mag, row

def decodePage(packet):
    tens =  deham(packet[3])
    units = deham(packet[2])
    return tens * 0x10 + units

def remote(ch):
    global pageNum
    global currentMag
    global currentPage
    global lastPacket
    global seeking
    global holdMode
    global revealMode
    if ch == 'h': # hold
        holdMode = not holdMode
        return
    if ch == 'r': # reveal-oh
        revealMode = not revealMode
        ttx.reveal(revealMode)
        return
    if ch>='0' and ch<='9':
        pageNum = pageNum + ch
        pageNum = pageNum[1:4]
        print ("Pagenum= " + pageNum)
        # validate
        if pageNum[0]>'0' and pageNum[0]<'9': # valid mag
            currentMag = int(pageNum[0])
            currentPage = int(pageNum[1:3],16)
            print ("mag, page = " + str(currentMag)+', '+hex(currentPage))
            # send the last header again, just so we can update the target page number
            seeking = True # @todo If we select the page we are already on
        ttx.printHeader(lastPacket,  'P'+pageNum+'    ', seeking)            
    else:
        print("Unhandled remote code: " + ch)
        # @todo Reveal, Fastext, Hold, Double height, Page up, Page Down, Mix
              
def process(packet):
    global capturing
    global currentMag
    global currentPage
    global elideRow
    global lastPacket
    global seeking
    result = mrag(packet[0], packet[1])
    mag = result[0]
    row = result[1]
    # If this is a header, decode the page
  
    # If we hit a row that follows a header, skip the packet
    if elideRow>0 and elideRow == row:
        ttx.mainLoop()
        #print("eliding row= " + str(elideRow))
        elideRow=0
        return
  
    # only display things that are on our magazine
    if currentMag == mag: # assume parallel mode
        if row == 0:
            if holdMode:
                ttx.printHeader(lastPacket, "HOLD    ", False)
                return
#      print("\033[0;0fP", end='')
            # is this the magazine that we want?
            page = decodePage(packet)
            capturing = currentPage == page
            if capturing:
                seeking = False # Capture starts if this is the right page
                lastPacket = packet
            if not seeking: # new header starts rendering the page
                clearPage() # @todo Decode header flags
                # @todo Don't clear if the page is already loaded
            printRow(packet, 0, 0, "P{:1d}{:02X}    ".format(currentMag,currentPage))
            elideRow = 0
            # Show the whole header if we are capturing. Otherwise just show the clock
            ttx.printHeader(packet,  "P{:1d}{:02X}    ".format(currentMag,currentPage), seeking)
            #if capturing:
            #printRow(packet, 0, 0, "{:1d}{:02X}".format(mag,page))
            # print("\033[2J", end='') # clear screen  
                #printRow(packet)
        else:
        # @todo Need to copy all pages until a new header arrives
            if capturing and row < 25:
                printRow(packet, row+1)
                if ttx.printRow(packet, row): # double height?
                    elideRow = row+1  
    ttx.mainLoop()
  
# Remote control talks on port 6558
bind = "tcp://*:7777"
print("vbit-vi binding to " + bind)
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind(bind)  
  
try:
    # This thread reads the input stream into a field buffer
    while True:
        # load a field of 16 vbi lines
        for line in range(16):  
            # packet=file.read(packetSize) # file based version
            packet=sys.stdin.buffer.read(packetSize) # read binary from stdin
            process(packet)
        time.sleep(0.020) # 20ms between fields
        # Remote control zmq port 5557
        try:
            #message = socket.recv()
            message = socket.recv(flags=zmq.NOBLOCK)
            message = message.decode("utf-8")
            remote(message)
            #print("Message received " + message)
            socket.send(b"sup?")
        except zmq.Again as e:
            time.sleep(0.001) # do nothing
    
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    print("Keyboard interrupt")    

except Exception as inst:
    print("some error") 
    print(type(inst)) 
    print(inst.args) 
    print(inst) 

finally:
    print("clean up") 