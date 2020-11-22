# ttxpage.py.
#
# VBIT Stream renderer. Teletext page level.
# You can modify this to run full frame
# or a smaller window
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

from tkinter import Tk
from ttxline import TTXline

class TTXpage:
    print("TTXPage created")
    def __init__(self):
        self.root = Tk()

        self.width_value=self.root.winfo_screenwidth() # full screen
        self.height_value=self.root.winfo_screenheight()

        #self.width_value = 768 # not full screen
        #self.height_value=576
        self.root.configure(background='black', borderwidth=0, highlightthickness=0)
        self.root.geometry("%dx%d+0+0" % (self.width_value, self.height_value))

        # Make it full screen (Comment it out if you want to run in a window)
        self.root.wm_attributes('-fullscreen','true')

        self.root.wait_visibility(self.root)

        # lines
        self.lines = TTXline(self.root)
        self.lines.text.pack()

        self.root.update_idletasks()
        self.root.update()
        
        self.mag=[None] * 4
        self.page=[None] * 4
        
        self.root.bind('<KeyPress>', self.onKeyPress)
        
        self.buffer = []
        
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
    
    def printRow(self, packet, row):
        if row < 0 or row > 24 :
            return
        self.lines.printRow(packet, row)

    def printHeader(self, packet, page, seeking):
        self.lines.printHeader(packet, page, seeking)

    # Actually draw the stuff
    def mainLoop(self):
        self.root.update_idletasks()
        self.root.update()
        
    def toggleReveal(self):
        self.lines.toggleReveal()
        
    # decode packet 27 fastext links
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
        
    def decodeTriplet(self, b1, b2, b3): # ETS: Page 22, section 8.3
        #b1 = self.reverse(b1)
        #b2 = self.reverse(b2)
        #b3 = self.reverse(b3)
        # Don't care about errors. Just remove the hamming bits
        c1 = (b1 & 0x04) >> 2 | (b1 & 0x70) >> 3 # .XXX.X..
        c2 = (b2 & 0x7f) << 8-4 # 4..10
        c3 = (b3 & 0x7f) << 16-5 # 11..17
        
        result = c1 | c2 | c3
        print ("c1 =" + hex(c1) + " c2 =" + hex(c2) + " c3 =" + hex(c3) + " " + hex(result))
        
        
        return result
  
    def reverse(self, x): # reverse the bit order in a byte
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
    
    def decodeRow28(self, pkt):
        # All I really want is the regional set number. See table 4
        dc = self.deham(pkt[3])
        
        self.dumpPacket(pkt)
        x = self.decodeTriplet(pkt[3],pkt[4],pkt[5])
        # We should validate this! It is only correct in X/28/0 format 1
        # region number is bits 11 to 14. Regions are listed in Table 32
        # @TODO This only decode the region code that VBIT2 puts out.
        # There is a a huge amount more in X/28.
        self.region = (x >> 10) & 0x0f
        print("Packet 28 DC = " + str(dc) + " " + hex(x) + " region = " + str(self.region))
        self.lines.region = self.region # National option


