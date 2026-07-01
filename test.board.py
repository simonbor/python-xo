import unittest
import numpy as np
from unittest.mock import patch
import io

# Make sure to import your Board class here if it's in a different file
from xo import Board

class TestBoard(unittest.TestCase):
    def setUp(self):
        # This method runs before every single test, giving us a fresh board
        self.board = Board()

    def test_init(self):
        # 1. Test that the board initializes as a 3x3 array of zeros
        self.assertEqual(self.board.game_board.shape, (3, 3))
        self.assertTrue(np.all(self.board.game_board == 0))

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_print_board(self, mock_stdout):
        # 2. Test that print_board formats and prints correctly
        self.board.game_board[0, 0] = 1  # X
        self.board.game_board[1, 1] = 2  # O
        self.board.print_board()
        
        output = mock_stdout.getvalue()
        self.assertIn("X| | ", output)
        self.assertIn(" |O| ", output)
        self.assertIn("-----", output)

    def test_is_move_valid(self):
        # 3. Test various valid and invalid moves
        self.assertTrue(self.board.is_move_valid([0, 0])) # Valid empty space
        self.assertTrue(self.board.is_move_valid([2, 2])) # Valid empty space
        
        self.assertFalse(self.board.is_move_valid([3, 0])) # Row out of bounds
        self.assertFalse(self.board.is_move_valid([0, 3])) # Col out of bounds
        self.assertFalse(self.board.is_move_valid([0]))    # Invalid move format (len != 2)
        
        # Test occupied space
        self.board.game_board[0, 0] = 1
        self.assertFalse(self.board.is_move_valid([0, 0]))

    def test_perform_move(self):
        # 4. Test performing valid and invalid moves
        # Valid move
        self.assertTrue(self.board.perform_move([0, 0], 1))
        self.assertEqual(self.board.game_board[0, 0], 1)
        
        # Invalid move (spot already taken)
        self.assertFalse(self.board.perform_move([0, 0], 2))
        self.assertEqual(self.board.game_board[0, 0], 1) # Should remain 1

    def test_is_winner(self):
        # 5. Test win conditions (rows, columns, diagonals)
        self.assertFalse(self.board.is_winner(1)) # Empty board

        # Test Row win
        self.board.game_board[0, :] = 1
        self.assertTrue(self.board.is_winner(1))
        self.board.game_board = np.zeros((3, 3), dtype=int) # Reset

        # Test Column win
        self.board.game_board[:, 1] = 2
        self.assertTrue(self.board.is_winner(2))
        self.board.game_board = np.zeros((3, 3), dtype=int) # Reset

        # Test Main Diagonal win
        np.fill_diagonal(self.board.game_board, 1)
        self.assertTrue(self.board.is_winner(1))
        self.board.game_board = np.zeros((3, 3), dtype=int) # Reset

        # Test Secondary Diagonal win
        self.board.game_board[0, 2] = 2
        self.board.game_board[1, 1] = 2
        self.board.game_board[2, 0] = 2
        self.assertTrue(self.board.is_winner(2))

    def test_is_full(self):
        # 6. Test board fullness
        self.assertFalse(self.board.is_full()) # Empty board
        
        self.board.game_board[0, 0] = 1
        self.assertFalse(self.board.is_full()) # Partially full board
        
        self.board.game_board.fill(1)
        self.assertTrue(self.board.is_full())  # Completely full board

    def test_is_tie(self):
        # 7. Test tie conditions
        self.assertFalse(self.board.is_tie()) # Empty board is not a tie
        
        # Setup a full board with a tie
        self.board.game_board = np.array([
            [1, 2, 1],
            [1, 2, 2],
            [2, 1, 1]
        ])
        self.assertTrue(self.board.is_tie())
        
        # Setup a full board but Player 1 actually won (bottom row)
        self.board.game_board = np.array([
            [2, 2, 1],
            [1, 2, 2],
            [1, 1, 1]
        ])
        self.assertFalse(self.board.is_tie())

    def test_get_empty_places(self):
        # 8. Test retrieving empty coordinates
        self.assertEqual(len(self.board.get_empty_places()), 9)
        
        self.board.game_board[0, 0] = 1
        self.board.game_board[2, 2] = 2
        empty_places = self.board.get_empty_places()
        self.assertEqual(len(empty_places), 7)
        self.assertNotIn([0, 0], empty_places)
        self.assertIn([0, 1], empty_places)
        
        self.board.game_board.fill(1)
        self.assertEqual(len(self.board.get_empty_places()), 0)

if __name__ == '__main__':
    unittest.main()