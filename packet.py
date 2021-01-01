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
from mapper import getdiacritical, MapLatinG2

# This doesn't want to be packets centred, it is pages meta data.
# In other words:
# Packets are analysed here.
# Data decoded from the packets may be retrieved but not specific data about the packets themselves
class Packet:
    def __init__(self):
        self.region = 0
        print('C')
        self.X26CharMappings = [] # diacriticals
        self.ChangeColour = [] # background colour replacement
        return
    
    # reset all meta-data to the defaults
    def clear(self):
        print('D')
        self.region = 0
        self.X26CharMappings = []        
        self.ChangeColour = []
        clut.reset()
        self.clearX26()
        
    def mapColourFg(self, row, column, colour):
        return self.mapColour(row, column, colour, True)
        
    def mapColourBg(self, row, column, colour):
        return self.mapColour(row, column, colour, False)
        
    # If there is an X26/0 mapped colour, return it
    # @row - Row index of a spacing attribute
    # @column - Column index of a spacing attribute
    # @IsFg - True if the colour we are looking for is a foreground colour
    # @return The colour mapped at the address    
    def mapColour(self, row, column, colour, isFg):
        # print("[packet::mapColour] entered. row = " + str(row) + " col = " + str(column) + " clr= " + str(colour) )
        # look through the ChangeColour list to find if we have a matched address
        for i in self.ChangeColour: # [row, column, clutIx, colourIx, isFg]
            r = i[0]
            c = i[1]
            fg = i[4]
            #print ("[mapColour] r = " + str(r))
            #print ("[mapColour] c = " + str(c))
            #print ("[mapColour] i[0]" + str(i[0]))
            # If the address matches and the foreground or background type matches
            if (row - 1) == r and column == c and fg == isFg:
                print('[mapColour] ' + str(i))
                print('[mapColour matched] row, col = ' + str(row) + ', ' + str(column) + ' fg = ' + str(isFg))
                print ("[mapColour matched] clut[ix] " + str(i[2]) + '[' + str(i[3])+ ']')
                colour = clut.get_value(i[2], i[3])
                print('[mapColour matched] colour = ' + colour)
                return colour # found and replaced
        return colour # Not found, don't change
        
    
    # decode a packet. Returns the packet type or 0 if it is not X/26, X28, X29
    # @param pkt - T42 packet
    # @param row - Packet number
    def decode(self, pkt, row):
        print("[Packet::decode] " + str(row) + " ************************************ Enters")
        dc = self.deham(pkt[2]) # designation code
        
        if (dc == 0 or dc == 4) and row == 28:
            #self.dumpPacket(pkt) # debug
            self.decodeX280Format1(pkt)
            return
        if row == 26:
            print("[decode] packet 26 dc = " + str(dc))#self.dumpPacket(pkt) # debug
            self.decodeX260(pkt)
            return
        
        print("[Packet::decode] Not implemented X/" + str(row) + "/ dc = " + str(dc))
            
        print("[Packet::decode] *************************** exits")
        
    def decodeX280Format1(self, pkt): # X/28/0 format 1. p32 table 4
        # "Default G0 primary and G2 supplementary character sets plus national option character
        # sub-sets are designated. The 7-bit value is used to select an entry in table 32."
        global clut
        dc = self.deham(pkt[2]) # 0 = CLUT 2/3, 4 = CLUT 0/1
        print("[Packet::decodeX280Format1] Packet X/28/" + str(dc)+ " format 1")
        
        # @todo "Where packets 28/0 and 28/4 are both transmitted as part of a page, packet 28/0 takes precedence over
        # 28/4 for all but the colour map entry coding."
        
        triplets = self.decodeTriplets(pkt) # decode all the triplets
        # self.printTriplets(triplets) # debug

        # Decode everything and decide if we want to do anything with it later
        t = triplets[0]
        function = t & 0x0f # 
        coding = (t > 4) & 0x07 # page coding (7 bits + parity)
        G0G2 = (t >> 8) & 0x7f # The lowest three bits are don't care

        self.region = (t >> 10) & 0x0f # This is the RE region number in tti files.
        
        print ("[Packet::decodeX280Format1] region = " + str(self.region))        
        secondG0 = ((t >> 14) & 0x0f) << 3 # 7 bit value defined in table 33. 
        t = triplets[1]
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
        # for i in range(16 * 3):
        for i in range(16 * 3): # @todo Should be 16 for the two palettes
            # work out the indices
            start_bit = (i * 4) + bit_index
            triplet_index = triplet_start + int(start_bit / 18)
            start_bit = start_bit % 18            
            colour_index = int(i/3) # CLUT 0/1 for dc == 4
            
            colour_value = i % 3 # RGB
            clut_ix = 1 #clut 0/1 where dc = 4
            if i < (8 * 3):
                clut_ix = 0
            if dc == 0: # CLUT 2/3 for dc == 0
                clut_ix = clut_ix + 2 
            # extract the 4 bit colour value
            t =  triplets[triplet_index] # Get the triplet
            #print("[decodeX280Format1] triplet = " + hex(t))
            t = (t >> start_bit) & 0x0f # Shift and mask
            #print("[decodeX280Format1] masked = " + hex(t))
            # does the data cross a triplet boundary?
            if start_bit > 14:                
                split = 18 - start_bit # This is always 2! Could assert that
                t = t << split
                t2 = triplets[triplet_index+1] & 0x03 # Triplets only ever break on two bits
                t = t | t2

                # print("split = " + str(split))
            
            
            #print("[decodeX280Format1] i = " + str(i) + " colour = " + str(colour_index) + "(" + str(colour_value) + ") triplet = " + str(triplet_index) + " start_bit = " + str(start_bit) + " Colour = " + hex(t))
            colour = colour | t <<  ((2-colour_value) * 4)
            #print("[decodeX280Format1]"+hex(t)+" ",end='')
            if colour_value == 2: # Done an RGB value
                colourHex = '#' + f'{colour:03x}' # This is the colour in 12 bit web hex format
                clut.set_value(colourHex, clut_ix, colour_index)
                #print("[decodeX280Format1] colour = " + hex(colour) +", colourHex = " + colourHex )
                colour = 0
        print("[decodeX280Format1] EXITS")
        
    def decodeX260(self, pkt):
        print("[decodeX260] ENTERS")
        
        # There is a lot of stuff in X26, diacriticals, colours, side panels ...
        tp =  self.decodeTriplets(pkt)
        dc = self.deham(pkt[2]) # 0  

        print("[decodeX260] dc = " + str(dc))
        for i in range (0, 13):
            x = tp[i] # self.getTriplet(i, pkt)
            data = (x >> 11) & 0x7f
            mode = (x >> 6) & 0x1f
            address = x & 0x3f
            if mode != 0x1f: # filter out termination marker
                print("[decodeX260] Packet 26 triplet = " + str(i) + " data = " + hex(data) + " address = " + str(address), end='')
            if address>=40 and address<=63: # It is a row address group. TABLE 27.
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
            print (" tuple("+str(i)+") mode(" + hex(mode) + ") = " + modeStr.get(mode, hex(mode)))
            if address>=40 and address<=63: # It is a row address group
                # @todo Modes between 0 and 0x1f
