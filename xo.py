from xo_lib.tournament import Tournament
from xo_lib.game import Game
from xo_lib.config import TOTAL_GAMES, DISCOUNT_RATE

if __name__ == "__main__":
    # Example: Run a tournament of N games between two players
    tournament = Tournament(player1_type=Game.RANDOM_PLAYER, player2_type=Game.SMART_AGENT, num_games=TOTAL_GAMES, gamma=DISCOUNT_RATE)
    
    tournament.start_a_tournament()
    tournament.print_results()
