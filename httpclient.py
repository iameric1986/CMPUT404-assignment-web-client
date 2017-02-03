#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):    
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def __init__(self):
        self.host = ""
        self.port = 80 # Default port as given by the socket library example https://docs.python.org/2/howto/sockets.html
        self.path = ""
        self.requestType = ""
        self.connection = None
        self.httpResponse = ""
        self.contentType = "Content-Type: application/x-www-form-urlencoded\r\n" # Per requirements

    def get_host_port(self, url):
        # URL will look like this: http://BASEHOST:BASEPORT/path OR http://BASEHOST OR http://BASEHOST/path
        # Will need to parse and separate the components of the string.
        
        url = url.strip('http:').strip('/') # Remove http:// and terminating '/'

        # Case for BASEHOST only
        if('/' not in url and ':' not in url):
            self.host = url
            self.path = "/"
            return None
        
        # In the case of BASEHOST:BASEPORT/path AND BASEHOST/path there is always a '/' char
        baseURLinfo = url.split('/') # If there is a path then they will be stored in [1:n]
                
        for i in range(1, len(baseURLinfo)):
            self.path += "/" + baseURLinfo[i]
        
        if(self.path == ""): #Set default path for HTTP requests if no path is given in the URL
            self.path = "/"
            
        if (':' not in url): # No port given, use the default port for the socket library (port 80)
            self.host = baseURLinfo[0]
            return None
            
        # Split on the ':' to get the port information
        hostPortInfo = baseURLinfo[0].split(':')
        self.host = hostPortInfo[0]
        self.port = int(hostPortInfo[1]) # Need to cast str back to an int
        return None

    # Ref: Python socket library document
    # URL: https://docs.python.org/2/howto/sockets.html
    # Retrieved: Feb 2, 2017
    def connect(self, host, port):
        # use sockets!
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((host, port))
        return None

    # The code is contained within the header.
    def get_code(self, data):
        header = self.get_headers(data).split("\r\n") # Get and split the header data
        return header[0].split()[1]

    # Get the headers only
    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    # Get the body only
    def get_body(self, data):
        return data.split("\r\n\r\n")[1]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    # I assume that the URL passed in is valid and matches the those in the freetest.py unit tests
    def GET(self, url, args=None):
        self.get_host_port(url)
        self.requestType = "GET %s HTTP/1.1\r\n" %(self.path)        
        httpRequest = self.requestType + "Host: " + self.host + "\r\n" + "Connection: close\r\n\r\n"
        # Convert the mapping into urllib usable string
        # Ref: Python urllib docs
        # URL: https://docs.python.org/2/library/urllib.html
        # Retrieved: Feb 2, 2017
        if(args != None):
            args = urllib.urlencode(args)
            httpRequest += args + "\r\n\r\n"
            
        self.requestHTTPpage(httpRequest)
        print(self.httpResponse) # Send the response to std out
        response = self.parseHTTPresponse()
        self.clearMem()
        return response

    # Same logic as GET but changed the request to POST and added the content-type
    def POST(self, url, args=None):        
        self.get_host_port(url)
        self.requestType = "POST %s HTTP/1.1\r\n" %(self.path)        
        httpRequest = self.requestType + "Host: " + self.host + "\r\n" + self.contentType + "Connection: close\r\n"
        
        if(args != None):
            args = urllib.urlencode(args)
            httpRequest += "Content-Length: %d\r\n\r\n" %(len(args)) + args + "\r\n\r\n" 
        else:
            httpRequest += "Content-Length: 0\r\n\r\n\r\n\r\n"
        
        self.requestHTTPpage(httpRequest)
        print(self.httpResponse) # Send the response to std out
        
        response = self.parseHTTPresponse()
        self.clearMem()
        return response
    
    def requestHTTPpage(self, request):
        try:
            self.connect(self.host, self.port)
        except:
            print("Error occurred while trying to connect")
             
        try:    
            self.connection.sendall(request)
            self.httpResponse = self.recvall(self.connection)
        except:
            print("Error occurred while requesting web page")
        return None
    
    def parseHTTPresponse(self):
        code = int(self.get_code(self.httpResponse)) # Need to cast the code from str back to int
        body = self.get_body(self.httpResponse) # Get the body
        return HTTPResponse(code, body)
    
    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
        
    def clearMem(self):
        self.host = ""
        self.port = 80
        self.path = ""
        self.requestType = ""
        self.connection.close()
        self.connection = None
        self.httpResponse = ""        
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
