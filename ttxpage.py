from tkinter import Tk
from ttxline import TTXline

class TTXpage:
  print("TTXPage created")
  def __init__(self):
    self.root = Tk()

    self.width_value=self.root.winfo_screenwidth()
    self.height_value=self.root.winfo_screenheight()

    #self.width_value = 768
    #self.height_value=576
    self.root.configure(background='black', borderwidth=0, highlightthickness=0)
    self.root.geometry("%dx%d+0+0" % (self.width_value, self.height_value))
    
    # Make it full screen
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
    #print ("row = " + str(row))
    #self.lines[row].printRow(packet, row)  

  def printHeader(self, packet, page, capturing):
    self.lines.printHeader(packet, page, capturing)

  # Actually draw the stuff
  def mainLoop(self):
    self.root.update_idletasks()
    self.root.update()
  
