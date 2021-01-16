import ssl
import socket
import datetime
import time
import traceback
from urllib import parse
from skyron import settings
from skyron.gemini import GeminiRequest, GeminiResponse


req = GeminiRequest('gemini://0.0.0.0/index.gmi')




HOST   = "127.0.0.1"
PORT        = 1965
DOC_ROOT = '/home/skyron/skyron-dev/gmi_docs'

# Create a server socket 
serverSocket = socket.socket()
serverSocket.bind((settings['HOST'], settings['PORT']))

# Listen for incoming connections
serverSocket.listen()
print(f"Server listening at {settings['HOST']}:{settings['PORT']}")

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
    req = GeminiRequest(url)
    response = req.handle()
    secureClientSocket.send(response.header)
    secureClientSocket.sendall(response.body)
    secureClientSocket.close()
    