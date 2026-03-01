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

DEFAULT_FALLBACK_CHAR = "¬"

def _warn_unknown(msg: str) -> None:
    print(msg)

def _map_by_option(c, option: int, region_number: int, option_map, default_mapper):
    mapper_fn = option_map.get(option)
    if mapper_fn is None:
        _warn_unknown(f"Unknown language region {region_number}, nat. option = {option}")
        mapper_fn = default_mapper
    return mapper_fn(c)

# --- extracted per-language maps (constants) ---

_EN_MAP = {
    "#": "£",
    "[": chr(0x2190),        # 5/B Left arrow.
    "\\": chr(0x00BD),       # 5/C Half
    "]": chr(0x2192),        # 5/D Right arrow.
    "^": chr(0x2191),        # 5/E Up arrow.
    "_": chr(0x0023),        # 5/F Underscore is hash sign
    "`": chr(0x2014),        # 6/0 Centre dash.
    "{": chr(0x00BC),        # 7/B Quarter
    "|": chr(0x2016),        # 7/C Double pipe
    "}": chr(0x00BE),        # 7/D Three quarters
    "~": chr(0x00F7),        # 7/E Divide
    chr(0x7F): chr(0xE65F),  # 7/F Bullet (rectangle block)
}

_FR_MAP = {
    "#": chr(0x00E9),
    "$": chr(0x00EF),
    "@": chr(0x00E0),
    "[": chr(0x00EB),
    "\\": chr(0x00EA),
    "]": chr(0x00F9),
    "^": chr(0x00EE),
    "_": "#",
    "`": chr(0x00E8),
    "{": chr(0x00E2),
    "|": chr(0x00F4),
    "}": chr(0x00FB),
    "~": chr(0x00E7),
}

_SE_MAP = {
    "$": chr(0x00A4),
    "@": chr(0x00C9),
    "[": chr(0x00C4),
    "\\": chr(0x00D6),
    "]": chr(0x00C5),
    "^": chr(0x00DC),
    "_": chr(0x005F),
    "`": chr(0x00E9),
    "{": chr(0x00E4),
    "|": chr(0x00F6),
    "}": chr(0x00E5),
    "~": chr(0x00FC),
}

_CZ_MAP = {
    "$": chr(0x016F),
    "@": chr(0x010D),
    "[": chr(0x0165),
    "\\": chr(0x017E),
    "]": chr(0x00FD),
    "^": chr(0x00ED),
    "_": chr(0x0159),
    "`": chr(0x00E9),
    "{": chr(0x00E1),
    "|": chr(0x011B),
    "}": chr(0x00FA),
    "~": chr(0x0161),
}

_DE_MAP = {
    "$": chr(0x0024),
    "@": chr(0x00A7),
    "[": chr(0x00C4),
    "\\": chr(0x00D6),
    "]": chr(0x00DC),
    "_": chr(0x005F),
    "`": chr(0x00B0),
    "{": chr(0x00E4),
    "|": chr(0x00F6),
    "}": chr(0x00FC),
    "~": chr(0x00DF),
}

_ES_MAP = {
    "#": chr(0x00E7),
    "@": chr(0x00A1),
    "[": chr(0x00E1),
    "\\": chr(0x00E9),
    "]": chr(0x00ED),
    "^": chr(0x00F3),
    "_": chr(0x00FA),
    "`": chr(0x00BF),
    "{": chr(0x00FC),
    "|": chr(0x00F1),
    "}": chr(0x00E8),
    "~": chr(0x00E0),
}

_IT_MAP = {
    "#": chr(0x00A3),
    "@": chr(0x00E9),
    "[": chr(0x00B0),
    "\\": chr(0x00E7),
    "]": chr(0x2192),
    "^": chr(0x2191),
    "_": "#",
    "`": chr(0x00F9),
    "{": chr(0x00E0),
    "|": chr(0x00F2),
    "}": chr(0x00E8),
    "~": chr(0x00EC),
}

