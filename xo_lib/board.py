import numpy as np
from xo_lib.config import BOARD_SIZE

class Board:
    def __init__(self):
        # Initialize an empty board
        # A NxN 2D array using numpy. 
        # 0 represents an empty space, 1 represents 'X', 2 represents 'O'
        self.game_board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)

    def print_board(self):
        # Print the current board to the console with separators ('|') between cells
        # map the numbers to their string representations for readability
        symbols = {0: ' ', 1: 'X', 2: 'O'}
        for row in self.game_board:
            # Convert each value in the row to the corresponding character and join with '|'
            row_str = '|'.join([symbols[val] for val in row])
            print(row_str)
            print("-" * (BOARD_SIZE * 2 - 1)) # separator line between rows

    def is_move_valid(self, move):
        # 3. Check if the requested move is valid
        # The 'move' parameter should be a list containing [row_number, column_number]
        if len(move) != 2:
            return False
        
        row, col = move
        # Check if the coordinates are within the board boundaries
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            # The move is valid only if the spot is empty (contains 0)
            if self.game_board[row, col] == 0:
                return True
        return False

    def perform_move(self, move, player):
        # Perform a valid move on the board for the given player
        if self.is_move_valid(move):
            row, col = move
            self.game_board[row, col] = player
            return True # Returns True if the move was executed successfully
        return False # Returns False otherwise

    def is_winner(self, player):
        # Check if the given player won
        # A win is defined as 3 consecutive marks in a row, column, or diagonal.
        
        # Check rows and columns
        for i in range(BOARD_SIZE):
            if np.all(self.game_board[i, :] == player): # Full row for the player
                return True
            if np.all(self.game_board[:, i] == player): # Full column for the player
                return True

        # Check diagonals
        if np.all(np.diag(self.game_board) == player): # Main diagonal
            return True
        if np.all(np.diag(np.fliplr(self.game_board)) == player): # Secondary diagonal
            return True
            
        return False

    def is_full(self):
        # Check if the board is full (no empty spaces)
        # Returns True if there are no 0s left in the array
        return not np.any(self.game_board == 0)

    def is_tie(self):
        # Check if the game ended in a tie
        # A tie occurs when the board is full and neither player 1 nor player 2 has won
        return self.is_full() and not self.is_winner(1) and not self.is_winner(2)

    def get_empty_places(self):
        # Return a list of all empty places on the board
        # Returns a list of lists containing the coordinates of empty cells
        empty_places = []
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.game_board[i, j] == 0:
                    empty_places.append([i, j])
        return empty_places