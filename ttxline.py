#!/usr/bin/env python3

# Teletext Stream to Invision decoder
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

from tkinter import Text, END, NORMAL, DISABLED
from tkinter.font import Font
from mapper import mapchar, mapdiacritical
from clut import clut, Clut
from packet import Packet, metaData

class TTXline:
    print("TTXLine created")

    # Map a teletext colour number to an actual colour
    # I suspect that the CLUT
    def getcolourOLD(self, c):
        switcher = {
        0: "black",
        1: "red",
        2: "green1",
        3: "yellow",
        4: "blue",
        5: "magenta",
        6: "cyan",
        7: "white"
        }
        return switcher.get(c, "white")

    # Map a teletext colour number to an actual colour
    # I suspect that the CLUT
    def getcolour(self, c):
        global clut
        return clut.clut0[c]

    def __init__(self, root_param):
        # this is where we define a Text object and set it up
        self.root = root_param
        self.text = Text(self.root)

        # establish the maximum font size required to fill the available space
        # what is the window height?
        self.height_value=self.root.winfo_screenheight()

        lines = 25

        self.fontH=-round((-1+self.height_value/(lines+1)))#
        # self.ttxfont0 = Font(family='teletext2', size=round(self.fontH/2))
        self.ttxfont2 = Font(family='teletext2', size=round(self.fontH))
        self.ttxfont4 = Font(family='teletext4', size=round(self.fontH*1.95))

        # allow for side panel of up to 16 characters
        self.text = Text(self.root, width = 56, height = lines) # The normal text
        self.textConceal = Text(self.root, width = 56, height = lines) # Copy of text but with reveals hidden

        # Most of these options are failed attempts to remove the single pixel lines
        self.text.config(borderwidth=0, foreground='white', background='black', font=self.ttxfont2, padx=0, pady=0, autoseparators=0, highlightbackground='black')
        self.textConceal.config(borderwidth=0, foreground='white', background='black', font=self.ttxfont2, padx=0, pady=0, autoseparators=0, highlightbackground='black')

        for i in range(24):
            if i==11:
                self.text.insert(END, "     VBIT IN-VISION                     \n")
                self.textConceal.insert(END, "     VBIT IN-VISION                     \n")
                tag_id = "dbl"
                self.text.tag_add(tag_id, "12.0", '12.end')
                self.text.tag_config(tag_id, font=self.ttxfont4, offset=0, foreground = 'orange') # double height
            else:
                self.text.insert(END, "                                        \n")
                self.textConceal.insert(END, "                                        \n")
        #self.text.tag_add("all", "1.0", END) # test to delete
        #self.text.tag_config("all", spacing2 = 10) # test to delete

        self.rowOffset = 0 # Used to elide double height lines

        self.pageLoaded = False
        self.found = False
        self.currentHeader = bytearray()
        self.currentHeader.extend(b'YZ0123456789012345678901234567890123456789') # header of the page that is being displayed

        self.revealMode = False # hidden

        # header flags
        self.natOpt = 0 # 0=EN, 1=FR, 2=SW/FI/HU, 3=CZ/SK, 4=DE, 5=PT/SP, 6=IT, 7=N/A
        # self.region = 0 # National option selection bits in X/28/0 format 1. Used by RE in tti files.

        self.clearFlag = False # Set by clear(), cleared by printHeader()
        
        self.offsetSplit = 8 # Where the side panels are split (0..16, default 8)

    def deham(self, value):
        # Deham with NO checking! @todo Parity and error correction
        b0 = (value & 0x02) >> 1
        b1 = (value & 0x08) >> 2
        b2 = (value & 0x20) >> 3
        b3 = (value & 0x80) >> 4
        return b0+b1+b2+b3

    # true if while in graphics mode, it is a mosaic character. False if control or upper case alpha
    def isMosaic(self, ch):
        return ch & 0x20; # Bit 6 set?

    # clear and replace the line contents
    # @param packet : packet to write
    # @param row : row number to write (starting from 0)
    def setLine(self, pkt, row):
        # It has two phases
        # 1) Place all the characters on the line
        # 2) Set their attributes: colour and font size
        
        

        rstr = str(row + 1) + "." # The row string. First Text row is 1
        tag_start=str(rstr +"0")
        tag_end=str(rstr +"end")

        # wsfn remove this for testing
        for tag in self.text.tag_names(): # erase the line attributes
            attr = tag.split('-')
            if attr[0] == str(row+1):
                #print('deleting tag = ' + tag)
                self.text.tag_delete(tag)
                self.textConceal.tag_delete(tag)
        #print ("[setLine]row = "+str(row))
        # erase the line
        self.text.delete(tag_start, tag_end ) # erase the line
        self.textConceal.delete(tag_start, tag_end )


        # Set the conditions at the start of the line
        graphicsMode = False
        hasDoubleHeight = False
        holdChar = 0x00
        holdMode  = False
        contiguous = True
        concealed = False
        flashMode = False # @todo

        lastMosaicChar = ' '
        
        self.text.insert(tag_start, "        ") # This could be a big mistake
        self.text.insert(tag_start, "        ")

        # PASS 1: put the characters in. Selects glyphs for alpha, contiguous gfx, separated gxf
        for i in range(40):
            c = pkt[i+2] & 0x7f # strip parity
            # Convert control code ascii
            # @todo Regional mappings
            ch = chr(c)
            if c < 0x08 or c >= 0x10 and c < 0x18: # colour codes cancel conceal mode
                concealed = False
            #if c == 0x0f: # double size
             #   print("double size not implemented")  # Not the same as double height
            if c == 0x1e: # hold graphics - set at
                holdMode = True
                holdChar = lastMosaicChar # ' '
            if c == 0x18: # conceal mode - set at
                concealed = True
            if c == 0x19: # Contiguous graphics
                contiguous = True
            if c == 0x1a: # Separated graphics
                contiguous = False
            if graphicsMode:
                # If it is a mosaic, work out what character it is
                if self.isMosaic(c):
                    if contiguous:
                        ch = chr(c + 0x0e680 - 0x20) # contiguous
                    else:
                        ch = chr(c + 0x0e680) # separate
                    if holdMode:
                        holdChar = ch # save the character for later
                    lastMosaicChar = ch
                else:
                    if ch<' ': # Unprintable?
                        if holdMode:
                            ch = holdChar # non printable and in hold
                        else:
                            ch = ' ' # Non printable
                    else:
                        ch = mapchar(ch, self.natOpt , metaData.getRegion()) # text in alpha mode @todo implement group number
                        ch = mapdiacritical(ch, row, i, metaData.X26CharMappings)
                # if it is not a mosaic and we are in hold mode, substitute the character
            else:
                # alpha is way simpler
                if ch < ' ':
                    ch = ' '
                else:
                    ch = mapchar(ch, self.natOpt , metaData.getRegion()) # text in alpha mode @todo implement group number
                    ch = mapdiacritical(ch, row, i, metaData.X26CharMappings)
            # Add the character, unless it is hidden
            self.text.insert(rstr+str(i+self.offsetSplit), ch if not concealed else ' ')
            # Keep the concealed characters only
            self.textConceal.insert(rstr+str(i+self.offsetSplit), ch if concealed else ' ') # Save the characters that ARE concealed
            # set-after
            if c == 0x1f: # release graphics - set after
                holdMode = False
            if c < 0x08: # alpha colours
                graphicsMode = False
            if c >= 0x10 and c < 0x18: # Mosaic colour
                graphicsMode = True

        # PASS 2: Add text attributes: font, colour, flash
        foreground_colour = 'white'
        background_colour = 'black'
        text_height = 'single'
        # Set the initial colour for the row

        # Set the text attributes: colour and font size
        # row
        row = str(row + 1)
        ix= 0
        attr = text_height
        for i in range(40):
            c = pkt[i+2] & 0x7f
            ch = chr(c)
            #if i==1 and c<0x20:
            #print (hex(c))
            attributeChanged =False
            if c == 0x0c: # normal height
                # This code breaks if there is a normal size but NO double height on the line
                text_height = 'single'
                #tag_id = "thc"+str(row)+"-"+str(i)
                attributeChanged = True
                #tag_id = text_height + '-' + foreground_colour + '-' + background_colour
                #self.text.tag_add(tag_id, rstr + str(i+1), rstr + 'end') # column + 1 - set-after
                # self.text.tag_config(tag_id, font=self.ttxfont2, offset=0) # normal height too
            # @todo Doing another pass for the offset is the only way to make it work correctly, probably
            if c == 0x0d: # double height
                text_height = 'double'
                hasDoubleHeight = True
                attributeChanged = True
                #tag_id = "thd"+str(row)+"-"+str(i)
                #tag_id = text_height + '-' + foreground_colour + '-' + background_colour
                #self.text.tag_add(tag_id, rstr + str(i+1), rstr + 'end') # column + 1 - set-after
                #print("Setting height attributes " + tag_id)
                ##self.text.tag_config(tag_id, font=self.ttxfont4, offset=0) # double height

            set_at = 1 # 0 = set at, 1 = set after
            if c==0x1c: # black background - set at
                background_colour = 'black'
                attributeChanged = True
                set_at = 0
                #background_colour = metaData.mapColourBg(int(row), i, background_colour)
                #foregroundground_colour = metaData.mapColourFg(int(row), i, foreground_colour) # x26/0
            if c==0x1d: # new background - set at
                background_colour = foreground_colour
                attributeChanged = True
                set_at = 0
                #background_colour = metaData.mapColourBg(int(row), i, background_colour)
                #foregroundground_colour = metaData.mapColourFg(int(row), i, foreground_colour) # x26/0
            if c < 0x08 : # alpha colour - set after
                foreground_colour = self.getcolour(c)
                attributeChanged = True
                # also need to see if there is an X26/0 background colour change
                #foreground_colour = metaData.mapColourFg(int(row), i, foreground_colour)
                #background_colour = metaData.mapColourBg(int(row), i, background_colour)
            if c >= 0x10 and c < 0x18: # Mosaic colour - set after
                foreground_colour = self.getcolour(c-0x10)
                attributeChanged = True
                #foreground_colour = metaData.mapColourFg(int(row), i, foreground_colour)
                #background_colour = metaData.mapColourBg(int(row), i, background_colour)
                # also need to see if there is an X26/0 foreground colour change
            fg = metaData.mapColourFg(int(row), i+1, foreground_colour) # Set after
            if fg != foreground_colour:
                attributeChanged = True
                foreground_colour = fg
            bg = metaData.mapColourBg(int(row), i+1, background_colour) # Set at
            if bg != background_colour:
                attributeChanged = True
                background_colour = bg
            if attributeChanged:
                # tag_id identifies the row
                tag_id = row + '-' + str(ix) + '-' + text_height + '-' + foreground_colour + '-' + background_colour
                ix = ix + 1
