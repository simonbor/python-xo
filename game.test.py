import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import io

from xo import Game, Board

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game(
            player1_type=Game.HUMAN_PLAYER,
            player2_type=Game.RANDOM_PLAYER,
            gamma=0.9,
            win_score=1.0,
            tie_score=0.5,
            loose_score=0.1
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
            return player_num == 2
        
        self.game.board.is_winner = MagicMock(side_effect=is_winner_side_effect)

        winner = self.game.play_game()
        self.assertEqual(winner, 'O')
        self.assertEqual(len(self.game.game_history), 2)
        
        self.assertEqual(self.game.game_history[1]['gm'], self.game.loose_score)
        self.assertAlmostEqual(self.game.game_history[0]['gm'], self.game.loose_score * self.game.gamma)

if __name__ == '__main__':
    unittest.main()
