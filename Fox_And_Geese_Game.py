import json
import time
import keyboard
import os
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
        game = Game.load_game_from_file('saved_game.json')
        if game:
            self.replay_or_continue_game(game)
        else:
            print("No saved game found. Starting a new game instead.")
            self.start_game()

    def replay_or_continue_game(self, game):
        print("Saved game loaded.")
        print("1. Replay the game from the beginning")
        print("2. Continue from where you left off")

        choice = input("Select an option: ")
        if choice == "1":
            game.replay_game()
        elif choice == "2":
            game.play_game()
        else:
            print("Invalid choice. Continuing the game.")
            game.play_game()

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
                self.make_move()
                print("Game is ongoing...")

                if self.foxandgeese.current_player == 'F':
                    print("Fox's turn.")
                    fox_position = self.foxandgeese.find_fox_position()
                    user_input = input(f"Enter the end position of the fox: {fox_position}-")
                else:
                    print("Geese's turn.")
                    user_input = input("Enter the move (format: start_x,start_y-end_x,end_y): ")

                if self.exit_game(user_input):
                    return
                if user_input.lower() == 'save':
                    self.save_game()
                    continue
                if user_input.lower() == 'undo':
                    self.undo_move()
                    continue

                user_sanitize = self.foxandgeese.sanitize_valid_input(user_input)
                if user_sanitize == GameStatus.NOT_VALID_INPUT:
                    print("Invalid input. Please provide two pairs of numbers between 0 and 8 in the format: x1,y1-x2,y2.")
                    continue
                break

            if self.foxandgeese.current_player=='F':
                fox_position = self.foxandgeese.find_fox_position()
                start = tuple(map(int, fox_position.split(',')))
                end = tuple(map(int, user_input.split(',')))
                move_status = self.foxandgeese.logic_valid_move(start, end)
            else:
                start_end = user_input.split('-')
                start = tuple(map(int, start_end[0].split(',')))
                end = tuple(map(int, start_end[1].split(',')))
                move_status = self.foxandgeese.logic_valid_move(start, end)


            self.push_to_undo()

            if move_status == GameStatus.NOT_VALID_POSITION:
                print("Invalid move. Try again.")
                continue

            current_move = self.foxandgeese.current_players_move(user_input)

            if current_move == GameStatus.FOX_MOVING:
                if self.foxandgeese.check_win() == GameStatus.FOX_WIN:
                    self.foxandgeese.game_board.print_board()
                    print("The fox has won!")
                    break
            if current_move == GameStatus.GOOSE_MOVING:
                if self.foxandgeese.check_win() == GameStatus.GEESE_WIN:
                    self.foxandgeese.game_board.print_board()
                    print("The geese have won! The fox is surrounded!")
                    break


    def replay_game(self):
            print("Replaying the game...")
            replay_moves = self.foxandgeese.move_history.copy()
            self.foxandgeese.reset_game()

            move_index = 0

            while move_index < len(replay_moves):
                os.system('cls' if os.name == 'nt' else 'clear')
                self.foxandgeese.game_board.print_board()

                move = replay_moves[move_index]
                sx, sy = move[0]
                ex, ey = move[1]

                if self.foxandgeese.current_player == 'F':
                    self.foxandgeese.fox_move(sx, sy, ex, ey)
                else:
                    self.foxandgeese.geese_move(sx, sy, ex, ey)

                move_index += 1

                print(f"Kicked out geese: {self.foxandgeese.geese_kicked}/10")
                print(f"Move {move_index}: {move}")
                print("Press the space bar to see the next move...")

                while True:
                    if keyboard.is_pressed('space'):
                        while keyboard.is_pressed('space'):
                            time.sleep(0.1)
                        break
                    time.sleep(0.1)

            os.system('cls' if os.name == 'nt' else 'clear')
            self.foxandgeese.game_board.print_board()

            print("Replay finished. Returning to the last game state.")
            self.foxandgeese.move_history = replay_moves

            print("Press the space bar to continue playing...")
            while True:
                if keyboard.is_pressed('space'):
                    while keyboard.is_pressed('space'):
                        time.sleep(0.1)
                    break
                time.sleep(0.1)

            self.play_game()

    def make_move(self):
        pass

    def undo_move(self):
        if self.last_state:
            self.__dict__.update(self.last_state)
            self.foxandgeese.game_board.print_board()
            print("Undo successful.")
        else:
            print("Nothing to undo.")

    def push_to_undo(self):
        self.last_state = copy.deepcopy(self.__dict__)


    def save_game(self, filename='saved_game.json'):
        print("Saving the game...")
        game_state = self.foxandgeese.to_dict()
        with open(filename, 'w') as file:
            json.dump(game_state, file, indent=4)
        print("Game saved.")

    @staticmethod
    def load_game_from_file(filename='saved_game.json'):
        print("Loading the game...")
        try:
            with open(filename, 'r') as file:
                game_state = json.load(file)
            game = Game()
            game.foxandgeese = FoxAndGeese.from_dict(game_state)
            print("Game loaded")
            return game
        except FileNotFoundError:
            print("No saved game found.")
            return None
        except Exception as e:
            print(f"An error occurred while loading the game: {e}")
            return None


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





