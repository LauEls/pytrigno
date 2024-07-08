import socket

comm_socket = socket.create_connection(("192.168.152.1", 50040), 10)
emg_data_socket = socket.create_connection(("192.168.152.1", 50043), 10)

comm_socket.send('START\r\n\r\n'.encode())

for i in range(100000):
    print(emg_data_socket.recv(1024)[0])

comm_socket.send('STOP'.encode())