import os

class GameBoard:
    def __init__(self):
        self.board = self.create_board()

    def create_board(self):
        board = [[' ' for _ in range(9)] for _ in range(9)]

        for i in range(9):
            board[3][i] = '-'
            board[4][i] = '-'
            board[5][i] = '-'

            board[i][3] = '-'
            board[i][4] = '-'
            board[i][5] = '-'

        for i in range(3, 6):
            board[0][i] = 'G'
            board[1][i] = 'G'
            board[2][i] = 'G'

        for i in range(9):
            board[3][i] = 'G'

        board[7][4] = 'F'
        return board

    def print_board(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("   " + " ".join(f"{i}" for i in range(9)))

        for idx, row in enumerate(self.board):
            print(f"{idx}  " + " ".join(row))
        print("\nG: Goose, F: Fox, -: Empty space, ' ' represents invalid positions\n")

