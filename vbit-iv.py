#!/usr/bin/env python3

# T42 Teletext Stream to In-vision decoder
#
# Copyright (c) 2020-2026 Peter Kwan
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
from packet import Packet, metaData
from clut import clut, Clut


# Globals
packetSize=42 # The input stream packet size. Does not include CRI and FC

# buffer stuff
head=0
tail=0

# decoder state
currentMag=1#4
currentPage=0x00#0x70
capturing = False # True while we are accepting rows for the selected page
wasCapturing = False # True if last row was accepted. Used to detect when a page load is complete.
elideRow = 0
seeking = True # True while seeking a new page to display
lastPacket = b"AB0123456789012345678901234567890123456789"
holdMode = False
subCode = 0 # The current page subcode
lastSubcode = 0 # The previous carousel page subcode
rowCounter = 0 # Rows count for this page so far, except for rows after Double Height

suppressHeader = False

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

def dump(pkt, row):
    print("dump row = "+str(row))
    print(pkt.hex())

def deham(value):
    # Deham with NO checking! @todo Parity and error correction
    b0 = (value & 0x02) >> 1
    b1 = (value & 0x08) >> 2
    b2 = (value & 0x20) >> 3
    b3 = (value & 0x80) >> 4
    return b0+b1+b2+b3

def mrag(byte1: int, byte2: int) -> tuple[int, int]:
    """Decode Teletext MRAG (Magazine and Row Address Group) from two bytes."""
    ROW_LSB_FLAG = 0x08  # bit indicating the least-significant bit of the row number

    decoded1 = deham(byte1)
    magazine = decoded1 % 8 or 8  # magazines are 1..8, where 0 maps to 8

    row_number = (deham(byte2) << 1) | (1 if (decoded1 & ROW_LSB_FLAG) else 0)
    return magazine, row_number

def decodePage(pkt):
    tens =  deham(pkt[3])
    units = deham(pkt[2])
    return tens * 0x10 + units

def decodeSubcode(pkt):
    s1 = deham(pkt[4])
    s2 = deham(pkt[5]) & 0x07
    s3 = deham(pkt[6])
    s4 = deham(pkt[7]) & 0x03
    return (s4 << 11) + (s3 << 7) + (s2 << 4) + s1

def getC7(pkt): # C7 - Suppress header
    s1 = deham(pkt[8])
    return s1 & 0x01

def remote(ch):
    global pageNum
    global currentMag
    global currentPage
    global lastPacket
    global seeking
    global holdMode
    if ch == '':
        return
    if ch == 'h': # hold
        holdMode = not holdMode
        return
    if ch == 'r': # reveal-oh
        ttx.toggleReveal()
        return
    if ch == 'q' or ord(ch) == 27: # quit
        exit()
    if ch == 'P' or ch == 'u': # f1 red link
        currentMag = ttx.get_mag(0)
        currentPage = ttx.get_page(0)
        print(str(currentMag) + " " + hex(currentPage))
        seeking = True
        ttx.clear() # Doubt we want to do this!
        return
    if ch == 'Q'  or ch == 'i': # f2: green link
        currentMag = ttx.get_mag(1)
        currentPage = ttx.get_page(1)
        print(str(currentMag) + " " + hex(currentPage))
        seeking = True
        return
    if ch == 'R' or ch == 'o': # f3 yellow link
        currentMag = ttx.get_mag(2)
        currentPage = ttx.get_page(2)
        print(str(currentMag) + " " + hex(currentPage))
        seeking = True
        return
    if ch == 'S' or ch == 'p': # f4 cyan link
        currentMag = ttx.get_mag(3)
        currentPage = ttx.get_page(3)
        print(str(currentMag) + " " + hex(currentPage))
        seeking = True
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
        page_number = 'P' + pageNum
        print("page number = " + page_number)
        ttx.print_header(lastPacket,  page_number+'    ', seeking, False)
    if ch=='d':
        metaData.dump()
    else:
        print("[vbit-iv] Unhandled remote code: " + ch)
        # @todo Reveal, Fastext, Hold, Double height, Page up, Page Down, Mix
    #if seeking:
    #    ttx.clear()

