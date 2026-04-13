import socket

def send_and_receive(server_ip, server_port, raw_message, local_ip, local_port, buffer_size=1024):
    """
    Uses a single UDP socket to send and then receive a response.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # 绑定到本地端口
            sock.bind((local_ip, local_port))

            # 发送消息
            sock.sendto(raw_message.encode('utf-8'), (server_ip, server_port))
            print(f"Sent: {raw_message}")

            # 等待服务器回复
            data, addr = sock.recvfrom(buffer_size)
            response = data.decode('utf-8')
            print(f"Received: {response}")
            return response
    except Exception as e:
        print(f"Error sending/receiving message: {e}")
        return None

if __name__ == "__main__":
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 8889
    CLIENT_IP = "127.0.0.1"
    CLIENT_PORT = 7777

    # Get user input for arm index
    arm_index = int(input("Enter the arm index (0-99): "))

    # Validate input range
    if arm_index < 0 or arm_index > 99:
        print("Error: arm index must be between 0 and 99")
        exit(1)

    # Combine JSON objects with proper f-string formatting
    combined_json_string = f"""{{
        "selectCmd": {{
            "armIndex": {arm_index},
            "leftHandIndex": 0,
            "rightHandIndex": 0,
            "soundIndex": 0,
            "emojIndex": 0
        }}
    }}"""

    print("Sending and waiting for server response...")

    response = send_and_receive(SERVER_IP, SERVER_PORT, combined_json_string, CLIENT_IP, CLIENT_PORT)
    if response:
        print(f"Server responded with: {response}")

