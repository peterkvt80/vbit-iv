#!/usr/bin/env python3

# Teletext Stream to Invision decoder
# Copyright (c) 2020 Peter Kwan
# MIT License. blah blah.

from tkinter import Tk, Text, END
from tkinter.font import Font

class TTXline:
    print("TTXLine created")
    def __init__(self, root_param):
        # this is where we define a Text object and set it up  
        self.root = root_param
        self.text = Text(self.root)

        # establish the maximum font size required to fill the available space
        # what is the window height?
        self.height_value=self.root.winfo_screenheight()

        lines = 25

        self.fontH=-round((-1+self.height_value/(lines+1)))# 
        self.ttxfont0 = Font(family='teletext2', size=round(self.fontH/2))
        self.ttxfont2 = Font(family='teletext2', size=round(self.fontH))
        self.ttxfont4 = Font(family='teletext4', size=round(self.fontH*1.95))

        self.text = Text(self.root, width = 40, height = lines)
        # Most of these options are failed attempts to remove the single pixel lines
        self.text.config(borderwidth=0, foreground='white', background='black', font=self.ttxfont2, padx=0, pady=0, autoseparators=0, highlightbackground='black')

        for i in range(24):
            self.text.insert(END, "0123456789012345678901234567890123456789\n")
        self.text.tag_add("all", "1.0", END) # test to delete
        self.text.tag_config("all", spacing2 = 10) # test to delete

        self.rowOffset = 0 # Used to elide double height lines

        self.pageLoaded = False
        self.found = False
        self.currentHeader = bytearray()
        self.currentHeader.extend(b'YZ0123456789012345678901234567890123456789') # header of the page that is being displayed
    
    # true if while in graphics mode, it is a mosaic character. False if control or upper case alpha  
    def isMosaic(self, c):
        ch = c & 0x7f  
        return (ch>=0x20 and ch<0x40) or ch>=0x60

    # Map character c to regional character
    def mapchar(self, c):
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
    
    def getcolour(self, c):    
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

    # return True if the ascii value of the character is mosaic
    def isMosaic(self, ch):
        return ch & 0x20; # Bit 6 set?

    # clear and replace the line contents
    # @param packet : packet to write
    # @param row : row number to write
    def setLine(self, packet, row):
        # It has two phases
        # 1) Place all the characters on the line
        # 2) Set their attributes: colour and font size

        #print ("[setLine]row = "+str(row))
        # erase the line
        rstr = str(row + 1) + "." # The row string
        tag_start=str(rstr +"0")
        tag_end=str(rstr +"end")
        self.text.delete(tag_start, tag_end ) # erase the line

        # Set the conditions at the start of the line
        graphicsMode = False
        doubleHeight = False
        hasDoubleHeight = False
        holdChar = 0x00
        holdMode  = False
        contiguous = True
        concealed = True # @todo
        flashMode = False # @todo

        lastMosaicChar = ' '
    
        # PASS 1: put the characters in. Selects glyphs for alpha, contiguous gfx, separated gxf
        for i in range(40):
            c = packet[i+2] & 0x7f # strip parity
            # Convert control code ascii
            # @todo Regional mappings
            ch = chr(c)
            if c == 0x0f: # double size
                print("double size not implemented")  # Not the same as double height
            if c == 0x1e: # hold graphics - set at
                holdMode = True
                holdChar = lastMosaicChar # ' '
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
                    if holdMode:
                        ch = holdChar # non printable and in hold
                    else:  
                        ch = ' ' # Non printable  
                # if it is not a mosaic and we are in hold mode, substitute the character      
            else:
                # alpha is way simpler  
                if ch < ' ':
                    ch = ' '
                else:              
                    ch = self.mapchar(ch) # text in alpha mode
            self.text.insert(rstr+str(i), ch)
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
        tagRowID = "WholeRow"+ str(row)
        self.text.tag_add(tagRowID, tag_start, tag_end)
        self.text.tag_config(tagRowID, font=self.ttxfont2)

        hf=1
    
        # Set the text attributes: colour and font size
        for i in range(40):
            c = packet[i+2] & 0x7f
            ch = chr(c)
            #if i==1 and c<0x20:
            #print (hex(c))
            if c == 0x0c: # normal height
                # This code breaks if there is a normal size but NO double height on the line 
                tag_id = "thc"+str(row)+str(i)
                self.text.tag_add(tag_id, rstr + str(i+1), rstr + 'end') # column + 1 - set-after
                self.text.tag_config(tag_id, font=self.ttxfont2, offset=0) # normal height too
            # @todo Doing another pass for the offset is the only way to make it work correctly, probably
            if c == 0x0d: # double height
                hasDoubleHeight = True  
                tag_id = "thd"+str(row)+str(i)
                self.text.tag_add(tag_id, rstr + str(i+1), rstr + 'end') # column + 1 - set-after         
                self.text.tag_config(tag_id, font=self.ttxfont4, offset=0) # double height

            colourChanged =False
            set_at = 1 # 0 = set at, 1 = set after
            if c==0x1c: # black background - set at
                background_colour = 'black'
                colourChanged = True
                set_at = 0
            if c==0x1d: # new background - set at
                background_colour = foreground_colour
                colourChanged = True
                set_at = 0
            if c < 0x08 : # alpha colour - set after
                foreground_colour = self.getcolour(c)
                colourChanged = True
            if c >= 0x10 and c < 0x18: # Mosaic colour - set after
                foreground_colour = self.getcolour(c-0x10)
                colourChanged = True

            if colourChanged:          
                tag_id = "tg"+str(row)+str(i) # Do not add set-at to the column in the tag. It could alias the tag
                self.text.tag_add(tag_id, rstr + str(i+set_at), rstr + 'end') # 
                self.text.tag_config(tag_id , foreground = foreground_colour, background = background_colour)
          
        return hasDoubleHeight
    
    def printHeader(self, packet, page = "Header..", seeking = False):
        global found
        buf = bytearray(packet) # convert to bytearray so we can modify it
        for i in range(10): # blank out the header bytes
            buf[i]=ord(' ')
        #print('A')  
        for i in range(34,42): # copy the clock
            self.currentHeader[i] = buf[i]
            #print(str(type(self.currentHeader)))  
            #print(str(type(buf)))
          
        if seeking:
            #self.pageLoaded = False
            self.currentHeader = buf # The whole header is updating
            found = False
        else:
            if not found:
                self.currentHeader = buf # The whole header is updating
                found = True
            #if not self.pageLoaded:
            #    self.pageLoaded = True  
            buf = self.currentHeader # The header stays on the loaded page

        self.setLine(buf, 0)

        # Now that the buffer has the correct characters loaded, we can set the generated page number
        #@todo Change the colour of the page number while seeking a page
        self.text.delete("1.0", "1.8") # strip the control bytes
        self.text.insert("1.0", ("P"+page)[0:4]) # add the page number
        self.text.insert("1.4", "    ") # pad the remaining space
        self.text.tag_add("pageColour", "1.0", "1.8")
        if seeking:
            self.text.tag_config("pageColour", foreground = "green1") # seeking
        else:
            self.text.tag_config("pageColour", foreground = "white") # found
          
        self.rowOffset = 0
  
    # Return True if the row includes double height
    def printRow(self, packet, row):
        # print(packet)
        # @todo row
        if self.setLine(packet, row - self.rowOffset):
            self.rowOffset=self.rowOffset+1
            return True
        return False


