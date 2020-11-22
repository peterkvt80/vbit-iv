# Mapper
#
# Copyright (c),2020 Peter Kwan
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
# \param region : region number
def mapchar(c, option, region):
    if region==0: # West Europe
        return mapregion0(c, option)
    if region==1: # West Europe plus Polish
        return mapregion1(c, option)
    if region==2: # West Europe plus Turkish
        return mapregion2(c, option)
    if region==3: # East Europe
        return mapregion3(c, option)
    if region==4: # Russia
        return mapregion4(c, option)
    if region==6: # Russia
        return mapregion6(c, option) # turk + greek
    print("Unimplemented region code " + str(region))
    return '¬'

def mapregion0(c, option): # West Europe
    if option==0:
        return mapEN(c)
    if option==1:
        return mapFR(c)
    if option==2:
        return mapSE(c)
    if option==3:
        return mapCZ(c)
    if option==4:
        return mapDE(c)
    if option==5:
        return mapES(c)
    if option==6:
        return mapIT(c)
    if option==7:
        return mapEN(c) # spare
    print("Unknown language region 0, nat. option = " + str(option))
    return mapEN(c)

def mapregion1(c, option): # West Europe
    if option==0:
        return mapPL(c)
    if option==1:
        return mapFR(c)
    if option==2:
        return mapSE(c)
    if option==3:
        return mapCZ(c)
    if option==4:
        return mapDE(c)
    if option==5:
        return mapPL(c) # spare
    if option==6:
        return mapIT(c)
    if option==7:
        return mapPL(c) # spare
    print("Unknown language region 1, nat. option = " + str(option))
    return mapEN(c)

def mapregion2(c, option): # West Europe plus turkish
    if option==0:
        return mapEN(c)
    if option==1:
        return mapFR(c)
    if option==2:
        return mapSE(c)
    if option==3:
        return mapTR(c) # Turkish
    if option==4:
        return mapDE(c)
    if option==5:
        return mapES(c)
    if option==6:
        return mapIT(c)
    if option==7:
        return mapEN(c) # spare
    print("Unknown language region 2, nat. option = " + str(option))
    return mapEN(c)

def mapregion3(c, option): # East Europe
    if option==0:
        return mapEN(c) # spare
    if option==1:
        return mapFR(c) # spare
    if option==2:
        return mapSE(c) # spare
    if option==3:
        return mapTR(c) # spare
    if option==4:
        return mapDE(c) # spare
    if option==5:
        return mapRS(c) # serbian/croatian/slovenian
    if option==6:
        return mapEN(c) # spare
    if option==7:
        return mapRO(c) # romanian
    print("Unknown language region 3, nat. option = " + str(option))
    return mapEN(c)

def mapregion4(c, option): # Russia/Bulgaria
    if option==0:
        return mapRS(c) # serbian
    if option==1:
        return mapRU(c) # russian
    if option==2:
        return mapEE(c) # estonian (Same as czech/slovak)
    if option==3:
        return mapCZ(c) # czechia/slovak
    if option==4:
        return mapDE(c) # german
    if option==5:
        return mapUA(c) # ukrainian
    if option==6:
        return mapLV(c) # lettish(latvian)/lithuanian (latin)
    if option==7:
        return mapEN(c) # spare
    print("Unknown language region 4, nat. option = " + str(option))
    return mapEN(c)

def mapregion6(c, option): # Turkish-3/Greek-7
    if option==3:
        return mapTR(c) # turkish
    if option==7:
        return mapGR(c) # greek
    print("Unknown language region 6, nat. option = " + str(option))
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
        '~':  chr(0x00e7), # 7/E c cedilla
    }
    return mapper.get(c, c)

def mapSE(c): # Swedish Nat. Opt. 2, group 0
    mapper = { 
        # '#':  '#', # 2/3 hash not mapped
        '$':  chr(0x00a4), # 2/4 currency bug
        '@':  chr(0x00c9), # 4/0 E acute
        '[':  chr(0x00c4), # 5/B A umlaut
        '\\': chr(0x00d4), # 5/C O umlaut
        # Nat. opt. 2
        ']':  chr(0x00c5), # 5/D A ring
        '^':  chr(0x00dc), # 5/E U umlaut
        '_':  chr(0x005f), # 5/F Underscore (not mapped)
        '`':  chr(0x00e9), # 6/0 e acute
        '{':  chr(0x00e4), # 7/B a umlaut
        '|':  chr(0x00d6), # 7/C o umlaut
        '}':  chr(0x00e5), # 7/D a ring
        '~':  chr(0x00fc), # 7/E u umlaut
    }
    return mapper.get(c, c)

