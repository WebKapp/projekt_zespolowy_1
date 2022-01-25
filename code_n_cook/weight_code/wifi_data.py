import socket

class Client():
   def __init__(self,Adress=('192.168.8.129', 80)):
      self.socket = socket.socket()
      self.socket.connect(Adress)

client = Client()

def send_data(data:"str"):
   client.socket.send(data.encode())
