import socket
import time

rpi1 = socket.socket()
rpi2 = socket.socket()
#rpi3 = socket.socket()
rpi1.connect(('192.168.0.150', 9090))
rpi2.connect(('192.168.0.150', 9090))
#rpi3.connect(('192.168.0.150', 9090))
print(rpi1.recv(1024).decode())
print(rpi2.recv(1024).decode())
#print(rpi3.recv(1024).decode())

input('Press enter to start')
start_time = time.time()
rpi1.send(str(start_time).encode())
rpi2.send(str(start_time).encode())
#rpi3.send(str(start_time).encode())
