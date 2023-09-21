class Othello:
    def __init__(self):
        # 0 for empty, 1 for player 1, and 2 for player 2
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        # Initial setup
        self.board[3][3], self.board[3][4] = 1, 2
        self.board[4][3], self.board[4][4] = 2, 1
        self.current_player = 1

    def display_board(self):
        for row in self.board:
            print(' '.join(['-' if cell == 0 else 'X' if cell == 1 else 'O' for cell in row]))
        print()

    def get_valid_moves(self, player):
        valid_moves = []
        for x in range(8):
            for y in range(8):
                if self.is_valid_move(x, y, player):
                    valid_moves.append((x, y))
        return valid_moves

    def is_valid_move(self, x, y, player):
        # Check if cell is empty and lies within the board
        if self.board[x][y] != 0 or x < 0 or x >= 8 or y < 0 or y >= 8:
            return False

        # Directions to check
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dx, dy in directions:
            temp_x, temp_y = x + dx, y + dy
            if 0 <= temp_x < 8 and 0 <= temp_y < 8 and self.board[temp_y][temp_x] == 3 - player:
                while 0 <= temp_x < 8 and 0 <= temp_y < 8:
                    if self.board[temp_y][temp_x] == 0:
                        break
                    if self.board[temp_y][temp_x] == player:
                        return True
                    temp_x += dx
                    temp_y += dy

        return False

    def make_move(self, x, y, player):
        if not self.is_valid_move(x, y, player):
            return False

        self.board[y][x] = player
        # Directions
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dx, dy in directions:
            temp_x, temp_y = x + dx, y + dy
            if 0 <= temp_x < 8 and 0 <= temp_y < 8 and self.board[temp_y][temp_x] == 3 - player:
                while 0 <= temp_x < 8 and 0 <= temp_y < 8:
                    if self.board[temp_y][temp_x] == 0:
                        break#
                    if self.board[temp_y][temp_x] == player:
                        while True:
                            temp_x -= dx
                            temp_y -= dy
                            if temp_x == x and temp_y == y:
                                break
                            self.board[temp_y][temp_x] = player
                        break
                    temp_x += dx
                    temp_y += dy

        return True

    def has_valid_moves(self, player):
        for x in range(8):
            for y in range(8):
                if self.is_valid_move(x, y, player):
                    return True
        return False

    def switch_player(self):
        self.current_player = 3 - self.current_player

    def get_winner(self):
        counts = [0, 0, 0]  # Empty, Player 1, Player 2
        for row in self.board:
            for cell in row:
                counts[cell] += 1

        if counts[1] > counts[2]:
            return 1
        elif counts[2] > counts[1]:
            return 2
        return 0  # Draw



def play_game():
    game = Othello()
    while True:
        game.display_board()
        move_made = False
        while not move_made:
            try:
                print(f"valid moves: {game.get_valid_moves(game.current_player)}")  
                x, y = map(int, input(f"Player {game.current_player}'s move (x y): ").split())
                if game.make_move(x, y, game.current_player):
                    move_made = True
                else:
                    print("Invalid move. Try again.")
            except (ValueError, IndexError):
                print("Invalid input. Please enter your move as two numbers separated by a space (e.g., '4 5').")
        if not game.has_valid_moves(3 - game.current_player):
            if not game.has_valid_moves(game.current_player):
                break
        game.switch_player()

    winner = game.get_winner()
    if winner == 0:
        print("It's a draw!")
    else:
        print(f"Player {winner} wins!")

if __name__ == "__main__":
    play_game()
