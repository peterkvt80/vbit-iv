Launchers are clickable desktop icons that can start teletext services.

A teletext service in this case is a folder with tti page files.
This is installed as a part of vbit2 or you can use other sets of pages. 

Launchers is a kit of bits for the Raspberry Pi OS and is an accessory for
vbit-iv, the teletext viewer. It is a desktop icon, some desktop
shortcuts and shell scripts.

Installation
============

Copy the files
==============
This assumes that you have installed vbit-iv already.
launchers is a subfolder of the vbit-iv project

1) Copy the icon palm_tree_icon32.png to /home/pi/Pictures 
2) Copy the go and ttx scripts to your home folder /home/pi
3) Copy one of the desktop files to /home/pi/Desktop

Edit the files
==============
Use geany, nano or whatever editor you like.

The go script is used for showing a vbit2 supported service such
as Teefax. You will need to change this according to where you
installed vbit-iv.

    #!/bin/sh
    # Run the current vbi2 service

    cd /home/pi/vbit-iv
    ./innervision.py &
    
Use vbit-config to select which service you want to view.

The ttx script is for running services that are not repo based and so
can't be added or selected using vbit-config. The instructions for the
three paths that it needs are in the ttx file.  

    #!/bin/sh
    # Displays a teletext service from a folder containing tti files.
    # It is most useful for running a service that isn't in vbit-config.
    # This is either because it doesn't have a repo associated with it
    # or it is a purely local service.

    # You must configure these file locations to match your installation.
    # Parameter - The name of your service in the service folder - eg. artfax
    # The VBIT2 stream generator executable - Wherever vbit2 was installed
    VBIT2="/home/pi/vbit2/vbit2"
    # The folder containing your teletext services - eg. /home/pi/Document/service/
    SERVICE="/home/pi/Documents/service/"
    # The vbit=iv.py executable
    VBITIV="/home/pi/vbit2/vbit-iv/vbit-iv.py"
    $VBIT2 --dir $SERVICE$1/ | $VBITIV 1 0 

The .desktop script comes in two flavours. The Teefax one should just
run if the go script is in /home/pi. For services not managed by
vbit-config you should make a new desktop launch file.
This one shows a service called Turner.
The Name parameter is the name on the icon.
The Exec parameter is the filename of the folder.

    [Desktop Entry]
    Type=Application
    Encoding=UTF-8
    Name=Turner
    Exec=/home/pi/ttx turner
    Icon=/home/pi/Pictures/palm_tree_icon32.png
    StartUpNotify=true
    Terminal=false

Optional
========

Replace the desktop image with
IMG_20200305_072500.jpg
and set the text colour to black.

Testing
=======
With so much manual intervention, things are bound to go wrong.
It should be possible to automate much of this.
It is also possible to test this manually to identify problems.
Unfortunately I haven't written any of this.
