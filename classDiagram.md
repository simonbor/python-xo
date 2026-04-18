%% Relationships
Tournament *-- Game : Creates and plays >
Game *-- Board : Contains >

%% Class Definitions
class Board {
    +ndarray game_board
    +__init__()
    +print_board()
    +is_move_valid(move: list) bool
    +perform_move(move: list, player: int) bool
    +is_winner(player: int) bool
    +is_full() bool
    +is_tie() bool
    +get_empty_places() list
    +get_str_board() str
}

class Game {
    +int HUMAN_PLAYER$
    +int RANDOM_PLAYER$
    +Board board
    +int player1
    +int player2
    +str current_player
    +__init__(player1_type, player2_type)
    +play_human_turn(sign: str)
    +play_random_turn(sign: str)
    -_execute_turn()
    -_check_game_over_and_show_result() bool
    +play_game() str
}

class Tournament {
    +int player1_type
    +int player2_type
    +int num_games
    +dict results
    +__init__(player1_type, player2_type, num_games)
    +start_a_tournament()
    +print_results()
}