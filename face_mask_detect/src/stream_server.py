#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" 
    Social-Distancing: Streaming http multipart jpeg/json server 
   
    IIT : Istituto italiano di tecnologia
    Pattern Analysis and Computer Vision (PAVIS) research line

    Disclaimer:
    The information and content provided by this application is for information purposes only. 
    You hereby agree that you shall not make any health or medical related decision based in whole 
    or in part on anything contained within the application without consulting your personal doctor.

    The software is provided "as is", without warranty of any kind, express or implied, 
    including but not limited to the warranties of merchantability, 
    fitness for a particular purpose and noninfringement. In no event shall the authors, 
    PAVIS or IIT be liable for any claim, damages or other liability, whether in an action of contract, 
    tort or otherwise, arising from, out of or in connection with the software 
    or the use or other dealings in the software.

    LICENSE:
    This project is licensed under the terms of the MIT license.
    This project incorporates material from the projects listed below (collectively, "Third Party Code").  
    This Third Party Code is licensed to you under their original license terms.  
    We reserves all other rights not expressly granted, whether by implication, estoppel or otherwise.

    The software can be freely used for any non-commercial applications and it is useful
    for the automatic early-screening of fever symptoms. The code is open and can be 
    improved with your support, please contact us at socialdistancing@iit.it if you want to help us.
"""

import os
import sys
import time
from sys import platform
import socket
import threading
import queue
import signal
import datetime
from turbojpeg import TurboJPEG, TJPF_GRAY, TJSAMP_GRAY, TJFLAG_PROGRESSIVE
import json
import threading
import glob

'''
    StreamServer class, send images/json to remote clients
'''
class StreamServer:
    '''
        Initialize Video server with port and queue_list
    '''
    def __init__(self, port, queue_list, mt):
        self.port = port
        self.queue_list = queue_list
        self.run = True
        self.mt = mt

    '''
        Activate litening
    '''
    def activate(self):
        self.run = True
         # Start listen thread
        threading.Thread(target=self.listen).start()

    '''
        Stop listening
    '''
    def disconnect(self):
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
        self.run = False

    '''
        Listen thermal from network
    '''
    def listen(self):
        # Create server socket
        port = self.port
          
        # Configure server and reuse address
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('127.0.0.1', port))
        self.s.listen()

        # Wait for new connections
        while self.run:
            try:
                # Wait new connection
                c, addr = self.s.accept()
                
                # Print connection
                print("Connection from {0} to local port {1}".format(addr, self.port), flush=True)

                # Create new sending client queue
                q = queue.Queue(256)

                # Add queue to queue clients list
                self.queue_list.append(q)

                # Crete new server thread
                threading.Thread(target=self.client_handler, args=(c,q,)).start()
            except socket.error as e:
                print ("Error while listening :{0}".format(e), flush=True)

        print("Server on {0} listen stop".format(self.port), flush=True)

    '''
        Send images over network
    '''
    def client_handler(self, c, q):
        # print("INSIDE CLIENT HANDLER")
        # Read request from remote web client
        data = c.recv(1024)

        # Decode data to eventually use it
        data = data.decode("UTF-8")

        # Print received data
        print(data)

        # Create a fake header to send to remote client
        response = "HTTP/1.0 200 OK\r\n" \
                    "Cache-Control: no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0\r\n" \
                    "Pragma: no-cache\r\n" \
                    "Expires: Thu, 01 Dec 1994 16:00:00 GMT\r\n" \
                    "Access-Control-Allow-Origin: http://127.0.0.1:8000\r\n" \
                    "Connection: close\r\n" \
                    "Content-Type: multipart/x-mixed-replace; boundary=myboundary\r\n\r\n"

        # Print sending response
        print(response)

        # Send header
        c.send(bytes(response, "UTF-8"))

        # While module run, send images to remote client
        while self.run:
            # Read image from queue
            try:
                block = q.get(True, 0.5)
            except queue.Empty:
                continue

            # Create image header to client response
            response = "--myboundary\r\n" \
                        "X-TimeStamp: " + str(block[0]) + "\r\n" \
                        "Content-Type: " + self.mt + "\r\n" \
                        "Content-Length: " + str(len(block[1])) + "\r\n\r\n"
                       

            # Print multipart response
            print(response)
            
            # Try to send data until socket is valid
            try:
                c.send(bytes(response, "UTF-8"))
            except socket.error as e:
                print(e, flush=True)
                break

            # Try to send data until socket is valid
            try:
                c.send(block[1])
            except socket.error as e:
                print(e, flush=True)
                break
    
        # Remove Id from queue
        self.queue_list.remove(q)

        # Close connection
        c.close()

        print('Client handler closed')
