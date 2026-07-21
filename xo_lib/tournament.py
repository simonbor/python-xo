import json
import numpy as np
from xo_lib.game import Game
from config import (
    WIN_SCORE,
    TIE_SCORE,
    LOOSE_SCORE,
    JSON_FILE_NAME,
    SAVE_SCOREBOARDS,
)

class Tournament:
    def __init__(self, player1_type, player2_type, num_games, gamma):
        # 1. Initialize attributes
        # Store the types of the two players (e.g., Human or Random)
        self.player1_type = player1_type
        self.player2_type = player2_type
        
        # Store the total number of games to be played in becoming tournament
        self.num_games = num_games
        self.gamma = gamma
        self.scoreboards = self.load_scoreboards(JSON_FILE_NAME)

        # Dictionary to store the tournament results (wins for each player and ties)
        # Based on the Game class, Player 1 is always 'X' and Player 2 is always 'O'
        self.results = {
            'X': 0,    # Wins for Player 1
            'O': 0,    # Wins for Player 2
            'Tie': 0   # Number of tied games
        }
    
    # load and return JSON from a proj file
    def load_scoreboards(self, json_file_name):
        try:
            with open(json_file_name, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    # Checks if a board state, or any of its rotations, already exists in the scoreboards.
    def _does_board_exist(self, board):
        # Generate and check keys for all 4 rotations
        for i in range(4):
            rotated_board = np.rot90(board, k=i)
            rotated_key = "".join(map(str, rotated_board.flatten()))
            if rotated_key in self.scoreboards:
                return rotated_key
        return ""

    # update the boards in the scoreboards with a count and score per each board
    def update_scoreboards(self, game_history):
        for row in game_history:
            value = row["gm"]
            existing_key = Game.get_optimized_board(row["bd"], self.scoreboards)

            if (existing_key == ""):
                key = "".join(str(item) for sublist in row["bd"] for item in sublist)
                self.scoreboards[key] = [value, 1]
            elif (value in {WIN_SCORE, TIE_SCORE, LOOSE_SCORE}):
                scoreBoard = self.scoreboards[existing_key]
                scoreBoard[1] = scoreBoard[1] + 1
                self.scoreboards[existing_key] = scoreBoard
            else:
                scoreBoard = self.scoreboards[existing_key]
                scoreBoard[0] = ((scoreBoard[0] * scoreBoard[1]) + value) / (scoreBoard[1] + 1)
                scoreBoard[1] = scoreBoard[1] + 1
                self.scoreboards[existing_key] = scoreBoard

    # store the self.scoreboards to file data.json
    def save_scoreboards(self):
        if (not SAVE_SCOREBOARDS):
            return
        
        with open(JSON_FILE_NAME, 'w') as file:
            # further param indent=4 makes the JSON file formatted for easy read
            json.dump(self.scoreboards, file)

    def start_a_tournament(self):
        # 2. Run the tournament
        # Run the specified number of games between the players
        for current_game in range(self.num_games):
            print(f"\n--- Starting Game {current_game + 1} of {self.num_games} ---")
            
            # Create a fresh instance of the Game for each round
            game = Game(self.player1_type, self.player2_type, self.gamma, WIN_SCORE, TIE_SCORE, LOOSE_SCORE, self.scoreboards)
            
            # Play the game and get the result ('X', 'O', or 'Tie')
            winner = game.play_game()
            self.results[winner] += 1
            self.update_scoreboards(game.game_history)

        self.save_scoreboards()

    # 3. Print the tournament results in an organized way
    def print_results(self):
        print("\n" + "="*30)
        print("     TOURNAMENT RESULTS     ")
        print("="*30)
        print(f"Total Games Played: {self.num_games}")
        print("-" * 30)
        print(f"Player 1 ('X') Wins : {self.results['X']}")
        print(f"Player 2 ('O') Wins : {self.results['O']}")
        print(f"Ties                : {self.results['Tie']}")
        print("="*30)