#When data field D6 and D5 are both set to '0', bits D4 - D0 define the background
#colour. Bits D4 and D3 select a CLUT in the Colour Map of table 30, and bits D2 -
#D0 select an entry from that CLUT. All other data field values are reserved.
#The effect of this attribute persists to the end of a display row unless overridden
#by either a spacing or a non-spacing attribute defining the background colour.
                if mode == 0x04: # Set Active Position
                    self.rowAddr = address - 40
                    if data<40: # level >= 2.5
                        self.colAddr = data
                    # print("rowAddr = " + str(self.rowAddr))
            if address>=0 and address<=39: # It is a column address group
                # @todo Modes between 0 and 0x1f
                if mode == 0x00: #Foreground colour
                    if (data & 0x60) == 0:
                        clutIndex = (data >> 3) & 0x03 # Which CLUT?
                        colourIndex = data & 0x07 # Which colour in the CLUT?
                        print ("[decodeX260] set foreground colour at (" + str(self.rowAddr) + ", " + str(address) + ") to " + str(clutIndex) + "[" + str(colourIndex) +']')
                        fgCol = [self.rowAddr, address, clutIndex, colourIndex, True]
                        self.ChangeColour.append(fgCol)
                if mode == 0x01: # Block Mosaic Character from the G1 Set. Page 90
                    # @todo Probably needs to take into account contiguous/separated
                    ch = data & 0x7f
                    if ch >= 0x20 and ch < 0x40:
                        ch = ch + 0xe680 - 0x20
                    if ch >= 0x60 and ch < 0x80:
                        ch = ch + 0xe6a0 - 0x60
                    mapChar = tuple((self.rowAddr, address, ch))                    
                    self.addMapping(mapChar)
                if mode == 0x03: # Background colour
                    if (data & 0x60) == 0:
                        clutIndex = (data >> 3) & 0x03 # Which CLUT?
                        colourIndex = data & 0x07 # Which colour in the CLUT?
                        print ("[decodeX260] set background colour at (" + str(self.rowAddr) + ", " + str(address) + ") to " + str(clutIndex) + "[" + str(colourIndex) +']')
                        bgCol = [self.rowAddr, address, clutIndex, colourIndex, False]
                        self.ChangeColour.append(bgCol)
                if mode == 0x09: # Character from G0 set (2.5, 3.5)
                    #print('[decodeX260: mode 9] place character ' + hex(data) + " at (" + str(address) +", " + str(self.rowAddr) + ")")
                    mapChar = tuple((self.rowAddr, address, data))
                    self.addMapping(mapChar)
                if mode == 0x0f: # Character from the G2 Supplementary Set. Page 94
                    g2char = MapLatinG2(data)
                    mapChar = tuple((self.rowAddr, address, g2char))
                    self.addMapping(mapChar)                   
                if mode == 0x10: # Character from G0 set (2.5, 3.5)
                    print('[decodeX260: mode 10] place character ' + hex(data) + " at (" + str(address) +", " + str(self.rowAddr) + ")")
                    mapChar = tuple((self.rowAddr, address, ord('?')))
                    self.addMapping(mapChar)
                if mode > 0x10 and mode <= 0x1f: # G0 character with diacritical mark
                    self.colAddr = address
                    dia = int(mode & 0x0f)
                    # mapChar = tuple((self.rowAddr, self.colAddr, dia))
                    mapChar = tuple((self.rowAddr, self.colAddr, ord(getdiacritical(chr(data), dia)) ))
                    # need to re-implement this
                    self.addMapping(mapChar)
                    print("[mapChar] = " + str(mapChar[0]) + " " + str(mapChar[1]) + " " + str(mapChar[2]) + " ")

        
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
        c2 = (b2 & 0x7f) << (8-4) # 4..10
        c3 = (b3 & 0x7f) << (16-5) # 11..17
        
        result = c1 | c2 | c3
        #print ("b1 =" + hex(b1) + " b2 =" + hex(b2) + " b3 =" + hex(b3))                
        #sprint ("c1 =" + hex(c1) + " c2 =" + hex(c2) + " c3 =" + hex(c3) + " " + hex(result))                
        return result
    
    # decode triplet in X/26 etc.
    # \param ix Triplet number 0 to 12
    def getTriplet(self, ix, pkt):
        i = (ix * 3) + 3
        return self.decodeTriplet(pkt[i] & 0x7f, pkt[i+1] & 0x7f, pkt[i+2] & 0x7f)
    
    # debug
    def printTriplets(self, tr):
        print("[debug] Triplet = ", end = '')
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

    # dump a packet as hex
    def dumpPacket(self, pkt):
        # print('Dump: ' + f'{pkt[0]:02x}' + ' ' + f'{pkt[1]:02x}')
        print([f'{pkt[i]:02x}' for i in range(0, 42)])
        
    # dump ALL the metadata in one handy chunk
    def dump(self):
        print("[Dump] Region = " + str(self.region))
        clut.dump()
        print("[Dump] diacritical count = " + str(len(self.X26CharMappings)))
        
    # The clut is shared
    # Other metadata has access functions
    
    # The region code number
    def getRegion(self):
        return self.region
    
    ############## X/26 character mappings ###############
    def addMapping(self, mappedChar):
        #print('TRACE A')
        self.X26CharMappings.append(mappedChar)
        
    # Clear any X26 mappings
    def clearX26(self):
        #print('TRACE B')
        self.X26CharMappings = []        
    
metaData = Packet()