_PL_MAP = {
    "$": chr(0x0144),
    "@": chr(0x0105),
    "[": chr(0x01B5),
    "\\": chr(0x015A),
    "]": chr(0x0141),
    "^": chr(0x0107),
    "_": chr(0x00F3),
    "`": chr(0x0119),
    "{": chr(0x017C),
    "|": chr(0x015B),
    "}": chr(0x0142),
    "~": chr(0x017A),
}

_TR_MAP = {
    "#": chr(0x0167),
    "$": chr(0x011F),
    "@": chr(0x0130),
    "[": chr(0x015E),
    "\\": chr(0x00D6),
    "]": chr(0x00C7),
    "^": chr(0x00DC),
    "_": chr(0x011E),
    "`": chr(0x0131),
    "{": chr(0x015F),
    "|": chr(0x00F6),
    "}": chr(0x00E7),
    "~": chr(0x00FC),
}

_RS_MAP = {
    "#": chr(0x0023),
    "$": chr(0x00CB),
    "@": chr(0x010C),
    "[": chr(0x0106),
    "\\": chr(0x017D),
    "]": chr(0x0110),
    "^": chr(0x0160),
    "_": chr(0x00EB),
    "`": chr(0x010D),
    "{": chr(0x0107),
    "|": chr(0x017E),
    "}": chr(0x0111),
    "~": chr(0x0161),
}

_RO_MAP = {
    "#": chr(0x0023),
    "$": chr(0x00A4),
    "@": chr(0x0162),
    "[": chr(0x00C2),
    "\\": chr(0x015E),
    "]": chr(0x0102),
    "^": chr(0x00CE),
    "_": chr(0x0131),
    "`": chr(0x0163),
    "{": chr(0x00E2),
    "|": chr(0x015F),
    "}": chr(0x0103),
    "~": chr(0x00EE),
}

_RU_MAP = {
    "@": chr(0x042E),
    "C": chr(0x0426),
    "D": chr(0x0414),
    "E": chr(0x0415),
    "F": chr(0x0424),
    "G": chr(0x0413),
    "H": chr(0x0425),
    "Q": chr(0x042F),
    "R": chr(0x0420),
    "S": chr(0x0421),
    "T": chr(0x0422),
    "U": chr(0x0423),
    "V": chr(0x0416),
    "W": chr(0x0412),
    "X": chr(0x042C),
    "Y": chr(0x042A),
    "Z": chr(0x0417),
    "[": chr(0x0428),
    "\\": chr(0x042D),
    "]": chr(0x0429),
    "^": chr(0x0427),
    "_": chr(0x042B),
    "`": chr(0x044E),
    "c": chr(0x0446),
    "d": chr(0x0434),
    "e": chr(0x0435),
    "f": chr(0x0444),
    "g": chr(0x0433),
    "h": chr(0x0445),
    "i": chr(0x0438),
    "j": chr(0x0439),
    "q": chr(0x044F),
    "r": chr(0x0440),
    "s": chr(0x0441),
    "t": chr(0x0442),
    "u": chr(0x0443),
    "v": chr(0x0436),
    "w": chr(0x0432),
    "x": chr(0x044C),
    "y": chr(0x044A),
    "z": chr(0x0437),
    "{": chr(0x0448),
    "|": chr(0x044D),
    "}": chr(0x0449),
    "~": chr(0x0447),
}

