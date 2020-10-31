# ttxpage.py.
#
# VBIT Stream renderer. Teletext page level.
# You can modify this to run full frame
# or a smaller window
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

from tkinter import Tk
from ttxline import TTXline

class TTXpage:
    print("TTXPage created")
    def __init__(self):
        self.root = Tk()

        self.width_value=self.root.winfo_screenwidth() # full screen
        self.height_value=self.root.winfo_screenheight()

        #self.width_value = 768 # not full screen
        #self.height_value=576
        self.root.configure(background='black', borderwidth=0, highlightthickness=0)
        self.root.geometry("%dx%d+0+0" % (self.width_value, self.height_value))

        # Make it full screen (Comment it out if you want to run in a window)
        self.root.wm_attributes('-fullscreen','true')

        self.root.wait_visibility(self.root)

        # lines
        self.lines = TTXline(self.root)
        self.lines.text.pack()

        self.root.update_idletasks()
        self.root.update()
    
    def printRow(self, packet, row):
        if row < 0 or row > 24 :
            return
        return self.lines.printRow(packet, row)

    def printHeader(self, packet, page, seeking):
        self.lines.printHeader(packet, page, seeking)

    # Actually draw the stuff
    def mainLoop(self):
        self.root.update_idletasks()
        self.root.update()
  
