import random
from xo_lib.board import Board
from config import (
    RANDOM_SMART_RATIO,
    PRINT_BOARDS,
    PRINT_SCORE_HISTORY
)

class Game:
    # Constants for player types
    HUMAN_PLAYER = 1
    RANDOM_PLAYER = 2
    SMART_AGENT = 3

    def __init__(self, player1_type, player2_type, gamma, win_score, tie_score, loose_score, score_boards):
        self.board = Board()
        self.player1 = player1_type
        self.player2 = player2_type

        self.win_score = win_score
        self.tie_score = tie_score 
        self.loose_score = loose_score 
        self.gamma = gamma # decision rate

        self.game_history = []
        self.score_boards = score_boards

        # current_player: The sign of the current player ('X' or 'O').
        # player1 will always be the first and gets the marker 'X'
        self.current_player = 'X'

    def play_human_turn(self, sign):
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
        player_num = 1 if sign == 'X' else 2
        empty_places = self.board.get_empty_places()
        
        # Randomly choose an empty cell and place the sign
        if empty_places:
            move = random.choice(empty_places)
            self.board.perform_move(move, player_num)
            print(f"Random player {sign} played at row {move[0]}, col {move[1]}")

    def play_smart_agent_turn(self, sign, dictionary):
        player_num = 1 if sign == 'X' else 2
        empty_places = self.board.get_empty_places()
        
        if not empty_places:
            return None

        # to make the game more dynamic and less predictable
        # calculate the move by a correlation between random and smart decision 
        if random.random() < RANDOM_SMART_RATIO:
            move = random.choice(empty_places)
        else:
            move = self.smart_decision(sign, dictionary)
            
        self.board.perform_move(move, player_num)
        print(f"Smart agent {sign} played at row {move[0]}, col {move[1]}")

    # Determine the right move for the smart agent
    def smart_decision(self, sign, dictionary):
        player_num = 1 if sign == 'X' else 2
        empty_places = self.board.get_empty_places()
        best_move = None
        # Initialize best_score to negative infinity so any valid score will be higher
        best_score = -float('inf') if(player_num == 1) else float('inf') 
        

        # Evaluate every possible move (every empty cell)
        for move in empty_places:
            # Create a simulation of the board to test the move
            simulated_board = self.board.game_board.copy()
            simulated_board[move[0], move[1]] = player_num

            # generate string key from 2D array board values
            key = "".join(str(item) for sublist in simulated_board.tolist() for item in sublist)

            # if the board state exists, retrieve its score
            score = dictionary[key][0] if key in dictionary else 0

            # If this move results in a better score, update the best score and best move
            if player_num == 1: # Maximize score for player 1 ('X')
                if score > best_score:
                    best_score = score
                    best_move = move
            else: # Minimize score for player 2 ('O')
                if score < best_score:
                    best_score = score
                    best_move = move

        return best_move

    # --- Helper Functions (as suggested in the instructions) ---

    # Helper function: Executes the current player's turn
    def _execute_turn(self):
        current_type = self.player1 if self.current_player == 'X' else self.player2
        
        if current_type == self.HUMAN_PLAYER:
            self.play_human_turn(self.current_player)
        elif current_type == self.RANDOM_PLAYER:
            self.play_random_turn(self.current_player)
        elif current_type == self.SMART_AGENT:
            self.play_smart_agent_turn(self.current_player, self.score_boards)

    # Helper function: Checks if the game ended (win or tie) and displays the result
    def _check_game_over_and_show_result(self):
        player_num = 1 if self.current_player == 'X' else 2
        
        if self.board.is_winner(player_num):
            print(f"\n*** Player {self.current_player} wins! ***\n")
            return True
        
        if self.board.is_tie():
            print("\n*** The game ended in a tie! ***\n")
            return True
            
        return False

    # decision rate (gamma) calculation per each board by reverse order 
    def update_scores(self):
        prev_board_gamma = 0
        game_history_length = len(self.game_history)

        if(PRINT_SCORE_HISTORY): print("\nThe game_history image after calculation:\n")
        for index, row in enumerate(reversed(self.game_history)):
            # don't change gamma value in the last board
            if (game_history_length - index) != game_history_length: 
                row['gm'] = prev_board_gamma * self.gamma
            prev_board_gamma = row['gm']
            if (PRINT_SCORE_HISTORY): print(row)

    # -----------------------------------------------------------

    def play_game(self):
        # 2. Main game loop
        # Runs the main game loop until the game ends and returns the winner
        print("Game Started!")
        self.game_history.clear()
        winner = ''

        while True:
            # Execute the turn for the current player
            self._execute_turn()
            
            # Show the board after the move
            if(PRINT_BOARDS): self.board.print_board()

            # Check if the game is over
            if self._check_game_over_and_show_result():
                # Return the winner ('X' or 'O') or 'Tie'
                player_num = 1 if self.current_player == 'X' else 2
                if self.board.is_winner(player_num):
                    grade = self.win_score if self.current_player == 'X' else self.loose_score
                    winner = self.current_player
                else:
                    grade = self.tie_score
                    winner = "Tie"

                self.game_history.append({'bd': self.board.game_board.tolist(), 'gm': grade})
                self.update_scores()
                return winner
            
            # Switch turns for the next loop iteration
            self.current_player = 'O' if self.current_player == 'X' else 'X'

            # save turns (boards)
            self.game_history.append({'bd': self.board.game_board.tolist()})