_UA_MAP = {
    "@": chr(0x042E),
    "C": chr(0x0426),
    "D": chr(0x0414),
    "E": chr(0x0415),
    "F": chr(0x0424),
    "G": chr(0x0413),
    "H": chr(0x0425),
    "Q": chr(0x042F),
    "R": chr(0x0420),
    "S": chr(0x0421),
    "T": chr(0x0422),
    "U": chr(0x0423),
    "V": chr(0x0416),
    "W": chr(0x0412),
    "X": chr(0x042C),
    "Y": chr(0x0406),
    "Z": chr(0x0417),
    "[": chr(0x0428),
    "\\": chr(0x0404),
    "]": chr(0x0429),
    "^": chr(0x0427),
    "_": chr(0x0407),
    "`": chr(0x044E),
    "c": chr(0x0446),
    "d": chr(0x0434),
    "e": chr(0x0435),
    "f": chr(0x0444),
    "g": chr(0x0433),
    "h": chr(0x0445),
    "i": chr(0x0438),
    "j": chr(0x0439),
    "p": chr(0x006E),
    "q": chr(0x044F),
    "r": chr(0x0440),
    "s": chr(0x0441),
    "t": chr(0x0442),
    "u": chr(0x0443),
    "v": chr(0x0436),
    "w": chr(0x0432),
    "x": chr(0x044C),
    "y": chr(0x0456),
    "z": chr(0x0437),
    "{": chr(0x0448),
    "|": chr(0x0454),
    "}": chr(0x0449),
    "~": chr(0x0447),
}

_LV_MAP = {
    "#": chr(0x0023),
    "$": chr(0x0024),
    "@": chr(0x0160),
    "[": chr(0x0117),
    "\\": chr(0x0229),
    "]": chr(0x017D),
    "^": chr(0x010D),
    "_": chr(0x016B),
    "`": chr(0x0161),
    "{": chr(0x0105),
    "|": chr(0x0173),
    "}": chr(0x017E),
    "~": chr(0x012F),
}

_HE_SYMBOL_MAP = {
    "#": chr(0x00A3),
    "[": chr(0x2190),
    "\\": chr(0x00BD),
    "]": chr(0x2192),
    "^": chr(0x2191),
    "_": chr(0x0023),
    "{": chr(0x20AA),
    "|": chr(0x2016),
    "}": chr(0x00BE),
    "~": chr(0x00F7),
}

# --- language mapping functions (now tiny + consistent) ---

def mapEN(c):  # English
    return _EN_MAP.get(c, c)

def mapFR(c):  # French Nat. Opt. 1
    return _FR_MAP.get(c, c)

def mapSE(c):  # Swedish Nat. Opt. 2, group 0
    return _SE_MAP.get(c, c)

def mapCZ(c):  # Czech/Slovak Nat. Opt. 3, group 0
    return _CZ_MAP.get(c, c)

def mapDE(c):  # German Nat. Opt. 4, group 0
    return _DE_MAP.get(c, c)

def mapES(c):  # Spanish/Portuguese Nat. Opt. 5, group 0
    return _ES_MAP.get(c, c)

def mapIT(c):  # Italian Nat. Opt. 6, group 0
    return _IT_MAP.get(c, c)

def mapPL(c):  # Polish Nat. Opt. 6, region 1
    return _PL_MAP.get(c, c)

def mapTR(c):  # Turkish Nat. Opt. 2, region 3
    return _TR_MAP.get(c, c)

def mapRS(c):  # Serbian/Croatian/Slovenian, region 3
    return _RS_MAP.get(c, c)

def mapRO(c):  # Romanian, region 3
    return _RO_MAP.get(c, c)

def mapRU(c):  # Cyrillic Russian/Bulgarian, region 4
    return _RU_MAP.get(c, c)

def mapEE(c):  # Estonian, region 4
    return mapCZ(c)

def mapUA(c):  # Ukrainian, region 4
    return _UA_MAP.get(c, c)

def mapLV(c):  # Lettish/Lithuanian (Latin), region 4
    return _LV_MAP.get(c, c)

def mapGR(c):  # Greek region 6, option 7
    if c == "R":
        return chr(0x0374)  # Top right dot thingy
    if "@" <= c <= "~":
        return chr(ord(c) + 0x390 - ord("@"))
    if c == "<":
        return chr(0x00AB)  # left chevron
    if c == ">":
        return chr(0x00BB)  # right chevron
    return c

def mapAR(c):  # Arabic region 8, option 7
    if c == ">":
        return "<"  # 3/c
    if c == "<":
        return ">"  # 3/e
    return chr(ord(c) + 0xE606 - ord("&"))  # 2/6 onwards

