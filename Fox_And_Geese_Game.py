import pickle
import copy
from fox_and_geese import FoxAndGeese, GameStatus


class MainMenu:
    def __init__(self):
        self.fox_and_geese = FoxAndGeese()

    def show_menu(self):
        while True:
            print("Welcome to Fox and Geese")
            print("Main Menu")
            print("1. Play Now!")
            print("2. Load Saved Game")
            print("3. Exit game")

            choice = input("Select an option: ")
            match choice:
                case "1":
                    self.start_game()
                case "2":
                    self.load_game()
                case "3":
                    print("Exiting game...")
                    exit()
                case _:
                    print("Invalid choice. Please try again.")

    def start_game(self):
        print("Starting a new game...")
        game = Game()
        game.play_game()

    def load_game(self):
        print("Loading a saved game...")
        try:
           game = Game.load_game_from_file('saved_game.pkl')
           game.play_game()
        except FileNotFoundError:
            print("No saved game found. Starting a new game instead.")
            self.start_game()

class Game:
    def __init__(self):
        self.foxandgeese = FoxAndGeese()
        self.last_state = None

    def play_game(self):

        print("At any time, type 'save' to save your progress, 'exit' to leave the game, or 'undo' to redo your last move.")
        self.push_to_undo()


        while True:
            self.foxandgeese.game_board.print_board()
            kicked_geese = self.foxandgeese.geese_kicked
            print(f"{kicked_geese}/10 Geese")

            while True:
                if self.foxandgeese.current_player == 'F':
                    print("Fox's turn.")
                else:
                    print("Geese's turn.")

                user_start = input("Enter the starting position (format: start_x start_y): ")
                if self.exit_game(user_start):
                    return
                if user_start.lower() == 'save':
                    self.save_game()
                    continue
                if user_start.lower() == 'undo':
                    self.undo_move()
                    continue

                user_start_sanitize = self.foxandgeese.sanitize_valid_input(user_start)
                if user_start_sanitize == GameStatus.NOT_VALID_INPUT:
                    print("This is not valid, you should give two numbers beteween 0 and 8.")
                    continue

                break

            while True:
                user_end = input ("Enter the destination (end_x end_y):")
                if self.exit_game(user_end):
                    return
                if user_end.lower() == 'save':
                    self.save_game()
                    continue
                if user_end.lower() == 'undo':
                    self.undo_move()
                    continue

                user_end_sanitize = self.foxandgeese.sanitize_valid_input(user_end)
                if user_end_sanitize == GameStatus.NOT_VALID_INPUT:
                    print("This is not valid input, you should give two numbers beteween 0 and 8.")
                    continue

                break

            start_x, start_y = map(int, user_start.split())
            end_x, end_y = map(int, user_end.split())
            move_status = self.foxandgeese.logic_valid_move((start_x, start_y), (end_x, end_y))


            self.push_to_undo()

            if move_status == GameStatus.NOT_VALID_POSITION:
                print("Invalid move. Try again.")
                continue

            current_move = self.foxandgeese.current_players_move(start_x, start_y, end_x, end_y)

            if current_move == GameStatus.FOX_MOVING:
                self.foxandgeese.check_win()
                if self.foxandgeese.check_win() == GameStatus.FOX_WIN:
                    self.foxandgeese.game_board.print_board()
                    print("The fox has won!")
                    break
            if current_move == GameStatus.GOOSE_MOVING:
                self.foxandgeese.check_win()
                if self.foxandgeese.check_win() == GameStatus.GEESE_WIN:
                    self.foxandgeese.game_board.print_board()
                    print("The geese have won! The fox is surrounded!")
                    break


    def undo_move(self):
        if self.last_state:
            self.__dict__.update(self.last_state)
            self.foxandgeese.game_board.print_board()
            print("Undo successful.")
        else:
            print("Nothing to undo.")

    def push_to_undo(self):
        self.last_state = copy.deepcopy(self.__dict__)

    def save_game(self, filename = 'saved_game.pkl'):
        print("Saving the game...")
        with open(filename, 'wb') as file:
            pickle.dump(self, file)
        print("Game saved.")


    @staticmethod
    def load_game_from_file(filename='saved_game.pkl'):
        print("Loading the game...")
        with open(filename, 'rb') as file:
            return pickle.load(file)
        print("Game loaded.")


    def exit_game(self, command):
        if command.lower() == "exit":
            print("Exiting Game!")
            return True
        return False

try:
    game_try = MainMenu()
    game_try.show_menu()
except KeyboardInterrupt:
    print("\nGoodbye! Game interrupted!")






