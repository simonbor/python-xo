import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import io

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.modules['tensorflow'] = MagicMock()
sys.modules['tensorflow.keras'] = MagicMock()
sys.modules['tensorflow.keras.models'] = MagicMock()
from xo_lib import Game, Board

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game(
            player1_type=Game.HUMAN_PLAYER,
            player2_type=Game.RANDOM_PLAYER,
            gamma=0.9,
            win_score=1,
            tie_score=0.5,
            loose_score=0.1,
            score_boards={}
        )

    def test_init(self):
        self.assertIsInstance(self.game.board, Board)
        self.assertEqual(self.game.player1, Game.HUMAN_PLAYER)
        self.assertEqual(self.game.player2, Game.RANDOM_PLAYER)
        self.assertEqual(self.game.gamma, 0.9)
        self.assertEqual(self.game.win_score, 1.0)
        self.assertEqual(self.game.tie_score, 0.5)
        self.assertEqual(self.game.loose_score, 0.1)
        self.assertEqual(self.game.game_history, [])
        self.assertEqual(self.game.current_player, 'X')

    @patch('builtins.input', side_effect=['0 1'])
    def test_play_human_turn_valid(self, mock_input):
        self.game.play_human_turn('X')
        self.assertEqual(self.game.board.game_board[0, 1], 1)

    @patch('builtins.input', side_effect=['invalid', '1 1'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_play_human_turn_invalid_format(self, mock_stdout, mock_input):
        self.game.play_human_turn('O')
        self.assertEqual(self.game.board.game_board[1, 1], 2)
        output = mock_stdout.getvalue()
        self.assertIn("Invalid input format", output)

    @patch('builtins.input', side_effect=['0 0', '0 1'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_play_human_turn_invalid_move(self, mock_stdout, mock_input):
        self.game.board.game_board[0, 0] = 2 # Spot taken
        self.game.play_human_turn('X')
        self.assertEqual(self.game.board.game_board[0, 1], 1) # Next move is executed
        output = mock_stdout.getvalue()
        self.assertIn("Invalid move", output)

    @patch('random.choice', return_value=[2, 2])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_play_random_turn(self, mock_stdout, mock_choice):
        self.game.play_random_turn('X')
        self.assertEqual(self.game.board.game_board[2, 2], 1)
        output = mock_stdout.getvalue()
        self.assertIn("Random player X played", output)

    @patch('random.choice')
    def test_play_random_turn_no_empty(self, mock_choice):
        self.game.board.game_board.fill(1) # Board full
        self.game.play_random_turn('O')
        mock_choice.assert_not_called()

    def test_smart_decision_empty_dict(self):
        # With an empty dictionary, all moves have a score of 0.
        # It should pick the first evaluated move.
        move = self.game.smart_decision('X', {})
        self.assertEqual(move, [0, 0])

    def test_smart_decision_with_scores(self):
        # Mocking a dictionary where [1, 1] gives the highest score
        sim_board1 = np.zeros((3, 3), dtype=int)
        sim_board1[0, 0] = 1
        key1 = "".join(str(item) for sublist in sim_board1.tolist() for item in sublist)

        sim_board2 = np.zeros((3, 3), dtype=int)
        sim_board2[1, 1] = 1
        key2 = "".join(str(item) for sublist in sim_board2.tolist() for item in sublist)

        dictionary = {
            key1: [0.2, 1], 
            key2: [0.9, 1]
        }
        
        move = self.game.smart_decision('X', dictionary)
        self.assertEqual(move, [1, 1])

    def test_smart_decision_no_moves(self):
        self.game.board.game_board.fill(1) # Board full
        move = self.game.smart_decision('X', {})
        self.assertIsNone(move)

    @patch.object(Game, 'play_human_turn')
    def test_execute_turn_human(self, mock_play_human):
        self.game.current_player = 'X'
        self.game.player1 = Game.HUMAN_PLAYER
        self.game._execute_turn()
        mock_play_human.assert_called_once_with('X')

    @patch.object(Game, 'play_random_turn')
    def test_execute_turn_random(self, mock_play_random):
        self.game.current_player = 'O'
        self.game.player2 = Game.RANDOM_PLAYER
        self.game._execute_turn()
        mock_play_random.assert_called_once_with('O')

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_check_game_over_win(self, mock_stdout):
        self.game.current_player = 'X'
        self.game.board.is_winner = MagicMock(return_value=True)
        result = self.game._check_game_over_and_show_result()
        self.assertTrue(result)
        self.assertIn("*** Player X wins! ***", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_check_game_over_tie(self, mock_stdout):
        self.game.board.is_winner = MagicMock(return_value=False)
        self.game.board.is_tie = MagicMock(return_value=True)
        result = self.game._check_game_over_and_show_result()
        self.assertTrue(result)
        self.assertIn("*** The game ended in a tie! ***", mock_stdout.getvalue())

    def test_check_game_over_none(self):
        self.game.board.is_winner = MagicMock(return_value=False)
        self.game.board.is_tie = MagicMock(return_value=False)
        result = self.game._check_game_over_and_show_result()
        self.assertFalse(result)

    def test_update_scores(self):
        self.game.game_history = [
            {'bd': [[0,0,0],[0,0,0],[0,0,0]]},
            {'bd': [[1,0,0],[0,0,0],[0,0,0]]},
            {'bd': [[1,2,0],[0,0,0],[0,0,0]], 'gm': 1.0}
        ]
        self.game.update_scores()
        
        self.assertEqual(self.game.game_history[2]['gm'], 1.0)
        self.assertEqual(self.game.game_history[1]['gm'], 0.9)
        self.assertAlmostEqual(self.game.game_history[0]['gm'], 0.81)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_play_game_win(self, mock_stdout):
        self.game._execute_turn = MagicMock()
        self.game._check_game_over_and_show_result = MagicMock(return_value=True)
        self.game.board.is_winner = MagicMock(return_value=True)
        self.game.current_player = 'X'

        winner = self.game.play_game()
        self.assertEqual(winner, 'X')
        self.assertEqual(len(self.game.game_history), 1)
        self.assertEqual(self.game.game_history[0]['gm'], self.game.win_score)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_play_game_tie(self, mock_stdout):
        self.game._execute_turn = MagicMock()
        self.game._check_game_over_and_show_result = MagicMock(return_value=True)
        self.game.board.is_winner = MagicMock(return_value=False)
        self.game.current_player = 'X'

        winner = self.game.play_game()
        self.assertEqual(winner, 'Tie')
        self.assertEqual(len(self.game.game_history), 1)
        self.assertEqual(self.game.game_history[0]['gm'], self.game.tie_score)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_play_game_multiple_turns(self, mock_stdout):
        self.game._check_game_over_and_show_result = MagicMock(side_effect=[False, True])
        self.game._execute_turn = MagicMock()

        def is_winner_side_effect(player_num):
            # On the second call (which is the end of the game), player 'O' (2) wins.
            return self.game.current_player == 'O'

        self.game.board.is_winner = MagicMock(side_effect=is_winner_side_effect)

        winner = self.game.play_game()
        self.assertEqual(winner, 'O')
        self.assertEqual(len(self.game.game_history), 2)

        self.assertEqual(self.game.game_history[1]['gm'], self.game.loose_score)
        self.assertAlmostEqual(self.game.game_history[0]['gm'], self.game.loose_score * self.game.gamma)

    @patch('xo_lib.game.keras_load_model')
    def test_load_model_success(self, mock_keras_load_model):
        mock_keras_load_model.return_value = MagicMock()
        game = Game(1, 1, 0.9, 1, 0.5, 0.1, {})
        self.assertIsNotNone(game.model)
        mock_keras_load_model.assert_called_once()

    @patch('xo_lib.game.keras_load_model', side_effect=Exception("Test error"))
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_load_model_failure(self, mock_stdout, mock_keras_load_model):
        game = Game(1, 1, 0.9, 1, 0.5, 0.1, {})
        self.assertIsNone(game.model)
        self.assertIn("Error loading model", mock_stdout.getvalue())

    @patch.object(Game, 'network_decision', return_value=(1, 1))
    def test_play_network_agent_turn(self, mock_network_decision):
        self.game.play_network_agent_turn('X')
        mock_network_decision.assert_called_once()
        self.assertEqual(self.game.board.game_board[1, 1], 1)

    @patch.object(Game, 'network_decision')
    def test_play_network_agent_turn_no_empty_places(self, mock_network_decision):
        self.game.board.game_board.fill(1)
        self.game.play_network_agent_turn('X')
        mock_network_decision.assert_not_called()

    def test_network_decision_player_x(self):
        self.game.model = MagicMock()
        self.game.model.predict.side_effect = [[[-0.5]], [[0.8]], [[0.2]]]

        empty_places = [(0, 0), (1, 1), (2, 2)]
        move = self.game.network_decision('X', empty_places)

        self.assertEqual(move, (1, 1))

    def test_network_decision_player_o(self):
        self.game.model = MagicMock()
        self.game.model.predict.side_effect = [[[-0.5]], [[0.8]], [[-0.9]]]

        empty_places = [(0, 0), (1, 1), (2, 2)]
        move = self.game.network_decision('O', empty_places)

        self.assertEqual(move, (2, 2))

    @patch('random.random', return_value=0.1) # Less than RANDOM_SMART_RATIO
    @patch('random.choice', return_value=(1, 2))
    def test_play_smart_agent_turn_random_move(self, mock_random_choice, mock_random_random):
        self.game.play_smart_agent_turn('X', {})
        mock_random_choice.assert_called_once()
        self.assertEqual(self.game.board.game_board[1, 2], 1)

    @patch('random.random', return_value=0.9) # More than RANDOM_SMART_RATIO
    @patch.object(Game, 'smart_decision', return_value=(2, 1))
    def test_play_smart_agent_turn_smart_move(self, mock_smart_decision, mock_random_random):
        self.game.play_smart_agent_turn('X', {})
        mock_smart_decision.assert_called_once()
        self.assertEqual(self.game.board.game_board[2, 1], 1)

    @patch.object(Game, 'smart_decision')
    @patch('random.choice')
    def test_play_smart_agent_turn_no_empty_places(self, mock_random_choice, mock_smart_decision):
        self.game.board.game_board.fill(1)
        self.game.play_smart_agent_turn('X', {})
        mock_smart_decision.assert_not_called()
        mock_random_choice.assert_not_called()

    @patch.object(Game, 'play_smart_agent_turn')
    def test_execute_turn_smart_agent(self, mock_play_smart_agent):
        self.game.current_player = 'X'
        self.game.player1 = Game.SMART_AGENT
        self.game._execute_turn()
        mock_play_smart_agent.assert_called_once_with('X', {})

    @patch.object(Game, 'play_network_agent_turn')
    def test_execute_turn_network_agent(self, mock_play_network_agent):
        self.game.current_player = 'O'
        self.game.player2 = Game.NETWORK_AGENT
        self.game._execute_turn()
        mock_play_network_agent.assert_called_once_with('O')


if __name__ == '__main__':
    unittest.main()