def mapHE(c):  # Hebrew region 10, option 5
    oc = ord(c)
    if 0x5F < oc < 0x7B:  # Hebrew characters
        return chr(oc + 0x05D0 - 0x60)
    return _HE_SYMBOL_MAP.get(c, c)

# --- option dispatch tables (defined after functions they reference) ---

_REGION0_OPTIONS = {0: mapEN, 1: mapFR, 2: mapSE, 3: mapCZ, 4: mapDE, 5: mapES, 6: mapIT, 7: mapEN}
_REGION1_OPTIONS = {0: mapPL, 1: mapFR, 2: mapSE, 3: mapCZ, 4: mapDE, 5: mapPL, 6: mapIT, 7: mapPL}
_REGION2_OPTIONS = {0: mapEN, 1: mapFR, 2: mapSE, 3: mapTR, 4: mapDE, 5: mapES, 6: mapIT, 7: mapEN}
_REGION3_OPTIONS = {0: mapEN, 1: mapFR, 2: mapSE, 3: mapTR, 4: mapDE, 5: mapRS, 6: mapEN, 7: mapRO}
_REGION4_OPTIONS = {0: mapRU, 1: mapRU, 2: mapEE, 3: mapCZ, 4: mapDE, 5: mapUA, 6: mapLV, 7: mapEN}
_REGION6_OPTIONS = {3: mapTR, 7: mapGR}
_REGION8_OPTIONS = {0: mapEN, 1: mapFR, 7: mapAR}
_REGION10_OPTIONS = {5: mapHE, 7: mapAR}

# --- region mapping (now small wrappers) ---

def mapregion0(c, option):  # West Europe
    return _map_by_option(c, option, 0, _REGION0_OPTIONS, mapEN)

def mapregion1(c, option):  # West Europe plus Polish
    return _map_by_option(c, option, 1, _REGION1_OPTIONS, mapEN)

def mapregion2(c, option):  # West Europe plus Turkish
    return _map_by_option(c, option, 2, _REGION2_OPTIONS, mapEN)

def mapregion3(c, option):  # East Europe
    return _map_by_option(c, option, 3, _REGION3_OPTIONS, mapEN)

def mapregion4(c, option):  # Russia/Bulgaria
    print("Region 4 option = " + str(option))
    return _map_by_option(c, option, 4, _REGION4_OPTIONS, mapEN)

def mapregion6(c, option):  # Turkish-3/Greek-7
    return _map_by_option(c, option, 6, _REGION6_OPTIONS, mapEN)

def mapregion8(c, option):  # Arabic
    return _map_by_option(c, option, 8, _REGION8_OPTIONS, mapEN)

def mapregion10(c, option):  # Arabic
    return _map_by_option(c, option, 10, _REGION10_OPTIONS, mapEN)

_REGION_DISPATCH = {
    0: mapregion0,
    1: mapregion1,
    2: mapregion2,
    3: mapregion3,
    4: mapregion4,
    6: mapregion6,    # turk + greek
    8: mapregion8,
    10: mapregion10,  # @todo G0/G2
}

# Public API (kept name to avoid breaking imports)
def mapchar(c, option, region):
    region_mapper = _REGION_DISPATCH.get(region)
    if region_mapper is None:
        _warn_unknown("Unimplemented region code " + str(region))
        return DEFAULT_FALLBACK_CHAR
    return region_mapper(c, option)



# @param ch - character to map
# @param diacritical to add (if possible) 0..15 from row 0x40 of Latin G2
# NOTE. This is now split. Characters are looked up during reading the page by getdiacritical
# mapdiacritical is now only used to render the character
def mapdiacritical(ch, row, col, diacritical):
    # print("[mapdiacritical] diacriticals on this page = " + str(len(diacritical)))
    for i in range(0, len(diacritical)):
        d = diacritical[i]
        if row==d[0] and col==d[1] : # match character location
            return chr(d[2]) # This is the correct character
    return ch # None found

