import socket

def receive_heartbeat(port):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', port))

    print(f"Listening for heartbeat on port {port}...")

    while True:
        try:
            data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
            print(f"Received heartbeat from {addr}: {data.decode('utf-8')}")
        except Exception as e:
            print(f"Error receiving heartbeat: {e}")

if __name__ == "__main__":
    receive_heartbeat(51800)