def mapCZ(c): # Czech/Slovak Nat. Opt. 3, group 0
    mapper = { 
        # '#': '#' # 2/3 hash
        '$': chr(0x016f),# 2/4 u ring
        '@': chr(0x010d),# 4/0 c caron
        '[': chr(0x0165),# 5/B t caron
        '\\': chr(0x017e),# 5/C z caron
        # Nat. opt. 2
        ']': chr(0x00fd),# 5/D y acute
        '^': chr(0x00ed),# 5/E i acute
        '_': chr(0x0159),# 5/F r caron
        '`': chr(0x00e9),# 6/0 e acute
        '{': chr(0x00e1),# 7/B a acute
        '|': chr(0x011b),# 7/C e caron
        '}': chr(0x00fa),# 7/D u acute
        '~': chr(0x0161)# 7/E s caron
    }
    return mapper.get(c, c)
    
    
def mapDE(c): # German Nat. Opt. 4, group 0
    mapper = { 
        # '#': '#' # 2/3 # is not mapped
        '$': chr(0x0024),# 2/4 Dollar sign not mapped
        '@': chr(0x00a7),# 4/0 Section sign
        '[': chr(0x00c4),# 5/B A umlaut
        '\\': chr(0x00d6),# 5/C O umlaut
        # Nat. opt. 2
        ']': chr(0x00dc),# 5/D U umlaut
        #'^': '^',# 5/E Caret (not mapped)
        '_': chr(0x005f),# 5/F Underscore (not mapped)
        '`': chr(0x00b0),# 6/0 Masculine ordinal indicator
        '{': chr(0x00e4),# 7/B a umlaut
        '|': chr(0x00f6),# 7/C o umlaut
        '}': chr(0x00fc),# 7/D u umlaut
        '~': chr(0x00df)# 7/E SS
    }
    return mapper.get(c, c)

def mapES(c): # Spanish/Portuguese Nat. Opt. 5, group 0
    mapper = { 
        '#': chr(0x00e7),# 2/3 c cedilla
        # '$': '$' # 2/4 Dollar sign not mapped
        '@': chr(0x00a1),# 4/0 inverted exclamation mark
        '[': chr(0x00e1),# 5/B a acute
        '\\': chr(0x00e9),# 5/C e acute
        # Nat. opt. 2
        ']': chr(0x00ed),# 5/D i acute
        '^': chr(0x00f3),# 5/E o acute
        '_': chr(0x00fa),# 5/F u acute
        '`': chr(0x00bf),# 6/0 Inverted question mark
        '{': chr(0x00fc),# 7/B u umlaut
        '|': chr(0x00f1),# 7/C n tilde
        '}': chr(0x00e8),# 7/D e grave
        '~': chr(0x00e0)# 7/E a grave
    }
    return mapper.get(c, c)

def mapIT(c): # Italian Nat. Opt. 6, group 0
    mapper = { 
        '#': chr(0x00a3),# 2/3 Pound
        # '$': '$' # 2/4 Dollar sign not mapped
        '@': chr(0x00e9),# 4/0 e acute
        '[': chr(0x00b0),# 5/B ring
        '\\': chr(0x00e7),# 5/C c cedilla
        # Nat. opt. 2
        ']': chr(0x2192),# 5/D right arrow
        '^': chr(0x2191),# 5/E up arrow
        '_': '#', # 5/F hash
        '`': chr(0x00f9),# 6/0 u grave
        '{': chr(0x00e0),# 7/B a grave
        '|': chr(0x00f2),# 7/C o grave
        '}': chr(0x00e8),# 7/D e grave
        '~': chr(0x00ec)# 7/E i grave
    }
    return mapper.get(c, c)

