# Mapper
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
#
# Maps characters to according to region and group to the glyph in teletext2.ttf 

# \param c : character to map
# \param option : national option number 0..7
# \param group : group number
def mapchar(c, option, group):
    if group==0:
        return mapgroup0(c, option)
    return '¬'

def mapgroup0(c, option):
    if option==0:
        return mapEN(c)
    if option==1:
        print('French')
        return mapFR(c)
    print("Unknown language group 0, nat. option = " + str(option))
    return mapEN(c)

def mapEN(c): # English
    mapper = { 
        '#': '£',
        '[': chr(0x2190), # 5/B Left arrow.
        '\\':chr(0xbd),  # 5/C Half
        ']': chr(0x2192), # 5/D Right arrow.
        '^': chr(0x2191), # 5/E Up arrow.
        '_': chr(0x0023), # 5/F Underscore is hash sign
        '`': chr(0x2014), # 6/0 Centre dash. The full width dash e731
        '{': chr(0xbc),   # 7/B Quarter
        '|': chr(0x2016), # 7/C Double pipe
        '}': chr(0xbe),   # 7/D Three quarters
        '~': chr(0x00f7), # 7/E Divide 
        chr(0x7f): chr(0xe65f) # 7/F Bullet (rectangle block)
    }      
    return mapper.get(c, c)
    
def mapFR(c): # French Nat. Opt. 1
    mapper = { 
        '#':  chr(0x00e9), # 2/3 e acute
        '$':  chr(0x00ef), # 2/4 i umlaut
        '@':  chr(0x00e0), # 4/0 a grave
        '[':  chr(0x00eb), # 5/B e umlaut
        '\\': chr(0x00ea), # 5/C e circumflex
        # Nat. opt. 2
        ']':  chr(0x00f9), # 5/D u grave
        '^':  chr(0x00ee), # 5/E i circumflex
        '_':  '#',         # 5/F #
        '`':  chr(0x00e8), # 6/0 e grave
        '{':  chr(0x00e2), # 7/B a circumflex
        '|':  chr(0x00f4), # 7/C o circumflex
        '}':  chr(0x00fb), # 7/D u circumflex
        '~':  chr(0x00e7) # 7/E c cedilla
    }

    return mapper.get(c, c)
