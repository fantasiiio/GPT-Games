import math
import sys
import numpy as np
import pygame
import random

# Constants
ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER = 1
AI = 2
EMPTY = 0
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)
WIDTH = COLUMN_COUNT * SQUARESIZE
HEIGHT = (ROW_COUNT+1) * SQUARESIZE
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)



def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT), int)

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def check_winner(board, piece):
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == board[r][c+1] == board[r][c+2] == board[r][c+3] == piece:
                return True
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == board[r+1][c] == board[r+2][c] == board[r+3][c] == piece:
                return True
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3] == piece:
                return True
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == board[r-1][c+1] == board[r-2][c+2] == board[r-3][c+3] == piece:
                return True

def score_position(board, piece):
    score = 0
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    for row in board:
        row_array = [int(i) for i in row]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c+4]
            score += evaluate_window(window, piece)

    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in board[:, c]]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(3, COLUMN_COUNT):
            window = [board[r+i][c-i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER if piece == AI else AI

    if window.count(piece) == 4:
        score += 200
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 20

    return score

def minimax(board, depth, alpha, beta, maximizingPlayer, piece):
    valid_moves = [c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]
    is_terminal = len(valid_moves) == 0 or check_winner(board, PLAYER) or check_winner(board, AI)
    if depth == 0 or is_terminal:
        return None, score_position(board, piece)

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_moves)
        for col in valid_moves:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, piece)
            new_score = minimax(temp_board, depth-1, alpha, beta, False, piece)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:
        value = math.inf
        column = random.choice(valid_moves)
        for col in valid_moves:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, piece)
            new_score = minimax(temp_board, depth-1, alpha, beta, True, piece)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

import pygame.gfxdraw  # Import the gfxdraw module

def draw_board(board, winning_pieces = []):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, (0, 0, 0), (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), int(HEIGHT-int(r*SQUARESIZE+SQUARESIZE/2))), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), int(HEIGHT-int(r*SQUARESIZE+SQUARESIZE/2))), RADIUS)

    for piece in winning_pieces:  # Separate loop for drawing the winning pieces
        r, c = piece  # Unpack the row and column values
        for i in range(1, 4):  # Draw a thicker border
            pygame.gfxdraw.aacircle(screen, int(c*SQUARESIZE+SQUARESIZE/2), int(HEIGHT-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS-i, (0, 0, 139))
            pygame.gfxdraw.circle(screen, int(c*SQUARESIZE+SQUARESIZE/2), int(HEIGHT-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS-i, (0, 0, 139))

    pygame.display.update()



def end_game(winner):
    font = pygame.font.SysFont("monospace", 75)
    winning_pieces = []
    if winner == PLAYER:
        winning_pieces = highlight_winning_pieces(board, PLAYER)
        label = font.render("Player wins!", 1, RED)
    elif winner == AI:
        winning_pieces = highlight_winning_pieces(board, AI)
        label = font.render("AI wins!", 1, YELLOW)
    else:
        label = font.render("Tie game!", 1, (255, 255, 255))
    screen.blit(label, (40,10))
    draw_board(board, winning_pieces)  # Pass the winning_pieces to the draw_board function
    pygame.display.update()
    pygame.time.wait(5000)


def highlight_winning_pieces(board, player):
    winning_pieces = []  # Create an empty list to store the positions of the winning pieces
    for row in range(ROW_COUNT):
        for col in range(COLUMN_COUNT - 3):
            if board[row][col] == player and board[row][col + 1] == player and board[row][col + 2] == player and board[row][col + 3] == player:
                winning_pieces.extend([(row, col), (row, col + 1), (row, col + 2), (row, col + 3)])  # Add the winning positions to the list
    for col in range(COLUMN_COUNT):
        for row in range(ROW_COUNT - 3):
            if board[row][col] == player and board[row + 1][col] == player and board[row + 2][col] == player and board[row + 3][col] == player:
                winning_pieces.extend([(row, col), (row + 1, col), (row + 2, col), (row + 3, col)])
    for row in range(ROW_COUNT - 3):
        for col in range(COLUMN_COUNT - 3):
            if board[row][col] == player and board[row + 1][col + 1] == player and board[row + 2][col + 2] == player and board[row + 3][col + 3] == player:
                winning_pieces.extend([(row, col), (row + 1, col + 1), (row + 2, col + 2), (row + 3, col + 3)])
    for row in range(3, ROW_COUNT):
        for col in range(COLUMN_COUNT - 3):
            if board[row][col] == player and board[row - 1][col + 1] == player and board[row - 2][col + 2] == player and board[row - 3][col + 3] == player:
                winning_pieces.extend([(row, col), (row - 1, col + 1), (row - 2, col + 2), (row - 3, col + 3)])
    return winning_pieces  # Return the list of winning positions

board_history = []

def undo(board_history, turn):
    # Remove the last two board states (AI's move and player's move)
    if len(board_history) >= 2:
        board_history.pop()
        board_history.pop()

    # Set the current board state to the last remaining state in the list
    if board_history:
        return board_history[-1].copy(), turn
    else:
        return create_board(), PLAYER

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.update()

board = create_board()
draw_board(board)
game_over = False
turn = random.choice([PLAYER, AI])

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, WIDTH, SQUARESIZE))
            posx = event.pos[0]
            if turn == PLAYER:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
            else:
                pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)


        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, WIDTH, SQUARESIZE))

            if turn == PLAYER:
                col = int(event.pos[0] // SQUARESIZE)
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER)

                    # Add the current board state to the history
                    board_history.append(board.copy())

                    if check_winner(board, PLAYER):
                        end_game(PLAYER)
                        game_over = True

                turn = AI

        # Handle the undo action (e.g., when the 'U' key is pressed)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u:
                board, turn = undo(board_history, turn)

    if turn == AI and not game_over:
        col, _ = minimax(board, 7, -math.inf, math.inf, True, AI)
        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI)

            # Add the current board state to the history
            board_history.append(board.copy())

            if check_winner(board, AI):
                end_game(AI)
                game_over = True

        turn = PLAYER


    draw_board(board)
    if len([c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]) == 0:
        end_game(0)
        game_over = True     
