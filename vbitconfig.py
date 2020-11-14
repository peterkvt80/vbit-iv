# vbit-config.py
# Teletext Stream to selector
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

from pathlib import Path
import re

class Config:
    def __init__(self):
        # Get the sources
        self.HOME = str(Path.home())
        self.KNOWN = self.HOME + "/vbit2/known_services"
        self.SERVICESDIR = self.HOME+ "/.teletext-services"
        self.CONFIG = self.SERVICESDIR + "/config"
        
        # Read the config    
        f = open(self.CONFIG, 'r')
        text = f.read()
        # print(re.findall(r'#.*', text)) # Match comments
        
        # Read the source
        source = re.findall(r'SELECTED="(.*)"', text)
        self.service = source[0]
        
        # Create the launch string. It should look something like this:
        # /home/peterk/vbit2/vbit2 --dir /home/peterk/.teletext-services/Teefax | ./vbit-iv.py 1 0
        streamer = self.HOME + '/vbit2/vbit2 ' # Run vbit ...
        service = ' --dir ' + self.HOME + '/.teletext-services/' + self.service # using this service ...
        render = 'vbit-iv.py 1 0' # into a renderer
        self.launch = streamer + service + ' | ./' + render # Complete launch string with stream piped out for rendering
        
        self.service_stream = streamer + service # Launch only the streamer without rendering
        self.render = './' + render # Execute the render option

        # Extract the installs option
        # How to get an argument list from an Alistair Cree configuration file:
        # break it down: r'INSTALLED=\([\s\S.^)]*\)'
        # r means raw string
        # INSTALLED=\( means look for a match starting INSTALLED=(
        # [\s\S.^)]* means match all whitespace and non whitespace except )
        # \) means match the closing bracket )
        installed = re.search(r'INSTALLED=\([\s\S.^)]*\)', text)
        # There should only be one match
        self.instr = installed.group(0)
        #print("installed = " + instr) #

# What is our current source?
    
#!/bin/bash
# This file was created automatically by vbit-config.
#INSTALLED=(
#  "Ceefax,/home/peterk/.teletext-services/Ceefax,,svn"
#  "Ceefax (South West),/home/peterk/.teletext-services/Ceefax/regional,Ceefax,svn"
#  "Chunkytext,/home/peterk/.teletext-services/Chunkytext,,git"
#  "SPARK,/home/peterk/.teletext-services/SPARK,,git"
#  "Teefax,/home/peterk/.teletext-services/Teefax,,svn"
#)
#
#SELECTED="SPARK"
    
    
    #print("Home = " + HOME)
    #print("KNOWN = " + KNOWN)
    #print("SERVICESDIR = " + SERVICESDIR)
    #print("CONFIG = " + CONFIG)
    
#c = Config()
