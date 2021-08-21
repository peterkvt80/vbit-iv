# ttxpage.py.
#
# VBIT Stream renderer. Teletext page level.
# You can modify this to run full frame
# or a smaller window
#
# Copyright (c) 2020-2021 Peter Kwan
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

from tkinter import Tk
from ttxline import TTXline


import screeninfo

class TTXpage:
    print("TTXPage created")
    
    def get_monitor_from_coord(self, x, y):
        monitors = screeninfo.get_monitors()

        for m in reversed(monitors):
            if m.x <= x <= m.width + m.x and m.y <= y <= m.height + m.y:
                return m
        return monitors[0]

  
          

    def __init__(self):
        self.root = Tk()
        
        # Get the screen which contains top
        current_screen = self.get_monitor_from_coord(self.root.winfo_x(), self.root.winfo_y())

        # Get the monitor's size
        self.width_value = current_screen.width
        self.height_value = current_screen.height          

        self.root.configure(background='black', borderwidth=0, highlightthickness=0)
        geometry = "%dx%d+0+0" % (self.width_value, self.height_value)
        print('[ttxpage::_init__] geometry = ' + geometry)
        
        print(' GEOMETRY = ' + geometry)
        self.root.geometry(geometry)

        # Make it full screen (Comment it out if you want to run in a window)
        self.root.wm_attributes('-fullscreen','true')

        self.root.wait_visibility(self.root)

        # lines
        self.lines = TTXline(self.root, self.height_value)
        self.lines.text.pack()

        self.root.update_idletasks()
        self.root.update()
        
        self.mag=[None] * 4
        self.page=[None] * 4
        
        self.root.bind('<KeyPress>', self.onKeyPress)
        
        self.buffer = []
        
        # Level 1.5 character replacement
        self.rowAddr = 0
        self.colAddr = 0
        print("ttiPage constructor exits")
        
        
    # Return the page number for the link selected by index
    def getPage(self, index):
        return self.page[index]

    # Return the magazine number for the link selected by index
    def getMag(self, index):
        return self.mag[index]
        
    def deham(self, value):
        # Deham with NO checking! @todo Parity and error correction
        b0 = (value & 0x02) >> 1
        b1 = (value & 0x08) >> 2
        b2 = (value & 0x20) >> 3
        b3 = (value & 0x80) >> 4
        return b0+b1+b2+b3
    
    # return True if the packet contained double height
    def printRow(self, packet, row):
        if row < 0 or row > 24 :
            return False
        return self.lines.printRow(packet, row)

    def printHeader(self, packet, page, seeking, suppress = False):
        self.lines.printHeader(packet, page, seeking, suppress)

    # Actually draw the stuff
    def mainLoop(self):
        self.root.update_idletasks()
        self.root.update()
        
    def toggleReveal(self):
        self.lines.toggleReveal()
        
    # decode packet 27 fastext links. @TODO MOVE TO PACKET
    def decodeLinks(self, packet):
        offset = 2
        dc = self.deham(packet[6 + offset]) # designation code
        # print ("packet 27 dc = " + str(dc))
        # @todo extract the row 24 display 
        for i in range(4):
            mag = self.deham(packet[0]) &0x07 # Magazine of this packet
            addr = (i-1) * 6 + 7 + offset
            b1 = self.deham(packet[addr])
            b2 = self.deham(packet[addr+1])
            M1 = self.deham(packet[addr+3]) & 0x08 # relative magazie of target link M1, M2, M3
            M2 = self.deham(packet[addr+5]) & 0x04
            M3 = self.deham(packet[addr+5]) & 0x08
            tMag = mag
            if M1:
                tMag = tMag ^ 0x01
            if M2:
                tMag = tMag ^ 0x02
            if M3:
                tMag = tMag ^ 0x04
            if tMag == 0:
                tMag = 8
            page = b2 * 0x10 + b1
            #print("mag = " + hex(mag) + ", Target tMag = " + hex(tMag) + ", " + hex(b1) + ", " + hex(b2))
            #print("link " + str(i) + " = " + str(tMag) + " " + hex(page) )
            self.mag[i] = tMag
            self.page[i] = page
            
            # @todo Calculate the relative magazine
        
  
    def reverse(self, x): # reverse the bit order in a byte
        return
        x = ((x & 0xF0) >> 4) | ((x & 0x0F) << 4)
        x = ((x & 0xCC) >> 2) | ((x & 0x33) << 2)
        x = ((x & 0xAA) >> 1) | ((x & 0x55) << 1)
        return x
    
    def onKeyPress(self, event):
        self.buffer.append(event.char)
        if event.char!='':
            print("You pressed " + str(ord(event.char)))
        
    def getKey(self):
        if self.buffer:
            key = self.buffer.pop(0)
            if key != '':
                print("key == " + str(ord(key)))
                if key == 105: # Mappings F1
                    key = 'P'
                return key
        else:
            key = ' '
        return key
    
    def dumpPacket(self, pkt):
        for i in range(8):
            print(str(i) + ":" + hex(pkt[i]) + ' ', end='')
        print()
    
    ### IN PROGRESS: Move packet handling to packet.py    
    def decodeRow26(self, pkt):
        return # This is moved to packet
        # There is a lot of stuff in X26. Initially just look at diacriticals
        #self.dumpPacket(pkt)
        dc = self.deham(pkt[2])
        tp =  self.decodeTriplets(pkt)
        print("Packet 26 DC = " + str(dc))
        for i in range (0, 12):
            x = tp[i] # self.getTriplet(i, pkt)
            data = (x >> 11) & 0x7f
            mode = (x >> 6) & 0x1f
            address = x & 0x3f
            if mode != 0x1f: # filter out termination marker
                print("Packet 26 triplet = " + str(i) + " data = " + hex(data) + " mode = " + hex(mode) + " address = " + str(address), end='')
            if address>=40 and address<=63: # It is a row address group
                modeStr = {
                    0x01: "Full row colour",
                    0x02: "Reserved",
                    0x03: "Reserved",
                    0x04: "Set Active Position",
                    0x05: "Reserved",
                    0x06: "Reserved",
                    0x07: "Address display row0",
                    0x08: "PDC Data - Country",
                    0x09: "PDC Data - Month and day",
                    0x0a: "PDC Data - Cursor row, start time",
                    0x0b: "PDC Data - Cursor row, end time",
                    0x0c: "PDC",
                    0x0d: "PDC",
                    0x0e: "Reserved",
                    0x0f: "Reserved",
                    0x12: "Adaptive Object Invocation",
                    0x19: "Reserved",
                    0x1a: "Reserved",
                    0x1b: "Reserved",
                    0x1c: "Reserved",
                    0x1d: "Reserved",
                    0x1e: "Reserved",
                    0x1f: "Termination marker",
                    }
            if address>=0 and address<=39: # It is a column address group
                modeStr = {
                    0x00: "Foreground colour",
                    0x01: "Block mosaic character G1",
                    0x02: "Smoothed mosaic G3",
                    0x03: "Background colour",
                    0x04: "Reserved",
                    0x05: "Reserved",
                    0x06: "PDC - Cursor column",
                    0x07: "Additional flash functions",
                    0x08: "Modified G0/G2 character set",
                    0x09: "Character from G0 set (2.5, 3.5)",
                    0x0a: "Reserved",
                    0x0b: "Line drawing or smoothed mosaic G3 set (2.5, 3.5)",
                    0x0c: "Display attributes",
                    0x0d: "DRCS character invocation",
                    0x0e: "Font style",
                    0x0f: "Character from the G2 set",
                    0x10: "G0 character without diacritical mark",
                    0x11: "G0 character with diacritical mark",
                    0x12: "G0 character with diacritical mark",
                    0x13: "G0 character with diacritical mark",
                    0x14: "G0 character with diacritical mark",
                    0x15: "G0 character with diacritical mark",
                    0x16: "G0 character with diacritical mark",
                    0x17: "G0 character with diacritical mark",
                    0x18: "G0 character with diacritical mark",
                    0x19: "G0 character with diacritical mark",
                    0x1a: "G0 character with diacritical mark",
                    0x1b: "G0 character with diacritical mark",
                    0x1c: "G0 character with diacritical mark",
                    0x1d: "G0 character with diacritical mark",
                    0x1e: "G0 character with diacritical mark",
                    0x1f: "G0 character with diacritical mark",
                    }
            if mode == 0x1f: # A termination marker, nothing more to come
                return 
            print (" mode = " + modeStr.get(mode, hex(mode)))
            if address>=40 and address<=63: # It is a row address group
                # @todo Modes between 0 and 0x1f