def mapPL(c): # Polish Nat. Opt. 6, region 1#
    mapper = { 
        #'#': chr(0x0023), # 2/3 # is not mapped
        '$': chr(0x0144), # 2/4 - n acute
        '@': chr(0x0105), # 4/0 - a ogonek
        '[': chr(0x01b5), # 5/B - z stroke
        "\\": chr(0x015a), # 5/C - S acute
        ']': chr(0x0141), # 5/D - L stroke
        '^': chr(0x0107), # 5/E - c acute
        '_': chr(0x00f3), # 5/F - o acute
        '`': chr(0x0119), # 6/0 - e ogonek
        '{': chr(0x017c), # 7/B - s overdot
        '|': chr(0x015b), # 7/C - s acute
        '}': chr(0x0142), # 7/D - I stroke
        '~': chr(0x017a) # 7/E - z acute
    }
    return mapper.get(c, c)

def mapTR(c): # Turkish Nat. Opt. 2, region 3
    mapper = { 
        '#': chr(0x0167), # 2/3
        '$': chr(0x011f), # 2/4
        '@': chr(0x0130), # 4/0
        '[': chr(0x015e), # 5/B
        '\\': chr(0x00d6), # 5/C
        ']': chr(0x00c7), # 5/D
        '^': chr(0x00dc), # 5/E
        '_': chr(0x011e), # 5/F
        '`': chr(0x0131), # 6/0
        '{': chr(0x015f), # 7/B
        '|': chr(0x00f6), # 7/C
        '}': chr(0x00e7), # 7/D
        '~': chr(0x00fc) # 7/E
    }
    return mapper.get(c, c)

def mapRS(c): # Latin G0 Set - Option 2 Serbian/Croatian/Slovenian Nat. Opt. 2, region 3
    mapper = { 
        '#': chr(0x0023), # 2/3
        '$': chr(0x00cb), # 2/4
        '@': chr(0x010c), # 4/0
        '[': chr(0x0106), # 5/B
        '\\': chr(0x017d), # 5/C
        ']': chr(0x0110), # 5/D
        '^': chr(0x0160), # 5/E
        '_': chr(0x00eb), # 5/F
        '`': chr(0x010d), # 6/0
        '{': chr(0x0107), # 7/B
        '|': chr(0x017e), # 7/C
        '}': chr(0x0111), # 7/D
        '~': chr(0x0161) # 7/E
    }
    return mapper.get(c, c)

def mapRO(c): # Latin G0 Set - Option 7 Romanian Nat. Opt. 2, region 3
    mapper = { 
        '#': chr(0x0023), # 2/3
        '$': chr(0x00a4), # 2/4
        '@': chr(0x0162), # 4/0
        '[': chr(0x00c2), # 5/B
        '\\': chr(0x015e), # 5/C
        ']': chr(0x0102), # 5/D
        '^': chr(0x00ce), # 5/E
        '_': chr(0x0131), # 5/F
        '`': chr(0x0163), # 6/0
        '{': chr(0x00e2), # 7/B
        '|': chr(0x015f), # 7/C
        '}': chr(0x0103), # 7/D
        '~': chr(0x00ee) # 7/E
    }
    return mapper.get(c, c)

# region 4
def mapRU(c): # Cyrillic G0 Set - Option 2 Russian/Bulgarian, region 4
    mapper = { 
        # Not sure this is all correct
        # Nat. opt. 2. Column 40-4f
        '@': chr(0x042e),    # Cyrillic Capital Letter Yu
        'C': chr(0x0426), # Cyrillic
        'D': chr(0x0414), #
        'E': chr(0x0415),
        'F': chr(0x0424),
        'G': chr(0x0413), #
        'H': chr(0x0425), #
        # Cyrillic G0 Column 50-5f
        'Q': chr(0x042f),
        'R': chr(0x0420),
        'S': chr(0x0421),
        'T': chr(0x0422),
        'U': chr(0x0423),
        'V': chr(0x0416),
        'W': chr(0x0412),
        'X': chr(0x042c),
        'Y': chr(0x042a),
        'Z': chr(0x0417),
        '[': chr(0x0428), # Nap opt 2 starts here
        '\\': chr(0x042d),
        ']': chr(0x0429),
        '^': chr(0x0427),
        '_': chr(0x042b),
        # Cyrillic G0 Column 60-6f
        '`': chr(0x044e), # Nat opt 2 stops here
        # 'a': chr(0x0430),
        # 'b': chr(0x0431),
        'c': chr(0x0446),
        'd': chr(0x0434),
        'e': chr(0x0435),
        'f': chr(0x0444),
        'g': chr(0x0433),
        'h': chr(0x0445),
        'i': chr(0x0438),
        'j': chr(0x0439),
        # Remaining are OK
        # Cyrillic G0 Column 70-7f
        # 70 is OK
        'q': chr(0x044f),
        'r': chr(0x0440),
        's': chr(0x0441),
        't': chr(0x0442),
        'u': chr(0x0443),
        'v': chr(0x0436),
        'w': chr(0x0432),
        'x': chr(0x044c),
        'y': chr(0x044a),
        'z': chr(0x0437),
        '{': chr(0x0448),
        '|': chr(0x044d),
        '}': chr(0x0449),
        '~': chr(0x0447)
        # Remaining are OK
        }
    return mapper.get(c, c)


