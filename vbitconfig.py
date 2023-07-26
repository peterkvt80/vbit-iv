# vbit-config.py
# Reads vbit2 config to set up suitable launch command strings
#
# Copyright (c) 2020-2021 Peter Kwan
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
import json
class Config:
    def __init__(self):
        # Get the sources
        self.HOME = str(Path.home())
        self.KNOWN = self.HOME + "/vbit2/known_services"
        self.SERVICESDIR = self.HOME+ "/.teletext-services"
        self.CONFIG = self.SERVICESDIR + "/config.json"
        with open(self.CONFIG, 'r') as f:
          config_data = json.load(f)

        # Output: {'name': 'Bob', 'languages': ['English', 'French']}
        #print(data)
        service_name = config_data['settings']['selected'] # eg. Ceefax (London)
        #service = look for service_name in config_data installed
        service_data = list(filter(lambda x:x['name']==service_name, config_data['installed']))
        print (service_data)
        
        self.service = service_name
        
        path = service_data[0]['path']
        
        # Create the launch string. It should look something like this:
        # /home/peterk/vbit2/vbit2 --dir /home/peterk/.teletext-services/Teefax | ./vbit-iv.py 1 0
        streamer = self.HOME + '/vbit2/vbit2 ' # Run vbit ...
        service = ' --dir ' + path # using this service ...
        render = 'vbit-iv.py 1 0' # into a renderer
        self.launch = streamer + service + ' | ./' + render # Complete launch string with stream piped out for rendering

        self.service_stream = streamer + service # Launch only the streamer without rendering
        self.render = './' + render # Execute the render option

# What is our current source?
    
#c = Config()