# Page 95: Characters Including Diacritical Marks
# @param ch - Character to add a diacritical to
# @param accent - accent to add to the character (from X26/0)
# @return The accented character from the teletext font
def getdiacritical(ch, accent):
    # print("[getdiacritical] get diacriticals
    if accent == 0: # grave
        if ch=='A':
            return chr(0xc0)
        if ch=='E':
            return chr(0xc8)
        if ch=='I':
            return chr(0xcc)
        if ch=='O':
            return chr(0xd2)
        if ch=='U':
            return chr(0xd9)
        if ch=='a':
            return chr(0xe0)
        if ch=='e':
            return chr(0xe8)
        if ch=='i':
            return chr(0xec)
        if ch=='o':
            return chr(0xf2)
        if ch=='u':
            return chr(0xf9)
        # Cyrillics go here
    if accent == 2: # acute
        if ch=='A':
            return chr(0xc1)
        if ch=='E':
            return chr(0xc9)
        if ch=='I':
            return chr(0xcd)
        if ch=='O':
            return chr(0xd3)
        if ch=='U':
            return chr(0xda)
        if ch=='Y':
            return chr(0xdd)
        if ch=='a':
            return chr(0xe1)
        if ch=='e':
            return chr(0xe9)
        if ch=='i':
            return chr(0xed)
        if ch=='o':
            return chr(0xf3)
        if ch=='u':
            return chr(0xfa)
        if ch=='y':
            return chr(0xfd)
        if ch=='C':
            return chr(0x106)
        if ch=='c':
            return chr(0x107)
        if ch=='c':
            return chr(0x139)
        if ch=='l':
            return chr(0x13a)
        if ch=='N':
            return chr(0x143)
        if ch=='n':
            return chr(0x144)
        if ch=='R':
            return chr(0x154)
        if ch=='r':
            return chr(0x155)
        if ch=='S':
            return chr(0x15a)
        if ch=='s':
            return chr(0x15b)
    if accent == 3: # circumflex
        if ch=='A':
            return chr(0xc2)
        if ch=='E':
            return chr(0xca)
        if ch=='I':
            return chr(0xce)
        if ch=='O':
            return chr(0xd4)
        if ch=='U':
            return chr(0xd8)
        if ch=='a':
            return chr(0xe2)
        if ch=='e':
            return chr(0xea)
        if ch=='i':
            return chr(0xee)
        if ch=='o':
            return chr(0xf4)
        if ch=='u':
            return chr(0xfb)
        if ch=='C':
            return chr(0x108)
        if ch=='c':
            return chr(0x109)
        if ch=='G':
            return chr(0x11c)
        if ch=='g':
            return chr(0x11d)
        if ch=='H':
            return chr(0x124)
        if ch=='h':
            return chr(0x125)
        if ch=='J':
            return chr(0x134)
        if ch=='j':
            return chr(0x135)
        if ch=='S':
            return chr(0x15c)
        if ch=='s':
            return chr(0x15d)
        if ch=='W':
            return chr(0x174)
        if ch=='w':
            return chr(0x175)
        if ch=='Y':
            return chr(0x176)
        if ch=='y':
            return chr(0x177)
        
    if accent == 4: # tilde ~
        if ch=='A':
            return chr(0xc3)
        if ch=='N':
            return chr(0xd1)
        if ch=='O':
            return chr(0xd5)
        if ch=='a':
            return chr(0xe3)
        if ch=='n':
            return chr(0xf1)
        if ch=='o':
            return chr(0xf5)
        if ch=='I':
            return chr(0x128)
        if ch=='i':
            return chr(0x129)
        if ch=='U':
            return chr(0x168)
        if ch=='u':
            return chr(0x169)

    if accent == 5: # macron (over line)
        if ch=='A':
            return chr(0x100)
        if ch=='a':
            return chr(0x101)
        if ch=='E':
            return chr(0x112)
        if ch=='e':
            return chr(0x113)
        if ch=='I':
            return chr(0x12a)
        if ch=='i':
            return chr(0x12b)
        if ch=='O':
            return chr(0x14c)
        if ch=='o':
            return chr(0x14d)
        if ch=='U':
            return chr(0x16a)
        if ch=='u':
            return chr(0x16b)

    if accent == 6: # breve
        if ch=='A':
            return chr(0x102)
        if ch=='a':
            return chr(0x103)
        if ch=='E':
            return chr(0x114)
        if ch=='e':
            return chr(0x115)
        if ch=='G':
            return chr(0x11e)
        if ch=='g':
            return chr(0x11f)
        if ch=='I':
            return chr(0x12c)
        if ch=='i':
            return chr(0x12d)
        if ch=='O':
            return chr(0x14e)
        if ch=='o':
            return chr(0x14f)

    if accent == 7: # dot above
        if ch=='C':
            return chr(0x10A)
        if ch=='c':
            return chr(0x10B)
        if ch=='E':
            return chr(0x116)
        if ch=='e':
            return chr(0x117)
        if ch=='G':
            return chr(0x120)
        if ch=='g':
            return chr(0x121)
        if ch=='I':
            return chr(0x130)
        if ch=='Z':
            return chr(0x17B)
        if ch=='z':
            return chr(0x17C)

    if accent == 8: # diaresis above
        if ch=='A':
            return chr(0xc4)
        if ch=='E':
            return chr(0xcb)
        if ch=='I':
            return chr(0xcf)
        if ch=='O':
            return chr(0xd6)
        if ch=='U':
            return chr(0xdc)
        if ch=='a':
            return chr(0xe4)
        if ch=='e':
            return chr(0xeb)
        if ch=='i':
            return chr(0xef)
        if ch=='o':
            return chr(0xf6)
        if ch=='u':
            return chr(0xfc)
        if ch=='y':
            return chr(0xff)

    #if accent == 9: # low acute
        
    if accent == 10: # Ring above (0x4a)
        if ch=='A':
            return chr(0xc5)
        if ch=='a':
            return chr(0xe5)
        if ch=='U':
            return chr(0x16e)
        if ch=='u':
            return chr(0x16f)
        
    if accent == 11: # Cedilla (0x4b)
        if ch=='C':
            return chr(0xc7)
        if ch=='c':
            return chr(0xe7)
        if ch=='G':
            return chr(0x122)
        if ch=='g':
            return chr(0x123)
        if ch=='K':
            return chr(0x136)
        if ch=='k':
            return chr(0x137)
        if ch=='L':
            return chr(0x13b)
        if ch=='l':
            return chr(0x13c)
        if ch=='N':
            return chr(0x145)
        if ch=='n':
            return chr(0x146)
        if ch=='R':
            return chr(0x156)
        if ch=='r':
            return chr(0x157)
        if ch=='S':
            return chr(0x15e)
        if ch=='s':
            return chr(0x15f)
        if ch=='T':
            return chr(0x162)
        if ch=='t':
            return chr(0x163)
        if ch=='e':
            return chr(0x229)
        
    # if accent == 12: # low macron

    if accent == 13: # double acute 0x4d
        if ch=='O':
            return chr(0x150)
        if ch=='o':
            return chr(0x104)
        if ch=='U':
            return chr(0x170)
        if ch=='u':
            return chr(0x171)

    if accent == 14: # ogonek 0x4e
        if ch=='A':
            return chr(0x104)
        if ch=='a':
            return chr(0x105)
        if ch=='E':
            return chr(0x118)
        if ch=='e':
            return chr(0x119)
        if ch=='I':
            return chr(0x12e)
        if ch=='i':
            return chr(0x12f)
        if ch=='U':
            return chr(0x172)
        if ch=='u':
            return chr(0x173)
        
    if accent == 15: # caron 0x4f
        if ch=='C':
            return chr(0x10c)
        if ch=='c':
            return chr(0x10d)
        if ch=='D':
            return chr(0x10e)
        if ch=='d':
            return chr(0x10f)
        if ch=='E':
            return chr(0x11a)
        if ch=='e':
            return chr(0x11b)
        if ch=='L':
            return chr(0x13d)
        if ch=='l':
            return chr(0x13e)
        if ch=='N':
            return chr(0x147)
        if ch=='n':
            return chr(0x148)
        if ch=='R':
            return chr(0x158)
        if ch=='r':
            return chr(0x159)
        if ch=='S':
            return chr(0x160)
        if ch=='s':
            return chr(0x161)
        if ch=='T':
            return chr(0x164)
        if ch=='t':
            return chr(0x165)
        if ch=='Z':
            return chr(0x17d)
        if ch=='z':
            return chr(0x17e)
        if ch=='A':
            return chr(0x1cd)
        if ch=='a':
            return chr(0x1ce)
    return ch # Not possible to accent, it was an X26 substituted character                    

