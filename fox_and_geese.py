from enum import Enum
from gameboard import GameBoard

class GameStatus(Enum):
    GOOSE_MOVING = 1
    FOX_MOVING = 2
    KICK_OUT_GEESE = 3
    FOX_WIN= 4
    GEESE_WIN = 5
    VALID_INPUT = 6
    NOT_VALID_INPUT = 7
    VALID_POSITION = 8
    NOT_VALID_POSITION = 9


class FoxAndGeese:
    def __init__(self):
        self.__game_board = GameBoard()
        self.__current_player = 'F'
        self.__geese_kicked = 0
        self.__last_move_end_position = None

    @property
    def game_board(self):
        return self.__game_board

    @property
    def current_player(self):
        return self.__current_player

    @property
    def geese_kicked(self):
        return self.__geese_kicked

    @property
    def last_move_end_position(self):
        return self.__last_move_end_position

    def sanitize_valid_input(self, input):
        if (isinstance(input, str) and input in {'save', 'exit', 'undo'}):
            return GameStatus.VALID_INPUT
        try:
            x, y = map(int, input.split())
            if isinstance(x, int) and isinstance(y, int) and 0 <= x <= 8 and 0 <= y <= 8:
                return GameStatus.VALID_INPUT
            else:
                return GameStatus.NOT_VALID_INPUT
        except ValueError:
            return GameStatus.NOT_VALID_INPUT


    def logic_valid_move(self, start, end):
        sx, sy = start
        ex, ey = end

        invalid_moves = [
            ((6, 3), (5, 2)), ((5, 2), (6, 3)),
            ((6, 5), (5, 6)), ((5, 6), (6, 5)),
            ((2, 3), (3, 2)), ((3, 2), (2, 3)),
            ((2, 5), (3, 6)), ((3, 6), (2, 5)),
        ]

        if (start, end) in invalid_moves:
            return GameStatus.NOT_VALID_POSITION

        if self.__game_board.board[sx][sy] == '-':
            return GameStatus.NOT_VALID_POSITION
        if self.__game_board.board[sx][sy] == 'G' and self.__game_board.board[ex][ey] == 'G':
            return GameStatus.NOT_VALID_POSITION
        if (sx, sy) == (ex, ey):
            return GameStatus.NOT_VALID_POSITION
        if not (0 <= ex < len(self.__game_board.board) and 0 <= ey < len(self.__game_board.board[0])):
            return GameStatus.NOT_VALID_POSITION
        if self.__game_board.board[sx][sy] in {'F', 'G'} and self.__game_board.board[ex][ey] == '-':
            if self.__current_player == "F":
                if self.__game_board.board[sx][sy] != "F":
                    return GameStatus.NOT_VALID_POSITION
                if abs(ex - sx) <= 1 and abs(ey - sy) <= 1:
                    return GameStatus.VALID_POSITION
                if abs(ex - sx) > 1 or abs(ey - sy) > 1:
                    if (abs(ex - sx) == 2 or abs(ey - sy) == 2):
                        mid_x, mid_y = (sx + ex) // 2, (sy + ey) // 2
                        if self.__game_board.board[mid_x][mid_y] == 'G' and self.__game_board.board[ex][ey] == '-':
                            return GameStatus.VALID_POSITION
                        else:
                            return GameStatus.NOT_VALID_POSITION
                else:
                    return GameStatus.NOT_VALID_POSITION
            else:
                if self.__game_board.board[sx][sy] != "G":
                    return GameStatus.NOT_VALID_POSITION
                if abs(ex - sx) <= 1 and abs(ey - sy) <= 1:
                    return GameStatus.VALID_POSITION
                if abs(ex - sx) > 1 or abs(ey - sy) > 1:
                    return GameStatus.NOT_VALID_POSITION

    def move_piece(self, start, end):
        sx, sy = start
        ex, ey = end

        if self.logic_valid_move(start, end) == GameStatus.VALID_POSITION:
            self.__game_board.board[ex][ey] = self.__game_board.board[sx][sy]
            self.__game_board.board[sx][sy] = '-'

            if abs(sx - ex) == 2 or abs(sy - ey) == 2:
                mid_x, mid_y = (sx + ex) // 2, (sy + ey) // 2
                if self.__game_board.board[mid_x][mid_y] == 'G':
                    self.__game_board.board[mid_x][mid_y] = '-'
                    self.__geese_kicked += 1

    def fox_move(self, sx, sy, ex, ey):
        if self.logic_valid_move((sx,sy), (ex, ey)) == GameStatus.VALID_POSITION:
            self.move_piece((sx, sy), (ex, ey))
            self.__last_move_end_position = (ex, ey)
            self.__current_player = 'G'
            self.check_win()
            return GameStatus.FOX_MOVING


    def geese_move(self, sx, sy, ex, ey):
        if self.logic_valid_move((sx, sy), (ex, ey)) == GameStatus.VALID_POSITION:
            self.move_piece((sx, sy), (ex, ey))
            self.__current_player = 'F'
            self.check_win()
            return GameStatus.GOOSE_MOVING



    def current_players_move(self, sx, sy, ex, ey):
        if self.current_player == 'F':
            return self.fox_move(sx, sy, ex, ey)
        else:
            return self.geese_move(sx, sy, ex, ey)

    def check_win(self):
        if self.__geese_kicked >= 10:
            return GameStatus.FOX_WIN

        fox_pos = self.__last_move_end_position
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
        jump_directions = [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-2, 2), (2, -2)]

        potential_moves = []

        for dx, dy in directions:
            x1, y1 = fox_pos[0] + dx, fox_pos[1] + dy
            if 0 <= x1 < 9 and 0 <= y1 < 9 and self.__game_board.board[x1][y1] == '-':
                potential_moves.append((x1, y1))

        for dx, dy in jump_directions:
            mid_x, mid_y = fox_pos[0] + dx // 2, fox_pos[1] + dy // 2
            x2, y2 = fox_pos[0] + dx, fox_pos[1] + dy
            if (0 <= x2 < 9 and 0 <= y2 < 9 and
                    self.__game_board.board[mid_x][mid_y] == 'G' and
                    self.__game_board.board[x2][y2] == '-'):
                potential_moves.append((x2, y2))

        valid_moves = [(x, y) for (x, y) in potential_moves]

        if not valid_moves:
            return GameStatus.GEESE_WIN

        if len(valid_moves) == 1 and self.__last_move_end_position == valid_moves[0]:
            return GameStatus.GEESE_WIN

        return GameStatus.VALID_POSITION








