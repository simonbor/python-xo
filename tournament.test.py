import unittest
from unittest.mock import patch, mock_open
import numpy as np
import json

# Replace `tic_tac_toe` with the actual filename (without .py)
from xo import (
    Tournament,
    Game,
    Board,
    BOARD_SIZE,
    WIN_SCORE,
    TIE_SCORE,
    LOOSE_SCORE
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

    def test_update_scoreboards_existing_board(self):
        key = "100000000"

        self.tournament.scoreboards = {
            key: [0.5, 2]
        }

        game_history = [{ "bd": [[1, 0, 0], [0, 0, 0], [0, 0, 0]], "gm": 1 }]

        self.tournament.update_scoreboards(game_history)

        updated_score, updated_count = self.tournament.scoreboards[key]

        self.assertEqual(updated_count, 3)

        expected_average = ((0.5 * 3) + 1) / 3
        self.assertAlmostEqual(updated_score, expected_average)

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_scoreboards(self, mock_json_dump, mock_file):
        self.tournament.scoreboards = {
            "123": [1, 2]
        }

        self.tournament.save_scoreboards()

        mock_file.assert_called_once_with("data.json", "w")
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