def mapEE(c): # Latin G0 Set - Option 2 Estonian, region 4
    return mapCZ(c)


def mapUA(c): # Ukrainian (Cyrillic), region 4
    mapper = { 
        # Nat. opt. 2. Column 40-4f
        '@': chr(0x042e),    # Cyrillic Capital Letter Yu
        'C': chr(0x0426), # Cyrillic
        'D': chr(0x0414), #
        'E': chr(0x0415),
        'F': chr(0x0424),
        'G': chr(0x0413), #
        'H': chr(0x0425), #
        # Cyrillic G0 Column 50-5f
        'Q': chr(0x042f), # 5/1
        'R': chr(0x0420), # 5/2
        'S': chr(0x0421),
        'T': chr(0x0422),
        'U': chr(0x0423),
        'V': chr(0x0416),
        'W': chr(0x0412),
        'X': chr(0x042c),
        'Y': chr(0x0406), # 5/8 042a russian
        'Z': chr(0x0417), # 5/9
        '[': chr(0x0428), # Nat opt 2 starts here
        '\\': chr(0x0404), # 5/c Russian 042d
        ']': chr(0x0429), # 5/d
        '^': chr(0x0427), # 5/e
        '_': chr(0x0407), # 5/f russian 042b
        # Cyrillic G0 Column 60-6f
        '`': chr(0x044e), # 6/0
        # 'a': chr(0x0430), # 6/1
        # 'b': chr(0x0431),
        'c': chr(0x0446),
        'd': chr(0x0434),
        'e': chr(0x0435),
        'f': chr(0x0444),
        'g': chr(0x0433),
        'h': chr(0x0445),
        'i': chr(0x0438),
        'j': chr(0x0439),
        # Remaining are OK
        # Cyrillic G0 Column 70-7f
        'p': chr(0x006e), # 7/0 Use lower case n for Ukrainian
        'q': chr(0x044f), # 7/1
        'r': chr(0x0440), # 7/2
        's': chr(0x0441), # 7/3
        't': chr(0x0442), # 7/4
        'u': chr(0x0443), # 7/5
        'v': chr(0x0436), # 7/6
        'w': chr(0x0432), # 7/7
        'x': chr(0x044c), # 7/8
        'y': chr(0x0456), # 7/9 russian 044a
        'z': chr(0x0437), # 7/a
        '{': chr(0x0448), # 7/b
        '|': chr(0x0454), # 7/c russian 044d
        '}': chr(0x0449), # 7/d
        '~': chr(0x0447) # 7/e russian 0447
        # Remaining are OK
    }
    return mapper.get(c, c)

def mapLV(c): # Lettish/Lithuanian (Latin) region 4, option 6
    mapper = { 
        '#': chr(0x0023), # 2/3
        '$': chr(0x0024), # 2/4
        '@': chr(0x0160), # 4/0
        '[': chr(0x0117), # 5/B
        '\\': chr(0x0229), # 5/C
        ']': chr(0x017d), # 5/D
        '^': chr(0x010d), # 5/E
        '_': chr(0x016b), # 5/F
        '`': chr(0x0161), # 6/0
        '{': chr(0x0105), # 7/B
        '|': chr(0x0173), # 7/C
        '}': chr(0x017e), # 7/D
        '~': chr(0x012f) # 7/E This is the best match in teletext2
    }
    return mapper.get(c, c)

def mapGR(c): # Greek region 6, option 7
    if c=='R':
        return chr(0x0374); # Top right dot thingy
    if c>='@' and c<='~':
        return chr(ord(c)+0x390-ord('@'))
    if c=='<':
        return chr(0x00ab) # left chevron
    if c=='>':
        return chr(0x00bb) # right chevron
    return c
    