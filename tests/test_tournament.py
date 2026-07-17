import unittest
from unittest.mock import patch, mock_open, MagicMock
import numpy as np
import json

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.modules['tensorflow'] = MagicMock()
sys.modules['tensorflow.keras'] = MagicMock()
sys.modules['tensorflow.keras.models'] = MagicMock()
from xo_lib import Game, Tournament

from config import (
    JSON_FILE_NAME,
    WIN_SCORE,
)

class TestTournament(unittest.TestCase):

    def setUp(self):
        self.tournament = Tournament(
            player1_type=Game.RANDOM_PLAYER,
            player2_type=Game.RANDOM_PLAYER,
            num_games=5,
            gamma=0.9
        )

    @patch("builtins.open", new_callable=mock_open, read_data='{"123":[1,2]}')
    def test_load_scoreboards_existing_file(self, mock_file):
        result = self.tournament.load_scoreboards("data.json")

        self.assertEqual(result, {"123": [1, 2]})
        mock_file.assert_called_once_with("data.json", "r")

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_scoreboards_file_not_found(self, mock_file):
        result = self.tournament.load_scoreboards("missing.json")

        self.assertEqual(result, {})

    def test_update_scoreboards_new_board(self):
        self.tournament.scoreboards = {}

        game_history = [{ "bd": [[1, 0, 0], [0, 0, 0], [0, 0, 0]], "gm": 1 }]

        self.tournament.update_scoreboards(game_history)

        expected_key = "100000000"

        self.assertIn(expected_key, self.tournament.scoreboards)
        self.assertEqual(self.tournament.scoreboards[expected_key], [1, 1])

    def test_update_scoreboards_existing_board_win_score(self):
        key = "100000000"
        gm = WIN_SCORE # TIE_SCORE, LOOSE_SCORE

        self.tournament.scoreboards = {
            key: [0.5, 2]
        }

        game_history = [{ "bd": [[1, 0, 0], [0, 0, 0], [0, 0, 0]], "gm": gm }]

        self.tournament.update_scoreboards(game_history)

        updated_score, updated_count = self.tournament.scoreboards[key]

        self.assertEqual(updated_score, 0.5)
        self.assertEqual(updated_count, 3)

    def test_update_scoreboards_existing_board(self):
        key = "100000000"

        self.tournament.scoreboards = {
            key: [0.5, 2]
        }

        game_history = [{ "bd": [[1, 0, 0], [0, 0, 0], [0, 0, 0]], "gm": 0.2 }]

        self.tournament.update_scoreboards(game_history)

        updated_score, updated_count = self.tournament.scoreboards[key]

        self.assertEqual(updated_count, 3)

        expected_average = ((0.5 * 2) + 0.2) / 3
        self.assertAlmostEqual(updated_score, expected_average)

    def test_update_scoreboards_with_rotation(self):
        # Board state and its 90-degree counter-clockwise rotation
        board_orig_list = [[1, 2, 0], [0, 0, 0], [0, 0, 0]]
        board_rot90_ccw_list = np.rot90(np.array(board_orig_list), k=1).tolist()
        original_key = "120000000"

        # Test adding a new board.
        self.tournament.scoreboards = {}
        game_history = [{"bd": board_orig_list, "gm": 0.8}]
        self.tournament.update_scoreboards(game_history)

        # Assert that the original key was used and only one entry exists.
        self.assertEqual(len(self.tournament.scoreboards), 1)
        self.assertIn(original_key, self.tournament.scoreboards)
        self.assertEqual(self.tournament.scoreboards[original_key], [0.8, 1])

        # Test adding an existing board via a rotated version.
        game_history = [{"bd": board_rot90_ccw_list, "gm": 0.8}]
        self.tournament.update_scoreboards(game_history)
        
        # Assert that the existing entry was updated and no new key was added.
        self.assertEqual(len(self.tournament.scoreboards), 1)
        self.assertIn(original_key, self.tournament.scoreboards)

    @patch("xo_lib.tournament.SAVE_SCOREBOARDS", True)
    @patch("json.dump")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_scoreboards(self, mock_open, mock_json_dump):
        self.tournament.scoreboards = {
            "123": [1, 2]
        }

        self.tournament.save_scoreboards()

        mock_open.assert_called_once_with(JSON_FILE_NAME, "w")
        mock_json_dump.assert_called_once()

    @patch("builtins.print")
    def test_print_results(self, mock_print):
        self.tournament.results = {
            "X": 2,
            "O": 1,
            "Tie": 2
        }

        self.tournament.print_results()

        self.assertTrue(mock_print.called)

if __name__ == "__main__":
    unittest.main()