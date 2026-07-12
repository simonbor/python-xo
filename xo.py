from xo_lib import Tournament, Game
from config import TOTAL_GAMES, DISCOUNT_RATE

if __name__ == "__main__":
    # Example: Run a tournament of N games between two players
    tournament = Tournament(player1_type=Game.SMART_AGENT, player2_type=Game.NETWORK_AGENT, num_games=TOTAL_GAMES, gamma=DISCOUNT_RATE)

    tournament.start_a_tournament()
    tournament.print_results()
