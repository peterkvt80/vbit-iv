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
# I think we have four CLUTs 0 to 3

class Clut:
    def __init__(self):
        print ("Clut loaded")
        self.clut0 = [0] * 8
        # set defaults
        self.reset()
    
    def reset(self):
        self.clut0[0] = '#000' # black
        self.clut0[1] = '#f00' # red
        self.clut0[2] = '#0f0' # green
        self.clut0[3] = '#ff0' # yellow
        self.clut0[4] = '#00f' # blue
        self.clut0[5] = '#f0f' # magenta
        self.clut0[6] = '#0ff' # cyan
        self.clut0[7] = '#fff' # white

        
    # set a value in a particular clut
    # Get the colour from a particular clut
    # Probably want to record which cluts are selected
    # Lots of stuff
    
    # @param colour - 12 bit web colour string eg. '#1ab'
    # @param clr_index - 0..7 colour index
    # @todo Need to implement and address CLUTs 0 to 3
    def set_value(self, colour, clr_index):
        if clr_index>7:
            clr_index = clr_index % 8 # need to trap this a bit better. This is masking a problem
        self.clut0[clr_index] = colour;
        print("clut value set. YAY!")
        
clut = Clut()
