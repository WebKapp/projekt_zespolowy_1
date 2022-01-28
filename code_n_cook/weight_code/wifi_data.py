import socket

class Client():
   def __init__(self,Adress=('192.168.8.130', 80)):
      self.socket = socket.socket()
      self.socket.connect(Adress)

def send_data(data:"str"):
   client = Client()
   client.socket.send(data.encode())