#                tag_id = row + '-' + str(ix++) + '-' + text_height + '-' + foreground_colour + '-' + background_colour
                #tag_id = 'double' + '-' + 'cyan' + '-' + 'black'
                #print("Setting attributes at " +rstr + str(i+set_at) + " to " + rstr + 'end *' + tag_id + '*')
                self.text.tag_add(tag_id, rstr + str(i+set_at+self.offsetSplit), rstr + 'end') #
                self.textConceal.tag_add(tag_id, rstr + str(i+set_at+self.offsetSplit), rstr + 'end') #

                if text_height == 'double':
                    textFont = self.ttxfont4
                else:
                    textFont = self.ttxfont2
                self.text.tag_config(tag_id , font = textFont, foreground = foreground_colour, background = background_colour)
                self.textConceal.tag_config(tag_id , font = textFont, foreground = foreground_colour, background = background_colour)

        self.text.config(state = DISABLED) # prevent editing
        return hasDoubleHeight

    def decodeFlags(self, packet):
        return
        flags = [0,0,0,0,0,0,0,0,0]
        for i in range(8):
            flags[i] = self.deham(packet[i+2])
            print (hex(flags[i]) + ', ', end='')
        print()
        page = flags[1]*0x10 + flags[0]
        C4 = (flags[3] & 0x08) > 0 # clear
        C5 = (flags[5] & 0x04) > 0 # newsflash
        self.natOpt = (flags[7] >> 1) & 0x07 # C12, C13, C14
        C11 = flags[7] & 0x01 # Serial tx
        print("Page = " + hex(page) + ", C4(clear) = " + str(C4) + ", C5 = " + str(C5) + " natOpt = " + str(self.natOpt))

    # param page - An 8 character info string for the start of the header
    def printHeader(self, packet, page = "Header..", seeking = False):
        if self.clearFlag:
            self.clearFlag = False
        lines = self.text.index(END)
        line = lines.split('.')[0]
        if int(line)>26:
            print("[printHeader] " + str(line) + " Too many lines. Some bug somewhere!")
        self.text.config(state = NORMAL) # allow editing
        buf = bytearray(packet) # convert to bytearray so we can modify it
        for i in range(34,42): # copy the clock
            self.currentHeader[i] = buf[i]
            #print(str(type(self.currentHeader)))
            #print(str(type(buf)))

        for i in range(10): # blank out the header bytes
            buf[i]=buf[i] & 0x7f
            if buf[i]<0x20:
                buf[i]=0x20
        for i in range(2,10):
            buf[i]=ord(page[i-2])

        if seeking:
            #self.pageLoaded = False
            self.currentHeader = buf # The whole header is updating
            self.found = False
        else:
            if not self.found:
                self.currentHeader = buf # The whole header is updating
                self.found = True
                self.revealMode = False # New page starts with concealed text
                # Now that we have found the page, dump all of the tags
                # @todo Probably change this to tag_remove
                # for tag in self.text.tag_names(): # This clears all tags BUT only when moving to a new page
                #     self.text.tag_delete(tag)
                self.decodeFlags(packet)
                print("[printHeader]Is this where we run clear?") # yes it is. However, we ALSO want to run it
                self.clear()
                
            #if not self.pageLoaded:
            #    self.pageLoaded = True
            buf = self.currentHeader # The header stays on the loaded page

        self.setLine(buf, 0)

        # Now that the buffer has the correct characters loaded, we can set the generated page number
        #@todo Change the colour of the page number while seeking a page
        #self.text.delete("1.0", "1.8") # strip the control bytes
        #self.text.insert("1.0", "pagexxxx") # add the page number
        #print("inserting <" + page +'>')
        # self.text.insert("1.4", "    ") # pad the remaining space
        #self.text.tag_add("pageColour", "1.0", "1.7")
        if seeking or page[0] == 'H': # Page number goes green in HOLD or while seeking
            self.text.tag_add("pagenumber", "1.0", "1.7")
            self.text.tag_config("pagenumber", foreground = "green1") # seeking
            self.textConceal.tag_add("pagenumberc", "1.0", "1.7")
            self.textConceal.tag_config("pagenumberc", foreground = "green1") # seeking
        else:
            self.text.tag_add("pagenumber", "1.0", "1.7")
            self.text.tag_config("pagenumber", foreground = "white") # found
            self.textConceal.tag_add("pagenumberc", "1.0", "1.7")
            self.textConceal.tag_config("pagenumberc", foreground = "white") # found

        self.rowOffset = 0
        self.text.config(state = DISABLED)

    # Return True if the row includes double height
    def printRow(self, packet, row):
        self.text.config(state = NORMAL) # allow editing
        if self.setLine(packet, row - self.rowOffset):
            self.rowOffset=self.rowOffset+1
            return True
        return False

    # show/hide concealed text
    def toggleReveal(self):
        self.revealMode = not self.revealMode
        self.text.config(state = NORMAL) # allow editing
        for row in range(24):
            for col in range(40):
                p0 = str(row + 1) + '.' + str(col)
                ch = self.textConceal.get(p0) # The revealed character
                if ch!=' ': # It might be concealed
                    if not self.revealMode:
                        ch = ' ' # or it could be hidden
                    p1 = str(row + 1) + '.' + str(col+1)
                    self.text.insert(p0, ch)
                    self.text.delete(p1)
        self.text.config(state = DISABLED)

    # Clear stuff including all the page modifiers
    def clear(self):
        self.clearFlag = True
        # self.region = 0
        metaData.clear()
