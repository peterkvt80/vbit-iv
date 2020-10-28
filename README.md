# vbit-iv
## In-vision teletext display

Intended use. To get the full teletext experience without a television. For generating teletext displays on a Linux PC. To display teletext on any output device and not just in 625 line PAL.

It takes the teletext stream generated by vbit2 and decodes this and displays it full frame. It displays teletext pages on a Linux PC or Raspberry Pi. In this way you can display live teletext on any display that you have connected. This opens the possibiliy of using a projector for presentations and exhibitions.

By using vbit2 you can get a live teletext feed from a number of channels including Teefax and Chunkytext.

A network server listens for remote control commands so you can select pages by sending the appropriate commands. vbit-remote.py is a simple client that takes keyboard commands and sends the to vbit-iv. You can write your own client to work a remote control from a mobile phone for example. 

todo@ 
* Better header rendering. 
* Remaining features: flash/reveal etc.
* Standards compliance. Edge cases to fix.
* Channel switching via remote.
