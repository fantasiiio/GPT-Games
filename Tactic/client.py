import socket

def connect_to_server(server_ip, port=12345):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, port))
        return client_socket
    except Exception as e:
        print(e)
        return None

def player_turn(client_socket):
    # Send START_TURN signal
    client_socket.sendall("START_TURN".encode('utf-8'))

    while True:
        action_data = input("Enter your action (or type 'end' to end your turn): ")

        if action_data.lower() == 'end':
            client_socket.sendall("END_TURN".encode('utf-8'))
            break
        else:
            client_socket.sendall(f"ACTION:{action_data}".encode('utf-8'))
            
            # Here, you can optionally wait and display any counteractions or reactions from the other player
            response = client_socket.recv(1024).decode('utf-8')
            if response.startswith("ACTION:"):
                print(f"Opponent's reaction: {response[7:]}")

server_ip = "127.0.0.1"  # or the actual server IP
client_socket = connect_to_server(server_ip)
if client_socket:
    player_turn(client_socket)
    client_socket.close()                

