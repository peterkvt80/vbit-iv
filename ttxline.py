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
    
    fontH=-round((-1+self.height_value/(lines+1)))# 
    self.ttxfont0 = Font(family='teletext2', size=round(fontH/2))
    self.ttxfont2 = Font(family='teletext2', size=fontH)
    self.ttxfont4 = Font(family='teletext4', size=round(fontH*1.95))
    
    self.text = Text(self.root, width = 40, height = lines)
    # Most of these options are failed attempts to remove the single pixel lines
    self.text.config(borderwidth=0, foreground='white', background='black', font=self.ttxfont2, padx=0, pady=0, autoseparators=0, highlightbackground='black')
    
    for i in range(24):
      self.text.insert(END, "0123456789012345678901234567890123456789\n")
    self.text.tag_add("all", "1.0", END) # test to delete
    self.text.tag_config("all", spacing2 = 10) # test to delete
    
    self.rowOffset = 0 # Used to elide double height lines
    
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
    c = ch & 0x7f
    return (c>=0x20 and c<0x40) or c>=0x60  

  # clear and replace the line contents
  # @param packet : packet to write
  # @param row : row number to write
  def setLine(self, packet, row):
    # erase the line
    #print ("[setLine]row = "+str(row))
    rstr = str(row + 1) + "."
    tag_start=str(rstr +"0")
    tag_end=str(rstr +"40")
    self.text.delete(tag_start, tag_end ) # erase the line
    
    graphicsMode = False
    doubleHeight = False
    hasDoubleHeight = False
    holdChar = 0x00
    holdMode  = False
    contiguous = True
    concealed = True # @todo
    flashMode = False # @todo
    
    # PASS 1: put the characters in. Selects glyphs for alpha, contiguous gfx, separated gxf
    for i in range(40):
      c = packet[i+2] & 0x7f # strip parity
      #print(str(c))
      # Convert control code ascii
      # @todo Regional mappings
      ch = chr(c)
      #if ch<' ':#
        #ch = '?'  
      if c < 0x08: # alpha colours
        graphicsMode = False
      if c >= 0x10 and c < 0x18: # Mosaic colour
        graphicsMode = True
      if c == 0x1e: # hold graphics
        holdMode = True
      if c == 0x1f: # release graphics
        holdMode = False
      if c == 0x19: # Contiguous graphics
        contiguous = True
      if c == 0x1a: # Separated graphics
        contiguous = False  
      if graphicsMode:
        if holdMode:
          if self.isMosaic(c):
            holdChar = chr(c)
          else:
            c = ord('q')
        else:
          if c < 0x20: # Set At ( @todo. Set after )
            c = 0x020
        if self.isMosaic(c):
          if holdMode:
            ch = holdChar  # replace character if in hold mode
          if contiguous:
            ch = chr(c + 0x0e680 - 0x20) # contiguous
          else:  
            ch = chr(c + 0x0e680) # separated
        else:
          if ch < ' ': # blank out control code
            ch = ' '
          else:
            ch = chr(c)  # Text in graphics mode
      else:
        ch = self.mapchar(ch) # text in alpha mode
        #ch = 'x'
        # @todo separated and double height
      if ch < ' ':
        ch = ' '  
      self.text.insert(rstr+str(i), ch)
      
    # PASS 2: Add text attributes: font, colour, flash
    foreground_colour = 'white'
    background_colour = 'black'
    tagRowID = "WholeRow"+ str(row)
    self.text.tag_add(tagRowID, tag_start, tag_end)
    self.text.tag_config(tagRowID, font=self.ttxfont2)
    
    for i in range(40):
      doubleHeight = False
      c = packet[i+2] & 0x7f
      ch = chr(c)
      #if i==1 and c<0x20:
        #print (hex(c))
      if c == 0x0d:
        doubleHeight = True # @todo Need to make sure the next line is blanked
      if c==0x1c: # black background
        background_colour = 'black'  
      if c==0x1d: # new background
        background_colour = foreground_colour  
      if c < 0x08 or c==0x1d or c==0x1c: # alpha colours, new background, black background
        tid = "ta" + str(row)+str(i)
        loc = rstr + str(i)
        self.text.tag_add(tid, loc, rstr + str(40))

#self.text.tag_add("ta"+str(i), "1."+str(i)) #, "1."+str(39))
        foreground_colour = self.getcolour(c)
        self.text.tag_config(tid, background=background_colour, foreground=foreground_colour) #foreground_colour)
        #print("tid = " + tid + " loc = " + loc + ", colour = " + foreground_colour )
        #print ("c =" + str(colour))   
        #start = i  
        #print("got here - 2, start = " + str(start) +" i = " + str(i))
      if c >= 0x10 and c < 0x18: # Mosaic colour
        tag_id = "tg"+str(row)+str(i)
        self.text.tag_add(tag_id, rstr + str(i), rstr + str(40))
        foreground_colour = self.getcolour(c-0x10)
        self.text.tag_config(tag_id , foreground = foreground_colour, background = background_colour)
      if doubleHeight:
        hasDoubleHeight = True  
        self.text.tag_config(tid, font=self.ttxfont4) # Implement normal height too
        # hide the next row
        if row < 23 and False:          
          tag_id = "ta"+str(row + 1) + str(i)
          tag_rstr = str(row + 2) + "."
          print ("old tid = " + tid + " tag_id = " + tag_id + ", tag_rstr = " + tag_rstr)
          self.text.tag_add(tag_id, tag_rstr + str(0), tag_rstr + str(40))
          self.text.tag_config(tag_id, font=self.ttxfont0)
    return hasDoubleHeight
    
  def printHeader(self, packet, page = "Header.."):
    buf=bytearray(packet)
    for i in range(8): # blank the control area
      buf[i+2]=ord('x') #0x20
    self.setLine(buf, 0)
    self.text.delete("1.0", "1.8") # strip the control bytes
    self.text.insert("1.0", ("P"+page)[0:4]) # add the page number
    self.text.insert("1.4", "    ") # pad the remaining space
    self.rowOffset = 0
  
  # Return True if the row includes double height
  def printRow(self, packet, row):
    # print(packet)
    # @todo row
    if self.setLine(packet, row - self.rowOffset):
      self.rowOffset=self.rowOffset+1
      return True
    return False


