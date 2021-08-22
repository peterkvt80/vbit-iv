# vbit-iv
## In-vision teletext display

Intended use. To get the full teletext experience without a television. For generating teletext displays on a Linux PC. To display teletext on any output device and not just in 625 line PAL.

It takes the teletext stream generated by vbit2 and decodes this and displays it full frame. It displays teletext pages on a Linux PC or Raspberry Pi. In this way you can display live teletext on any display that you have connected. This opens the possibiliy of using a projector for presentations and exhibitions.

By using vbit2 you can get a live teletext feed from a number of channels including Teefax and Chunkytext.

A network server listens for remote control commands so you can select pages by sending the appropriate commands. vbit-remote.py is a simple client that takes keyboard commands and sends them to vbit-iv. You can write your own client to work a remote control from a mobile phone for example. 

# Installation

Requirements: Linux operating system. Tested with Ubuntu and Raspberry Pi OS. Python 3. <List of Python modules to add like zmq> VBIT2 teletext streamer.
It may work on Windows if you use the Windows version of VBIT2 but you are on your own!

* Install VBIT2 as detailed in the Github project. Use vbit-config to add services and select one to display.
* Download the vbit-iv ZIP and unpack it somewhere convenient OR better still, clone it if you want to keep the code up to date.
* Click on the font files and install them onto your system. These are teletext2.ttf and teletext4.ttf. For Raspberry Pi OS just copy them to the fonts folder. 
* You also need to install screeninfo from PyPI using a python package manager or type
    
    pip3 install screeninfo

# Running
Move to your vbit-iv/ directory. There are a number of ways that you could run the code.
## Python
The easiest method is to run the in-vision script as this starts everything and starts the vbit2 configured service.

    ./innervision.py

You can type commands directly onto the teletext page, or into the shell that you launched the program from. In the case of the shell, it sends the comands through the remote control port so you can't attach another remote control client to it.

To change the service, use the vbit configuration utility. You can manages services here including adding, selecting and updating. Don't use the Start VBIT2 option as the in vision viewer doesn't need it.

    vbit-config

## Command line
$HOME/vbit2/vbit2 --dir $HOME/.teletext-services/Teefax | ./vbit-iv.py 1 0

This command starts vbit2 with the Teefax service. Unlike the python startup script this doesn't use the vbit2 config system. You need to give it the name of one of the service that you installed using vbit-config (Ceefax, Chunkytext, SPARK, Teefax etc.). The last two numbers are the initial magazine (1..8) and the page number (0..99)


## Commands
The keyboard is used as a remote control. You may need to click on the screen first to get focus.
* 0 to 9. Select page number.
* h - Hold toggle
* r - Reveal-oh toggle
* u,i,o,p - Fastkeys Red, Green, Yellow, Cyan.
* q - Close down the viewer
* plus/minus - Next/Previous page (not implemented)

## Remote control
The viewer has a network remote control on port 7777. vbit-remote.py is a suitable client. It uses the same commands as the keyboard. You can edit the code to change your host if you want to run the remote on another computer. To use it just run the viewer and type the commands into the shell you ran it from.

    ./vbit-remote.py
  
Another remote control is "Pages from Teefax". This sequences a series of pages. First create a file caled pft.config. Each line is a three digit page number, a space and then a timing. The example below shows all of the BBC news pages in Teefax. Note that the units of the page number can be replaced by a wildcard to display all the pages (in this case) 110 to 119
  
    104 20
    105 20
    106 20
    107 20
    108 20
    109 20
    11* 20
    120 20
    121 20
    122 20
    123 20
    134 20
  
Run the remote control with 
    ./pft.py  

You can write your own remote control, for controlling vbit-iv. It only takes a little bit of Python coding. Some ideas for you: A voice activated page selector. A carousel of the last ten updated pages. A default page reset. The system always returns to the same page every five minutes, so people can browse but it resets. Any more ideas?
    
# FLIRC
FLIRC stands for Linux Infra Red Control. I'd rather not say what the F stands for. FLIRC is a tiny USB receiver that picks up infra red commands and converts them into keyboard key presses. So for example, you can program the Reveal button on your remote control so that it generates an "r" key press.
    
It is a really great if a bit pricey device once you have it set up. However, the setup software is a bad experience all round. Once you have the software installed and running you can program your FLIRC. Choose the full keyboard option and programme the keys listed in the *Commands* section with your remote control.
    
Fortunately you only need to do this once for when the keys are programmed, you can move the FLIRC to any PC, laptop, Raspberry Pi or whatever you've got that can be controlled by a USB keyboard.
