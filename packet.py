# packet.py Teletext packet decoder
# Takes a T42 packet and decodes whatever it can.
#
# Copyright (c) 2020, 2021 Peter Kwan
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
    DEFAULT_ROW_COLOUR = "#000"
    def __init__(self):
        self.clear()
        return
    
    # reset all meta-data to the defaults
    def clear(self):
        self.region = 0
        self.X26CharMappings = []  # diacriticals
        # X28/0 settings
        self.ChangeColour = [] # background colour replacement
        self.RowColour = []  # tuple(row 0..24 , clut number 0..3, colour index 0..7)
        self.BlackBackgroundColourSubstitution = False
        self.ColourTableRemapping=0 # clut swap 
        self.leftSidePanel = True # These should default to False for level 1
        self.rightSidePanel = True

        # X/28/0 format 1: character set designations (7-bit each: region(4) + language(3))
        self.defaultCharSet = None
        self.defaultCharSetRegion = None
        self.defaultCharSetLanguage = None
        self.secondCharSet = None
        self.secondCharSetRegion = None
        self.secondCharSetLanguage = None

        # X/28/0 format 1: screen colour remapping (triplet 13 fields)
        self.defaultScreenColour = None  # 5-bit
        self.defaultRowColour28 = None   # 5-bit (name avoids clashing with rowColour() method)

        clut.reset()

    def mapColourFg(self, row, column, colour):
        return self.mapColour(row, column, colour, True)

    def mapColourBg(self, row, column, colour):
        return self.mapColour(row, column, colour, False)
    
    # X26/0 full colour row
    # @param row - Row number to check
    # @return - The colour value for that row, or black if there is none
    def rowColour(self, row: int) -> str:
        for entry in self.RowColour:
            entry_row = entry[0]  # row
            applies_to_following_rows = entry[3]  # if set, then all rows from here are coloured

            is_applicable = (entry_row == row) or (applies_to_following_rows and row > entry_row)
            if not is_applicable:
                continue

            clut_index = entry[1]  # clut
            colour_index = entry[2]  # index
            return clut.get_value(clut_index, colour_index)

        return self.DEFAULT_ROW_COLOUR  # default row to black

    
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
                #print('[mapColour] ' + str(i))
                #print('[mapColour matched] row, col = ' + str(row) + ', ' + str(column) + ' fg = ' + str(isFg))
                #print ("[mapColour matched] clut[ix] " + str(i[2]) + '[' + str(i[3])+ ']')
                colour = clut.get_value(i[2], i[3])
                #print('[mapColour matched] colour = ' + colour)
                return colour # found and replaced
        return 'x'
        
    
    # decode a packet. Returns the packet type or 0 if it is not X/26, X28, X29
    # @param pkt - T42 packet
    # @param row - Packet number
    def decode(self, pkt, row):
        print("[Packet::decode] " + str(row) + " ************************************ Enters")
        dc = self.deham(pkt[2]) # designation code
        
        if dc == 0 and row == 27:
            decodeLinks(pkt)

        if (dc == 0 or dc == 4) and row == 28:
            #self.dumpPacket(pkt) # debug
            self.decodeX280Format1(pkt)
            return

        print("[Packet::decode] Not implemented")

    def decodeX280Format1(self, pkt): # X/28/0 format 1. p32 table 4
        """
        Decodes the X/28/0 format 1 packet and extracts its components for processing.
        """
        global clut
        dc = self.deham(pkt[2]) # 0 = CLUT 2/3, 4 = CLUT 0/1
        print("[Packet::decodeX280Format1] Packet X/28/" + str(dc)+ " format 1")

        triplets = self.decodeTriplets(pkt) # decode all the triplets

        def reverse_language_bits_7bit(value: int) -> int:
            """
            Match the C++ behaviour: swap language b0 and b2, keep region bits and language b1.
            Language bits are the low 3 bits of the 7-bit value.
            """
            value &= 0x7f
            a = value & 0x7a  # keep everything except language b0 (0x01) and b2 (0x04)
            if value & 0x01:
                a |= 0x04
            if value & 0x04:
                a |= 0x01
            return a & 0x7f

        def split_charset_7bit(value: int) -> tuple[int, int]:
            value &= 0x7f
            region = (value >> 3) & 0x0f
            language = value & 0x07
            return region, language

        # Triplet 1 (triplets[0]) fields (match C++ bit layout)
        t1 = triplets[0]
        pageFunction = t1 & 0x0f
        pageCoding = (t1 >> 4) & 0x07

        default_charset_raw = (t1 >> 7) & 0x7f
        default_charset = reverse_language_bits_7bit(default_charset_raw)

        self.defaultCharSet = default_charset
        self.defaultCharSetRegion, self.defaultCharSetLanguage = split_charset_7bit(default_charset)

        # Keep Packet.region aligned with the default character set's region nibble
        self.region = self.defaultCharSetRegion

        print(
            "[Packet::decodeX280Format1] function="
            + str(pageFunction)
            + " coding="
            + str(pageCoding)
        )
        print(
            "[Packet::decodeX280Format1] defaultCharSet(raw)="
            + str(default_charset_raw)
            + " defaultCharSet="
            + str(self.defaultCharSet)
            + " (region="
            + str(self.defaultCharSetRegion)
            + ", language="
            + str(self.defaultCharSetLanguage)
            + ")"
        )

        # Second character set: t1 bits 15..18 plus t2 bits 1..3 (match C++)
        t2 = triplets[1]
        second_charset_raw = (((t1 >> 14) & 0x0f) | ((t2 & 0x07) << 4)) & 0x7f
        second_charset = reverse_language_bits_7bit(second_charset_raw)

        self.secondCharSet = second_charset
        self.secondCharSetRegion, self.secondCharSetLanguage = split_charset_7bit(second_charset)

        # Side panel flags and columns (fix precedence + match C++ extraction)
        self.leftSidePanel = (t2 & 0x08) > 0
        self.rightSidePanel = (t2 & 0x10) > 0
        sidePanelStatus = (t2 & 0x20) > 0  # Level 3.5 only
        leftColumns = (t2 >> 6) & 0x0f     # t2, 7..10

        print(
            "* secondCharSet(raw)="
            + str(second_charset_raw)
            + " secondCharSet="
            + str(self.secondCharSet)
            + " (region="
            + str(self.secondCharSetRegion)
            + ", language="
            + str(self.secondCharSetLanguage)
            + ") leftPanel="
            + str(self.leftSidePanel)
            + " rightPanel="
            + str(self.rightSidePanel)
        )
        print("* sidePanelStatus = " + str(sidePanelStatus) + " leftColumns = " + str(leftColumns))

        # the rest is colour, 16 lots of 4 bit RGB
        bit_index = 10
        triplet_start = 1
        colour = 0
        for i in range(16 * 3): # Sixteen R, G, B values
            start_bit = (i * 4) + bit_index
            triplet_index = triplet_start + int(start_bit / 18)
            start_bit = start_bit % 18
            colour_index = int(i/3)

            colour_value = i % 3 # RGB
            clut_ix = 1
            if i < (8 * 3):
                clut_ix = 0
            if dc == 0:
                clut_ix = clut_ix + 2

            t = triplets[triplet_index]
            t = (t >> start_bit) & 0x0f
            if start_bit > 14:
                split = 18 - start_bit
                t = t << split
                t2b = triplets[triplet_index+1] & 0x03
                t = t | t2b

            colour = colour | (t << ((2-colour_value) * 4))
            if colour_value == 2:
                colourHex = '#' + f'{colour:03x}'
                clut.set_value(colourHex, clut_ix, colour_index)
                colour = 0

        # Triplet 13 (triplets[12]) screen colour remapping fields (match C++)
        t13 = triplets[12]
        self.defaultScreenColour = (t13 >> 4) & 0x1f   # bits 5..9
        self.defaultRowColour28 = (t13 >> 9) & 0x1f    # bits 10..14
        self.BlackBackgroundColourSubstitution = ((t13 >> 14) & 0x01) > 0  # bit 15
        self.ColourTableRemapping = (t13 >> 15) & 0x07 # bits 16..18

        print(
            "[Packet::decodeX280Format1] defaultScreenColour="
            + str(self.defaultScreenColour)
            + " defaultRowColour28="
            + str(self.defaultRowColour28)
            + " blackBgSub="
            + str(self.BlackBackgroundColourSubstitution)
            + " remap="
            + str(self.ColourTableRemapping)
        )
        print("[decodeX280Format1] EXITS")
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
        print("[Dump] ColourTableRemapping = " + str(self.ColourTableRemapping)) # Table 33
        
    # The clut is shared
    # Other metadata has access functions
    
    # The region code number
    def getRegion(self):
        return self.region
    
    ############## X/26 character mappings ###############
    def addMapping(self, mappedChar):
        #print('TRACE A')
        self.X26CharMappings.append(mappedChar)
        
    
metaData = Packet()