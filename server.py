import ssl
import socket
from datetime import datetime
import logging
import time
import traceback
from urllib import parse
from skyron import settings, VERSION
from skyron.gemini import GeminiRequest, GeminiResponse, GeminiException
import sys

# create logger
logger = logging.getLogger('skyron')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

# Create a server socket 
serverSocket = socket.socket()
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((settings['BIND'], settings['PORT']))

# Listen for incoming connections
serverSocket.listen()
print(f"\r\nSkyron {VERSION} is now listening at {settings['BIND']}:{settings['PORT']}.\r\n")

while(True):
    # Keep accepting connections from clients
    (clientConnection, clientAddress) = serverSocket.accept()
    
    # Make the socket connection to the clients secure through SSLSocket
    secureClientSocket = ssl.wrap_socket(clientConnection, 
                                        server_side=True, 
                                        ca_certs="/etc/letsencrypt/live/banjo.town/fullchain.pem", 
                                        certfile="/etc/letsencrypt/live/banjo.town/cert.pem",
                                        keyfile="/etc/letsencrypt/live/banjo.town/privkey.pem", 
                                        cert_reqs=ssl.CERT_NONE,
                                        ssl_version=ssl.PROTOCOL_TLSv1_2)

    url = secureClientSocket.recv(1024).rstrip().decode('UTF-8')
    try:
        req = GeminiRequest(url)
        response = req.dispatch()
        secureClientSocket.send(response.header)
        if response.body is not None:
            logger.info(f"{response.status}\t{url}")
            secureClientSocket.sendall(response.body)
        secureClientSocket.close()

    except GeminiException as e:
        response = e.response()
        secureClientSocket.sendall(response.header)
        logger.error(f"\t{response.status}\t{url}")
        secureClientSocket.close()
    