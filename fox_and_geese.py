from enum import Enum
from gameboard import GameBoard
import re

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
    def __init__(self, game_board=None, current_player='F', geese_kicked=0, move_history=None):
        self.__game_board = game_board if game_board is not None else GameBoard()
        self.__current_player = current_player
        self.__geese_kicked = geese_kicked
        self.__move_history = move_history if move_history is not None else []
        self.__last_state = self.find_fox_position()


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
    def last_state(self):
        return self.__last_state

    @property
    def move_history(self):
        return self.__move_history

    @move_history.setter
    def move_history(self, value):
        self.__move_history = value

    def to_dict(self):
        return {
            'game_board': self.__game_board.to_dict(),
            'current_player': self.__current_player,
            'geese_kicked': self.__geese_kicked,
            'move_history': self.__move_history,
        }

    @classmethod
    def from_dict(cls, data):
        game_board = GameBoard.from_dict(data['game_board'])
        return cls(
            game_board=game_board,
            current_player=data['current_player'],
            geese_kicked=data['geese_kicked'],
            move_history=data.get('move_history', [])  # Add this line
        )

    def reset_game(self):
        self.__game_board = GameBoard()  # Reset to initial state
        self.__current_player = 'F'  # Example initial player
        self.__geese_kicked = 0
        self.__move_history = []


    def find_fox_position(self):
        for x in range(len(self.__game_board.board)):
            for y in range(len(self.__game_board.board[x])):
                if self.__game_board.board[x][y] == 'F':
                    return f"{x},{y}"
        return None

    def sanitize_valid_input(self, input):
        if (isinstance(input, str) and input in {'save', 'exit', 'undo'}):
            return GameStatus.VALID_INPUT

        if self.current_player == 'F':
            if not re.match(r'^\d,\d$', input):
                return GameStatus.NOT_VALID_INPUT
            try:
                end = tuple(map(int, input.split(',')))
                if len(end) != 2:
                    return GameStatus.NOT_VALID_INPUT
                if isinstance(end[0], int) and isinstance(end[1], int) and 0 <= end[0] <= 8 and 0 <= end[1] <= 8:
                    return GameStatus.VALID_INPUT
                else:
                    return GameStatus.NOT_VALID_INPUT
            except ValueError:
                return GameStatus.NOT_VALID_INPUT

        else:
            if not re.match(r'^\d+,\d+-\d+,\d+$', input):
                return GameStatus.NOT_VALID_INPUT

            try:
                start_end = input.split('-')
                start = tuple(map(int, start_end[0].split(',')))
                end = tuple(map(int, start_end[1].split(',')))

                if len(start) != 2 or len(end) != 2:
                    return GameStatus.NOT_VALID_INPUT

                if isinstance(start[0], int) and isinstance(start[1], int) and 0 <= start[0] <= 8 and 0 <= start[1] <= 8:
                    return GameStatus.VALID_INPUT
                else:
                    return GameStatus.NOT_VALID_INPUT
            except ValueError:
                return GameStatus.NOT_VALID_INPUT

    def is_out_of_the_board(self, sx, sy, ex, ey):
        invalid_moves = [
            ((6, 3), (5, 2)), ((5, 2), (6, 3)),
            ((6, 5), (5, 6)), ((5, 6), (6, 5)),
            ((2, 3), (3, 2)), ((3, 2), (2, 3)),
            ((2, 5), (3, 6)), ((3, 6), (2, 5)),
        ]

        if ((sx, sy), (ex, ey)) in invalid_moves:
            return GameStatus.NOT_VALID_POSITION

        if not (0 <= ex < len(self.__game_board.board) and 0 <= ey < len(self.__game_board.board[0])):
            return GameStatus.NOT_VALID_POSITION

        return GameStatus.VALID_POSITION

    def is_not_players_position(self, sx, sy):
        if self.__game_board.board[sx][sy] == '-':
            return GameStatus.NOT_VALID_POSITION
        return GameStatus.VALID_POSITION

    def is_position_occupied_by_goose(self, ex, ey):
        if self.__game_board.board[ex][ey] == 'G':
            return GameStatus.NOT_VALID_POSITION
        return GameStatus.VALID_POSITION

    def is_the_same_position(self, sx, sy, ex, ey):
        if (sx, sy) == (ex, ey):
            return GameStatus.NOT_VALID_POSITION
        return GameStatus.VALID_POSITION

    def is_valid_fox_move(self, sx, sy, ex, ey):
        if self.__game_board.board[sx][sy] == "F" and self.__game_board.board[ex][ey] == '-':
            if abs(ex - sx) <= 1 and abs(ey - sy) <= 1:
                return GameStatus.VALID_POSITION
            if abs(ex - sx) == 2 or abs(ey - sy) == 2:
                mid_x, mid_y = (sx + ex) // 2, (sy + ey) // 2
                if self.__game_board.board[mid_x][mid_y] == 'G' and self.__game_board.board[ex][ey] == '-':
                    return GameStatus.VALID_POSITION
        return GameStatus.NOT_VALID_POSITION

    def is_valid_goose_move(self, sx, sy, ex, ey):
        if self.__game_board.board[sx][sy] == "G" and self.__game_board.board[ex][ey] == '-':
            if abs(ex - sx) <= 1 and abs(ey - sy) <= 1:
                return GameStatus.VALID_POSITION
        return GameStatus.NOT_VALID_POSITION

    def logic_valid_move(self, start, end):

        sx, sy = start
        ex, ey = end

        if self.is_out_of_the_board(sx, sy, ex, ey) == GameStatus.NOT_VALID_POSITION:
            return GameStatus.NOT_VALID_POSITION

        if self.is_not_players_position(sx, sy) == GameStatus.NOT_VALID_POSITION:
            return GameStatus.NOT_VALID_POSITION

        if self.is_position_occupied_by_goose(ex, ey) == GameStatus.NOT_VALID_POSITION:
            return GameStatus.NOT_VALID_POSITION

        if self.is_the_same_position(sx, sy, ex, ey) == GameStatus.NOT_VALID_POSITION:
            return GameStatus.NOT_VALID_POSITION

        if self.current_player == 'F':
            if self.is_valid_fox_move(sx, sy, ex, ey) == GameStatus.VALID_POSITION:
                return GameStatus.VALID_POSITION
            else:
                return GameStatus.NOT_VALID_POSITION

        if self.current_player == 'G':
            if self.is_valid_goose_move(sx, sy, ex, ey) == GameStatus.VALID_POSITION:
                return GameStatus.VALID_POSITION
            else:
                return GameStatus.NOT_VALID_POSITION

        return GameStatus.NOT_VALID_POSITION

    def move_piece(self, start, end):
        sx, sy = start
        ex, ey = end

        if self.logic_valid_move(start, end) == GameStatus.VALID_POSITION:
            self.__move_history.append(((sx, sy), (ex, ey)))
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
            self.__last_state = (ex, ey)
            self.__current_player = 'G'
            self.check_win()
            return GameStatus.FOX_MOVING


    def geese_move(self, sx, sy, ex, ey):
        if self.logic_valid_move((sx, sy), (ex, ey)) == GameStatus.VALID_POSITION:
            self.move_piece((sx, sy), (ex, ey))
            self.__current_player = 'F'
            self.check_win()
            return GameStatus.GOOSE_MOVING


    def current_players_move(self, input):

        if self.current_player == 'F':
            fox_position = self.find_fox_position()
            start = tuple(map(int, fox_position.split(',')))
            end = tuple(map(int, input.split(',')))
            sx, sy = start
            ex, ey = end
            move_status = self.fox_move(sx, sy, ex, ey)
        else:
            start_end = input.split('-')
            start = tuple(map(int, start_end[0].split(',')))
            end = tuple(map(int, start_end[1].split(',')))
            sx, sy = start
            ex, ey = end
            move_status = self.geese_move(sx, sy, ex, ey)
        return move_status



    def check_win(self):
        if self.__geese_kicked >= 10:
            return GameStatus.FOX_WIN

        fox_pos = self.__last_state

        if isinstance(fox_pos, str):
            if ',' in fox_pos:
                fox_pos = fox_pos.split(',')
                fox_pos = (int(fox_pos[0]), int(fox_pos[1]))
            else:
                raise ValueError("Invalid format for fox_pos")

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















