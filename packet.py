# ttxpage.py.
#
# packet.py Teletext packet decoder
# Takes a T42 packet and decodes whatever it can.
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
# packet decoding is a bit over complicated. Let's put it all here so we know
# where to look

from clut import clut, Clut

class Packet:
    def __init__(self):
        self.dc = 0 # designation code
        self.triplets = []
        return
    
    # decode a packet. Returns the packet type or 0 if it is not X/26, X28, X29
    # @param pkt - T42 packet
    # @param row - Packet number
    def decode(self, pkt, row):
        print("[Packet::decode] ************************************ Enters")
        self.dc = self.deham(pkt[2])
        self.triplets = self.decodeTriplets(pkt)
        self.printTriplets(self.triplets)
#                function = x & 0x0f # Page function. (0 = basic level 1 page)
 #       encoding= (x >> 4) & 0x07 # Page encoding (0 = 7 bit odd parity)
        # what sort of packet have we got?
        x = self.triplets[0]
        function = x & 0x0f # Page function. (0 = basic level 1 page)
        encoding= (x >> 4) & 0x07 # Page encoding (0 = 7 bit odd parity)
        
        if self.dc == 0 and row ==28:
            self.decodeX280Format1()
        else:
            print("Packet: Not implemented dc = " + str(self.dc))
            
        print("[Packet::decode] dc = " + str(self.dc) + " function = " + str(function) + " encoding = " + str(encoding))
        
        print("[Packet::decode] *************************** exits")
        
    def decodeX280Format1(self): # X/28/0 format 1. p32 table 4
        global clut
        print("* Packet X/28/0 format 1")
        # Decode everything and decide if we want to do anything with it later
        t = self.triplets[0]
        function = t & 0x0f # 
        coding = (t > 4) & 0x07 # page coding (7 bits + parity)
        G0G2 = (t >> 8) & 0x7f
        secondG0 = ((t >> 14) & 0x0f) << 3 # 7 bit value defined in table 33. 
        t = self.triplets[1]
        secondG0 = secondG0 | t & 0x07
        leftSidePanel = t & 0x08 > 0
        rightSidePanel = t & 0x10 > 0
        print("* coding = "+ str(coding) + " secondG0 = " + str(secondG0) + " leftPanel = " + str(leftSidePanel) + " rightPanel = " + str(rightSidePanel))
        sidePanelStatus = t & 0x20 > 0 # Level 3.5 only
        sidePanelColumns = t & 0x1c >> 6 # Number of columns in side panels
        print("* sidePanelStatus = " + str(sidePanelStatus) + " sidePanelColumns = " + str(sidePanelColumns))
        # the rest is colour, 16 lots of 4 bit RGB
        bit_index = 10
        triplet_start = 1
        colour = 0
        for i in range(16 * 3):
            # work out the indices
            start_bit = (i * 4) + bit_index
            triplet_index = triplet_start + int(start_bit / 18)
            start_bit =start_bit % 18            
            colour_index = int(i/3) # CLUT
            colour_value = i % 3 # RGB
            # extract the 4 bit colour value
            t =  self.triplets[triplet_index] # Get the triplet
            t = (t >> start_bit) & 0x0f # Shift and mask
            # does the data cross a triplet boundary?
            if start_bit > 14:                
                split = 18 - start_bit # This is always 2! Could assert that
                t = t << split
                t2 = self.triplets[triplet_index+1] & 0x03 # Triplets only ever break on two bits
                t = t | t2
                # print("split = " + str(split))
            
            
            #print("i = " + str(i) + " colour = " + str(colour_index) + "(" + str(colour_value) + ") triplet = " + str(triplet_index) + " start_bit = " + str(start_bit) + " Colour = " + hex(t))
            colour = colour * 0x10 + t
            print(hex(t)+" ",end='')
            if colour_value == 2: # Done an RGB value
                colourHex = '#' + f'{colour:03x}' # This is the colour in 12 bit web hex format
                clut.set_value(colourHex, colour_index)
                print(" colour = " + hex(colour) +", colourHex = " + colourHex )
                colour = 0
                    
        
    # Really need to make a better version of deham
    # @param 8 bit number to deham
    # @return 4 bit dehammed alue
    def deham(self, value):
        # Deham with NO checking! @todo Parity and error correction
        b0 = (value & 0x02) >> 1
        b1 = (value & 0x08) >> 2
        b2 = (value & 0x20) >> 3
        b3 = (value & 0x80) >> 4
        return b0+b1+b2+b3
    
    def decodeTriplet(self, b1, b2, b3): # ETS: Page 22, section 8.3
        #b1 = self.reverse(b1)
        #b2 = self.reverse(b2)
        #b3 = self.reverse(b3)
        # Don't care about errors. Just remove the hamming bits
        c1 = (b1 & 0x04) >> 2 | (b1 & 0x70) >> 3 # .XXX.X..
        c2 = (b2 & 0x7f) << 8-4 # 4..10
        c3 = (b3 & 0x7f) << 16-5 # 11..17
        
        result = c1 | c2 | c3
        # print ("c1 =" + hex(c1) + " c2 =" + hex(c2) + " c3 =" + hex(c3) + " " + hex(result))                
        return result
    
    # decode triplet in X/26 etc.
    # \param ix Triplet number 0 to 12
    def getTriplet(self, ix, pkt):
        i = (ix * 3) + 3
        return self.decodeTriplet(pkt[i], pkt[i+1], pkt[i+2])
    
    def printTriplets(self, tr):
        print("Triplet = ", end = '')
        for t in range(13):
            print(hex(tr[t]) + ' ', end = '')
        print()

    # @param pkt - An XX26/28.29 packet
    # @return - Array of 13 numbers, the decoded triplets
    def decodeTriplets(self, pkt):
        arr = []
        for i in range(13):
            arr.append( self.getTriplet(i, pkt) )
        return arr    
    
