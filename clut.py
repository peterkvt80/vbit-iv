# clut.py.
#
# clut.py Teletext colour lookup table
# Maintains colour lookups
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

# This holds the colour lookup tables read in by packet 28 etc.
# I think we have four CLUTs 0 to 3. Here is what the standard says:
## 8 background full intensity colours:
## Magenta, Cyan, White. Black, Red, Green, Yellow, Blue,
## 7 foreground full intensity colours:
## Cyan, White. Red, Green, Yellow, Blue, Magenta,
## Invoked as spacing attributes via codes in packets X/0 to X/25.
## Black foreground: Invoked as a spacing attribute via codes in packets X/0
## to X/25.
## 32 colours per page. The Colour Map contains four CLUTs
## (numbered 0 - 3), each of 8 entries. Each entry has a four bit resolution for
## the RGB components, subclause 12.4.
## Presentation
## Level
## 1 1.5 2.5 3.5
## { { ~ ~
## ~ ~ ~ ~
## { { ~ ~
## { { ~ ~
## Colour Definition
## CLUT 0 defaults to the full intensity colours used as spacing colour
## attributes at Levels 1 and 1.5.
## CLUT 1, entry 0 is defined to be transparent. CLUT 1, entries 1 to 7 default
## to half intensity versions of CLUT 0, entries 1 to 7.
## CLUTs 2 and 3 have the default values specified in subclause 12.4. CLUTs
## 2 and 3 can be defined for a particular page by packet X/28/0 Format 1, or
## for all pages in magazine M by packet M/29/0.
## Colour Selection
## CLUT 0, entries 1 to 7 are selectable directly by the Level 1 data as
## spacing attributes. CLUTs 0 to 3 are selectable via packets 26 or objects
## as non-spacing attributes.
## The foreground and background colour codes on the Level 1 page may be
## used to select colours from other parts of the Colour Map. Different CLUTs
## may be selected for both foreground and background colours.
## This mapping information is transmitted in packet X/28/0 Format 1 for the
## associated page and in packet M/29/0 for all pages in magazine M.
## With the exception of entry 0 in CLUT 1 (transparent), CLUTs 0 and 1 can
## be redefined for a particular page by packet X/28/4, or
##

class Clut:
    def __init__(self):
        print ("Clut loaded")
        self.clut0 = [0] * 8 # Default full intensity colours
        self.clut1 = [0] * 8 # default half intensity colours
        self.clut2 = [0] * 8
        self.clut3 = [0] * 8
        # set defaults
        self.reset()
    
    # Used by X26/0 to swap entire cluts
    # @param colour - Colour index 0..7
    # @param remap - Remap 0..7
    # @param foreground - True for foreground coilour, or False for background
    # @return - Colour string for tkinter. eg. 'black' or '#000'
    def RemapColourTable(self, colourIndex, remap, foreground):
        clutIndex = 0
        if foreground:
            if remap>4:
                clutIndex = 2
            elif remap<3:
                clutIndex = 0
            else:
                clutIndex = 1
        else: # background
            if remap < 3:
                clutIndex = remap
            elif remap == 3 or remap == 5:
                clutIndex = 1
            elif remap == 4 or remap == 6:
                clutIndex = 2
            else:
                clutIndex = 3
        return self.get_value(clutIndex, colourIndex)
        
    
    def reset(self): # To values from table 12.4
        # CLUT 0 full intensity
        self.clut0[0] = '#000' # black
        self.clut0[1] = '#f00' # red
        self.clut0[2] = '#0f0' # green
        self.clut0[3] = '#ff0' # yellow
        self.clut0[4] = '#00f' # blue
        self.clut0[5] = '#f0f' # magenta
        self.clut0[6] = '#0ff' # cyan
        self.clut0[7] = '#fff' # white
    
        # CLUT 1 half intensity
        self.clut1[0] = '#000' # transparent
        self.clut1[1] = '#700' # half red
        self.clut1[2] = '#070' # half green
        self.clut1[3] = '#770' # half yellow
        self.clut1[4] = '#007' # half blue
        self.clut1[5] = '#707' # half magenta
        self.clut1[6] = '#077' # half cyan
        self.clut1[7] = '#777' # half white

        # CLUT 2 lovely colours
        self.clut2[0] = '#f05' # crimsonish
        self.clut2[1] = '#f70' # orangish
        self.clut2[2] = '#0f7' # blueish green
        self.clut2[3] = '#ffb' # pale yellow
        self.clut2[4] = '#0ca' # cyanish
        self.clut2[5] = '#500' # dark red
        self.clut2[6] = '#652' # hint of a tint of runny poo
        self.clut2[7] = '#c77' # gammon

        # CLUT 3 more lovely colours
        self.clut3[0] = '#333' # pastel black
        self.clut3[1] = '#f77' # pastel red
        self.clut3[2] = '#7f7' # pastel green
        self.clut3[3] = '#ff7' # pastel yellow
        self.clut3[4] = '#77f' # pastel blue
        self.clut3[5] = '#f7f' # pastel magenta
        self.clut3[6] = '#7ff' # pastel cyan
        self.clut3[7] = '#ddd' # pastel white

        
    # set a value in a particular clut
    # Get the colour from a particular clut
    # Probably want to record which cluts are selected
    # Lots of stuff
    
    # @param colour - 12 bit web colour string eg. '#1ab'
    # @param clut_index CLUT index 0 to 3
    # @param clr_index - 0..7 colour index
    def set_value(self, colour, clut_index, clr_index):
        clr_index = clr_index % 8 # need to trap this a bit better. This is masking a problem
        clut_index = clut_index % 4
        if clut_index==0:
            self.clut0[clr_index] = colour;
        if clut_index==1:
            self.clut1[clr_index] = colour;
        if clut_index==2:
            self.clut2[clr_index] = colour;
        if clut_index==3:
            self.clut3[clr_index] = colour;
        print("clut value: clut" + str(clut_index) + " set[" + str(clr_index) + '] = ' + colour)
        
    # @return colour - 12 bit web colour string eg. '#1ab'
    # @param clut_index CLUT index 0 to 3
    # @param clr_index - 0..7 colour index
    def get_value(self, clut_index, clr_index):
        clut_index = clut_index % 4
        clr_index = clr_index % 8
        if clut_index == 0:
            return self.clut0[clr_index]
        if clut_index == 1:
            return self.clut1[clr_index]
        if clut_index == 2:
            return self.clut2[clr_index]
        if clut_index == 3:
            return self.clut3[clr_index]
        return 0 # just in case!
        
    # debug dump the clut contents
    def dump(self):
        print("[Dump] CLUT values")
        for i in range(8):
            print(self.clut0[i] + ', ', end='')
        print()
        for i in range(8):
            print(self.clut1[i] + ', ', end='')
        print()
        for i in range(8):
            print(self.clut2[i] + ', ', end='')
        print()
        for i in range(8):
            print(self.clut3[i] + ', ', end='')
        print()
        
clut = Clut()
