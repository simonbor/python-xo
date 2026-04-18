import numpy as np
import random

# Global variable defining the board size (NxN).
# You can change it to 4, 5, or any other integer to play on a larger board!
BOARD_SIZE = 5

class Tournament:
    def __init__(self, player1_type, player2_type, num_games):
        # 1. Initialize attributes
        # Store the types of the two players (e.g., Human or Random)
        self.player1_type = player1_type
        self.player2_type = player2_type
        
        # Store the total number of games to be played in the tournament
        self.num_games = num_games
        
        # Dictionary to store the tournament results (wins for each player and ties)
        # Based on the Game class, Player 1 is always 'X' and Player 2 is always 'O'
        self.results = {
            'X': 0,    # Wins for Player 1
            'O': 0,    # Wins for Player 2
            'Tie': 0   # Number of tied games
        }

    def start_a_tournament(self):
        # 2. Run the tournament
        # Run the specified number of games between the players
        for current_game in range(self.num_games):
            print(f"\n--- Starting Game {current_game + 1} of {self.num_games} ---")
            
            # Create a fresh instance of the Game for each round
            game = Game(self.player1_type, self.player2_type)
            
            # Play the game and get the result ('X', 'O', or 'Tie')
            winner = game.play_game()
            
            # Update the results dictionary with the outcome of the current game
            if winner == 'X':
                self.results['X'] += 1
            elif winner == 'O':
                self.results['O'] += 1
            else:
                self.results['Tie'] += 1

    def print_results(self):
        # 3. Print the tournament results in an organized way
        print("\n" + "="*30)
        print("     TOURNAMENT RESULTS     ")
        print("="*30)
        print(f"Total Games Played: {self.num_games}")
        print("-" * 30)
        print(f"Player 1 ('X') Wins : {self.results['X']}")
        print(f"Player 2 ('O') Wins : {self.results['O']}")
        print(f"Ties                : {self.results['Tie']}")
        print("="*30)

class Game:
    # Constants for player types
    HUMAN_PLAYER = 1
    RANDOM_PLAYER = 2

    def __init__(self, player1_type, player2_type):
        # 1. Initialization
        # board: An instance of the Board class
        self.board = Board()
        
        # player1/player2: Values representing the type of players (Human or Random)
        self.player1 = player1_type
        self.player2 = player2_type
        
        # current_player: The sign of the current player ('X' or 'O').
        # player1 will always be the first and gets the marker 'X'
        self.current_player = 'X'

    def play_human_turn(self, sign):
        # 3. Run a human player's turn
        # Get the integer representation for the Board class (1 for 'X', 2 for 'O')
        player_num = 1 if sign == 'X' else 2
        
        while True:
            try:
                # Ask the human player for row and column
                user_input = input(f"Player {sign}, enter row and column separated by a space (e.g., '0 1'): ")
                row, col = map(int, user_input.split())
                move = [row, col]
                
                # Try to perform the move on the board
                if self.board.perform_move(move, player_num):
                    break # Move was successful and valid
                else:
                    print("Invalid move. The cell might be taken or out of bounds. Try again.")
            except ValueError:
                print("Invalid input format. Please enter two numbers separated by a space.")

    def play_random_turn(self, sign):
        # 4. Run a random player's turn
        # Get the integer representation for the Board class
        player_num = 1 if sign == 'X' else 2
        
        # Get a list of available empty places
        empty_places = self.board.get_empty_places()
        
        if empty_places:
            # Randomly choose an empty cell and place the sign
            move = random.choice(empty_places)
            self.board.perform_move(move, player_num)
            print(f"Random player {sign} played at row {move[0]}, col {move[1]}")

    # --- Helper Functions (as suggested in the instructions) ---

    def _execute_turn(self):
        # Helper function: Executes the current player's turn
        current_type = self.player1 if self.current_player == 'X' else self.player2
        
        if current_type == self.HUMAN_PLAYER:
            self.play_human_turn(self.current_player)
        elif current_type == self.RANDOM_PLAYER:
            self.play_random_turn(self.current_player)

    def _check_game_over_and_show_result(self):
        # Helper function: Checks if the game ended (win or tie) and displays the result
        player_num = 1 if self.current_player == 'X' else 2
        
        if self.board.is_winner(player_num):
            print(f"\n*** Player {self.current_player} wins! ***\n")
            return True
        
        if self.board.is_tie():
            print("\n*** The game ended in a tie! ***\n")
            return True
            
        return False

    # -----------------------------------------------------------

    def play_game(self):
        # 2. Main game loop
        # Runs the main game loop until the game ends and returns the winner
        print("Game Started!")
        #self.board.print_board()

        while True:
            # Execute the turn for the current player
            self._execute_turn()
            
            # Show the board after the move
            self.board.print_board()

            # Check if the game is over
            if self._check_game_over_and_show_result():
                # Return the winner ('X' or 'O') or 'Tie'
                player_num = 1 if self.current_player == 'X' else 2
                if self.board.is_winner(player_num):
                    return self.current_player
                else:
                    return "Tie"
            
            # Switch turns for the next loop iteration
            self.current_player = 'O' if self.current_player == 'X' else 'X'

class Board:
    def __init__(self):
        # 1. Initialize an empty board
        # A NxN 2D array using numpy. 
        # 0 represents an empty space, 1 represents 'X', 2 represents 'O'
        self.game_board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)

    def print_board(self):
        # 2. Print the current board to the console with separators ('|') between cells
        # map the numbers to their string representations for readability
        symbols = {0: ' ', 1: 'X', 2: 'O'}
        for row in self.game_board:
            # Convert each value in the row to the corresponding character and join with '|'
            row_str = '|'.join([symbols[val] for val in row])
            print(row_str)
            print("-" * (BOARD_SIZE * 2 - 1)) # Separator line between rows

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
        # 4. Perform a valid move on the board for the given player
        if self.is_move_valid(move):
            row, col = move
            self.game_board[row, col] = player
            return True # Returns True if the move was executed successfully
        return False # Returns False otherwise

    def is_winner(self, player):
        # 5. Check if the given player won
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
        # 6. Check if the board is full (no empty spaces)
        # Returns True if there are no 0s left in the array
        return not np.any(self.game_board == 0)

    def is_tie(self):
        # 7. Check if the game ended in a tie
        # A tie occurs when the board is full and neither player 1 nor player 2 has won
        return self.is_full() and not self.is_winner(1) and not self.is_winner(2)

    def get_empty_places(self):
        # 8. Return a list of all empty places on the board
        # Returns a list of lists containing the coordinates of empty cells
        empty_places = []
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.game_board[i, j] == 0:
                    empty_places.append([i, j])
        return empty_places

if __name__ == "__main__":
    # Example: Run a tournament of N games between two Random players
    # Using the constants we defined in the Game class (Game.RANDOM_PLAYER = 2)
    tic_tac_toe = Tournament(player1_type=2, player2_type=2, num_games=1)
    
    # Start the tournament
    tic_tac_toe.start_a_tournament()
    
    # Print the final summary
    tic_tac_toe.print_results()
    