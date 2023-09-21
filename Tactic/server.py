import socket

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12345))  # Bind to all available IPs on the machine, port 12345
    server.listen(2)  # Listen for up to 2 connections (for a 2-player game)

    print("Waiting for players to connect...")
    player1, addr1 = server.accept()
    print(f"Player 1 connected from {addr1}")
    
    player2, addr2 = server.accept()
    print(f"Player 2 connected from {addr2}")

    return player1, player2
    
def game_loop(player1, player2):
    while True:
        # Wait for player 1's move
        move1 = player1.recv(1024).decode('utf-8')
        if not move1:
            break

        # Send player 1's move to player 2 and wait for response
        player2.sendall(move1.encode('utf-8'))
        move2 = player2.recv(1024).decode('utf-8')
        if not move2:
            break

        # Send player 2's move to player 1
        player1.sendall(move2.encode('utf-8'))

    player1.close()
    player2.close()

player1, player2 = start_server()
game_loop(player1, player2)
    