# @param ch - character to convert to G2 (ordinal value)
# @return G2 mapping of the character number
def MapLatinG2(ch): # Page 116 Latin G2 Supplementary Set
    if ch <= 0x20 :
        return 0x20
    if ch==0x21: # inverted exclamation mark
        return 0xa1
    if ch==0x22: # cent
        return 0xa2
    if ch==0x23: # pound
        return 0xa3
    if ch==0x24: # dollar
        return 0x24
    if ch==0x25: # yen
        return 0xa5
    if ch==0x26: # hash
        return 0x23
    if ch==0x27: # section
        return 0xa7
    if ch==0x28: # currency
        return 0xa4
    if ch==0x29: # left single quote
        return 0x2018
    if ch==0x2a: # left double quote
        return 0x201c
    if ch==0x2b: # left pointing double angle quotation mark
        return 0xab
    if ch==0x2c: # left pointing arrow
        return 0x2190
    if ch==0x2d: # upwards arrow
        return 0x2191
    if ch==0x2e: # rightwards arrow
        return 0x2192
    if ch==0x2f: # downwards arrow
        return 0x2193
    # 30
    if ch==0x30: # degree
        return 0xb0
    if ch==0x31: # plus/minus
        return 0xb1
    if ch==0x32: # superscript 2
        return 0xb2
    if ch==0x33: # superscript 3
        return 0xb3
    if ch==0x78: # multiplication x
        return 0xd7
    if ch==0x35: # micro u
        return 0xb5
    if ch==0x36: # pilcrow
        return 0xb6
    if ch==0x37: # middle dot
        return 0xb7
    if ch==0x38: # division
        return 0xf7
    if ch==0x39: # right single quote
        return 0x2019
    if ch==0x3a: # right double quote
        return 0x201d
    if ch==0x3b: # right double angle quote 
        return 0xbb
    if ch==0x3c: # quarter
        return 0xbc
    if ch==0x3d: # half
        return 0xbd
    if ch==0x3e: # three quarter
        return 0xbe
    if ch==0x3f: # inverted question mark
        return 0xbf
    
    # Diacriticals
    if ch==0x40:  # space
        return 0x20
    if ch==0x41:  # grave
        return 0x2cb
    if ch==0x42:  # acute
        return 0x2ca
    if ch==0x43:  # circumflex
        return 0x2c6
    if ch==0x44:  # tilde
        return 0x2dc
    if ch==0x45:  # macron
        return 0x2c9
    if ch==0x46:  # breve
        return 0x2d8
    if ch==0x47:  # dot above
        return 0x2d9
    if ch==0x48:  # diaeresis
        return 0xa8
    if ch==0x49:  # dot under (full stop :-o)
        return 0x2e
    if ch==0x4a:  # ring above
        return 0x2da
    if ch==0x4b:  # cedilla
        return 0xb8
    if ch==0x4c:  # low macron
        return 0x2cd
    if ch==0x4d:  # double acute
        return 0xdd
    if ch==0x4e:  # ogonek
        return 0x2db
    if ch==0x4f:  # caron
        return 0x2c7

    # ... @todo    
    if ch==0x55: # quaver
        return 0x266a
    # up to 0x7f
    print ("[MapLatinG2] @TODO. UNHANDLED MAPPING: " + str(ch))
    return ord('?') #