#When data field D6 and D5 are both set to '0', bits D4 - D0 define the background
#colour. Bits D4 and D3 select a CLUT in the Colour Map of table 30, and bits D2 -
#D0 select an entry from that CLUT. All other data field values are reserved.
#The effect of this attribute persists to the end of a display row unless overridden
#by either a spacing or a non-spacing attribute defining the background colour.
                if mode == 0x04: # Set Active Position
                    self.rowAddr = address - 40
                    if data<40:
                        self.colAddr = data
                    # print("rowAddr = " + str(self.rowAddr))
            if address>=0 and address<=39: # It is a column address group
                # @todo Modes between 0 and 0x1f
                if mode == 0x03: #Background colour
                    if (data & 0x60) == 0:
                        clut = (data >> 3) & 0x03
                        ix = data & 0x07
                        print ("set background colour at (" + str(self.rowAddr) + ", " + str(self.colAddr) + ") to " + str(clut) + "[" + str(ix) +']')
                if mode & 0x10 and mode != 0x1f: # G0 character with diacritical mark
                    self.colAddr = address
                    dia = int(mode & 0x0f)
                    mapChar = tuple((self.rowAddr, self.colAddr, dia))
                    self.lines.addMapping(mapChar)
                    # print("mapChar = " + str(mapChar[0]) + " " + str(mapChar[1]) + " " + str(mapChar[2]) + " ")
                    
    # Set a flag to clear down when starting the next page                    
    def clear(self):
        self.lines.clear()
