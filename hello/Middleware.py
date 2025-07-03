import socket
from datetime import datetime

# Step 1: Define host and port
HOST = '127.0.0.1'  # Listen on all available network interfaces
PORT = 5500       # Port to listen on (must match the sender's port)

# Step 2: Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Step 3: Bind the socket to the host and port
server_socket.bind((HOST, PORT))
print(f"Server listening on {HOST}:{PORT}")

# Step 4: Start listening for incoming connections
server_socket.listen(5)  # Allows up to 5 simultaneous connections

while True:
    # Step 5: Accept a connection from a client (POCT device)
    client_socket, client_address = server_socket.accept()
    print(f"Connection received from {client_address}")
    received_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log the message with the timestamp
   

    # Step 6: Receive data from the client
    data = client_socket.recv(1024)  # Receive up to 1024 bytes
    if data:
        #print(f"Data received: {data.decode()}")  # Decode and print the received message
        print(f"Message received at {received_time}:\n{data.decode()}")
        # Step 7: Send acknowledgment back to the client (if needed)
        client_socket.send(b"ACK")  # Acknowledge receipt of data

    # Step 8: Close the connection
    client_socket.close()
    print("Connection closed.")
