#!/usr/bin/env python3

# Teletext Stream to Invision decoder
# Copyright (c) 2020 Peter Kwan
# MIT License.

print('VBIT-iv System started')

import sys
import time
from ttxpage import TTXpage
import zmq


# Globals
packetSize=42 # The input stream packet size. Does not include CRI and FC

# buffer stuff
head=0
tail=0

# decoder state
currentMag=1#4
currentPage=0x00#0x70
capturing = False
elideRow = 0

# remote
pageNum = "100"

ttx = TTXpage()

print(sys.argv)

# Accept mag and page eg. .vbitvid 1 29
if int(sys.argv[1])>0:
  currentMag = int(sys.argv[1]) % 8
print ("mag = "+str(currentMag))
if int(sys.argv[2])>0:
  currentPage = int(sys.argv[2], 16)
print ("page = "+str(currentPage))

def clearPage():
  return # kill the console print 
  print("\033[2J", end='') # clear screen  
    

def printRow(packet, row=-1, col=-1, pagenum=''):
  return # Kill the console print  
  if row>-1 or col>-1:
    if row == -1:
      row = 0
    if col == -1:
      col = 0  
    print("\033[" + str(row) + ";" + str(col) + "f", end ='')  
  for i in range(2, 42):
    x = packet[i] & 0x7f
    if x < 0x020:
      print ('.', end='')
    else:
      print ( chr(packet[i] & 0x7f), end = '' )
  if pagenum != '':
    print("\033[" + str(row) + ";" + str(col) + "f" + pagenum, end ='')  
  print()

def deham(value):
  # Deham with NO checking! @todo Parity and error correction
  b0 = (value & 0x02) >> 1
  b1 = (value & 0x08) >> 2
  b2 = (value & 0x20) >> 3
  b3 = (value & 0x80) >> 4
  return b0+b1+b2+b3

def mrag(v1, v2):
  rowlsb = deham(v1)
  mag = rowlsb % 8
  if mag==0:
    mag = 8

  row = deham(v2) << 1
  if (rowlsb & 0x08)>0:
    row = row + 1
  return mag, row

def decodePage(packet):
  tens =  deham(packet[3])
  units = deham(packet[2])
  return tens * 0x10 + units

def remote(ch):
    global pageNum
    global currentMag
    global currentPage
    if ch>='0' and ch<='9':
        pageNum = pageNum + ch
        pageNum = pageNum[1:4]
        print ("Pagenum= " + pageNum)
        # validate
        if pageNum[0]>'0' and pageNum[0]<'9': # valid mag
            currentMag = int(pageNum[0])
            currentPage = int(pageNum[1:3],16)
            print ("mag, page = " + str(currentMag)+', '+hex(currentPage))
    else:
        print("Unhandled remote code: " + ch)
        # @todo Reveal, Fastext, Hold, Double height, Page up, Page Down, Mix
            
  
  
def process(packet):
  global capturing
  global currentMag
  global currentPage
  global elideRow
  result = mrag(packet[0], packet[1])
  mag = result[0]
  row = result[1]
  # If this is a header, decode the page
  
  # If we hit a row that follows a header, skip the packet
  if elideRow>0 and elideRow == row:
    ttx.mainLoop()
    print("eliding row= " + str(elideRow))
    elideRow=0
    return
  
  # only display things that are on our magazine
  if currentMag == mag: # assume parallel mode
    if row == 0:
      page = decodePage(packet)
#      print("\033[0;0fP", end='')
      # is this the magazine that we want?
      capturing = currentPage == page # Capture starts if this is the right page
      if capturing:
        clearPage() # @todo Decode header flags
      printRow(packet, 0, 0, "{:1d}{:02X}".format(mag,page))
      elideRow = 0
      # Show the whole header if we are capturing. Otherwise just show the clock
      ttx.printHeader(packet,  "{:1d}{:02X}".format(mag,page), capturing)
      #if capturing:
      #printRow(packet, 0, 0, "{:1d}{:02X}".format(mag,page))
      # print("\033[2J", end='') # clear screen  
        #printRow(packet)
    else:
      if capturing and row < 25:
        printRow(packet, row+1)
        if ttx.printRow(packet, row): # double height?
          elideRow = row+1  
  ttx.mainLoop()
  
# Remote control talks on port 6558
bind = "tcp://*:7777"
print("vbit-vi binding to " + bind)
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind(bind)  
  
try:
  # This thread reads the input stream into a field buffer
  while True:
    # load a field of 16 vbi lines
    for line in range(16):  
      # packet=file.read(packetSize) # file based version
      packet=sys.stdin.buffer.read(packetSize) # read binary from stdin
      process(packet)
    time.sleep(0.020) # 20ms between fields
    # Remote control zmq port 5557
    try:
      #message = socket.recv()
      message = socket.recv(flags=zmq.NOBLOCK)
      message = message.decode("utf-8")
      remote(message)
      #print("Message received " + message)
      socket.send(b"sup?")
    except zmq.Again as e:
      time.sleep(0.001) # do nothing
    
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
  print("Keyboard interrupt")    

except Exception as inst:
  print("some error") 
  print(type(inst)) 
  print(inst.args) 
  print(inst) 

finally:
  print("clean up") 