# \param pkt - raw T42 packet to process
def process(pkt):
    """
    Processes a teletext packet and handles it based on its type and current capturing state.

    :param pkt: The teletext packet to process. Its length must meet the minimum packet length.
    :type pkt: bytes

    :raises ValueError: Raised if the packet length is less than the required minimum length.
    :raises RuntimeError: Raised if there is an issue decoding specific packet rows or unsupported
        packet types are encountered.

    :return: This function does not return any values. It controls the flow of processing teletext
        packets and instructs appropriate handling for headers and body rows.
    """
    global capturing
    global wasCapturing
    global currentMag
    global currentPage
    global elideRow
    global rowCounter  # Counts the rows, except the rows following a double height row
    global lastPacket
    global seeking
    global holdMode
    global subCode
    global lastSubcode
    global clut
    global suppressHeader

    MIN_PACKET_BYTES = 42
    HEADER_ROW = 0
    LAST_DISPLAY_ROW_EXCLUSIVE = 25  # rows 0..24 inclusive are displayable

    def _handle_header(packet: bytes) -> bool:
        """
        Handle row 0 header packets.
        Returns False if processing should stop early (e.g. HOLD mode).
        """
        global capturing, wasCapturing, elideRow, rowCounter, lastPacket, seeking, lastSubcode, suppressHeader

        elideRow = 0  # new header, cancel any elide that might have happened

        if holdMode:
            ttx.print_header(lastPacket, "HOLD    ", False, False)
            return False

        page = decodePage(packet)
        subcode = decodeSubcode(packet)  # Used to clear down page if changed. Also clears X26 char map

        capturing = (currentPage == page)
        if capturing:
            rowCounter = 0
            seeking = False  # Capture starts if this is the right page
            lastPacket = packet
            suppressHeader = getC7(packet) > 0

            if subcode != lastSubcode:
                lastSubcode = subcode
                ttx.clear()

            wasCapturing = True
        else:
            # If we have fewer rows because of double height, we must blank the extra lines
            if wasCapturing:
                wasCapturing = False

        if seeking:
            suppressHeader = False
            clut.reset()  # @todo Do we need to save colours in some cases?

        page_label = "P{:1d}{:02X}    ".format(currentMag, currentPage)
        ttx.print_header(packet, page_label, seeking, suppressHeader)
        return True

    def _handle_body_row(packet: bytes, packet_row: int) -> bool:
        """
        Handle non-header rows.
        Returns False if we should stop early (elided row).
        """
        global elideRow, rowCounter

        # If we hit a row that follows a double height, skip the packet
        if elideRow > 0 and elideRow == packet_row:
            ttx.mainLoop()
            print("[vbit-iv]eliding row= " + str(elideRow) + " rowCounter = " + str(rowCounter))
            elideRow = 0
            return False

        if not capturing:
            return True

        if packet_row < LAST_DISPLAY_ROW_EXCLUSIVE:
            if ttx.printRow(packet, packet_row):  # printable row. Is it double height?
                elideRow = packet_row + 1
            rowCounter += 1

        if packet_row == 26:
            print("process packet26 called")
            metaData.decode(packet, 26)
        elif packet_row == 27:  # fastext
            ttx.decodeLinks(packet)
        elif packet_row == 28:  # region / metadata
            metaData.decode(packet, 28)
        elif packet_row == 29:
            print("Unsupported packet type = " + str(packet_row))
        elif packet_row == 30:
            print("Unsupported packet type = " + str(packet_row))

        return True

    if len(pkt) < MIN_PACKET_BYTES:  # Quit if we don't have a full packet
        print("invalid teletext packet")
        return

    mag, row = mrag(pkt[0], pkt[1])

    # only display things that are on our magazine
    if currentMag != mag:  # assume parallel mode
        ttx.mainLoop()
        return

    if row == HEADER_ROW:
        if not _handle_header(pkt):
            return
    else:
        if not _handle_body_row(pkt, row):
            return

    # ETS 300 706: May 1997
    ttx.mainLoop()
# Local control


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
        #print("x")
        for line in range(16):
            # packet=file.read(packetSize) # file based version
            packet=sys.stdin.buffer.read(packetSize) # read binary from stdin
            if len(packet)<42:
                print ("No source data. (Check vbit2 and the configured teletext service)")
            else:
                process(packet)
            #print("y")
        # see if the keyboard has received a remote control code
        key = ttx.getKey()
        if key != ' ':
            if key == 'q' or key == 27:
                exit()
            remote(key)
        time.sleep(0.020) # 20ms between fields


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

# except Exception as inst:
    # print("vbit-iv error")
    # print(type(inst))
    # print(inst.args)
    # print(inst)

finally:
    print("vbit-iv clean up")
