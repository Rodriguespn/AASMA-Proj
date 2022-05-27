"""Catpure The Flag (Ctf) state machine and game logic."""
import itertools
from math import ceil

import numpy as np

from ctf.pieces import Unit, Flag
from ctf.q_learning.environment import Environment
from ctf.rendering import Renderer

UP = 0
DOWN = 1
RIGHT = 2
LEFT = 3
STAY = 4


class Ctf(Environment):
    """`Ctf` class, handles a game of CTF.
    """

    def __init__(self,
                 board=None,
                 turn=0,
                 score=(0, 0),
                 captures=(0, 0),
                 jail_timer=5,
                 flags=None,
                 units=None,
                 renderer=None
                 ):
        """Initialization of `Ctf` object.
        """
        self.board = board
        self.turn = turn
        self.score = score
        self.captures = captures
        self.jail_timer = jail_timer
        self.flags = flags
        self.units = units
        self.renderer = renderer

    def __eq__(self, other):
        return self.units == other.units

    def __hash__(self):
        prime = 31
        hashcode = 1
        for i in range(2):
            hashcode = prime * hashcode + hash(tuple(self.units[i]))
        return hashcode

    def key(self):
        return (
            tuple([unit.position for unit in self.units[0]]),
            tuple([unit.position for unit in self.units[1]])
        )

    def copy(self):
        return Ctf(
            board=self.board,
            turn=self.turn,
            score=self.score,
            captures=self.captures,
            jail_timer=self.jail_timer,
            flags=(self.flags[0].copy(), self.flags[1].copy()),
            units=(
                [unit.copy() for unit in self.units[0]],
                [unit.copy() for unit in self.units[1]]
            ),
            renderer=self.renderer
        )

    def cost(self, unit, direction):
        new_position = self._new_position(unit, direction)

        if new_position == self.flags[~unit.team].position:
            return 0

        if new_position == unit.position and direction != STAY:
            return 1

        return 0.5

    def _new_position(self, unit, direction):
        y, x = unit.position

        if direction == UP and self.board[y - 1][x] == 0:
            return y - 1, x
        elif direction == DOWN and self.board[y + 1][x] == 0:
            return y + 1, x
        elif direction == LEFT and self.board[y][x - 1] == 0:
            return y, x - 1
        elif direction == RIGHT and self.board[y][x + 1] == 0:
            return y, x + 1

        return y, x

    def apply_actions(self, actions):
        for unit, action in actions:
            if unit.in_jail():
                unit.jail_timer -= 1
            else:
                unit.position = self._new_position(unit, action)

    def _capture(self, unit):
        unit.jail_timer = self.jail_timer
        unit.position = unit.initial_position
        if unit.team == 0:
            self.captures = (self.captures[0], self.captures[1] + 1)
        else:
            self.captures = (self.captures[0] + 1, self.captures[1])

    def update_before(self):
        for unit0, unit1 in itertools.product(self.units[0], self.units[1]):
            if unit0.in_jail() or unit1.in_jail():
                continue

            if unit0.position == unit1.position:
                if unit0.position[0] < self.board.shape[0] / 2:
                    self._capture(unit0)
                else:
                    self._capture(unit1)

        for i in range(2):
            if self.flags[~i].grounded:
                for unit in self.units[i]:
                    if unit.in_jail():
                        continue

                    if unit.position == self.flags[~i].position:
                        unit.has_flag = True
                        self.flags[~i].grounded = False
                        break

    def update_after(self):
        end = False

        if not self.flags[0].grounded:
            self.score = (self.score[0], self.score[1] + 1)
            end = True

        if not self.flags[1].grounded:
            self.score = (self.score[0] + 1, self.score[1])
            end = True

        if end:
            self.reset()

        self.turn += 1

    def get_actors(self):
        return self.units[0] + self.units[1]

    def _new_board(self, board):
        if board is not None:
            self.board = board
        else:
            self.board = np.zeros((16, 9))
            self.board[0] = 1
            self.board[-1] = 1
            self.board[:, 0] = 1
            self.board[:, -1] = 1

    def _new_units(self, number_units, unit_positions):
        height, width = self.board.shape

        if unit_positions is not None:
            self.units = (
                [Unit(str(i), 0, unit_positions[0][i]) for i in range(len(unit_positions[0]))],
                [Unit(str(i), 1, unit_positions[1][i]) for i in range(len(unit_positions[1]))]
            )
        else:
            if number_units == 1:
                self.units = (
                    [Unit(str(i), 0, (height - 2, ceil((width - 1) / 2))) for i in range(number_units)],
                    [Unit(str(i), 1, (1, (width - 1) // 2)) for i in range(number_units)]
                )
            else:
                step = (width - 3) / (number_units - 1)
                self.units = (
                    [Unit(str(i), 0, (height - 2, int(i * step + 1))) for i in range(number_units)],
                    [Unit(str(i), 1, (1, int(i * step + 1))) for i in range(number_units)]
                )

    def _new_flags(self, flag_positions):
        height, width = self.board.shape

        if flag_positions is not None:
            self.flags = (
                Flag(0, flag_positions[0]),
                Flag(1, flag_positions[1])
            )
        else:
            self.flags = (
                Flag(0, (height - 2, ceil((width - 1) / 2))),
                Flag(1, (1, (width - 1) // 2))
            )

    def new_game(self, board=None, number_units=2, unit_positions=None, flag_positions=None):
        self._new_board(board)
        self._new_units(number_units, unit_positions)
        self._new_flags(flag_positions)

    def reset(self):
        for i in range(2):
            for unit in self.units[i]:
                unit.reset()
            self.flags[i].reset()

    def render(self):
        """Method for rendering a frame.

        If this method is called and the `Ctf` instance currently has no
        renderer, the `ctf.rendering.Renderer` is imported and
        intialized which requires OpenGL.

        Once the renderer is initialized and stored on the `Ctf` object
        it will create a window displaying the state of the game. All
        subsequent calls will utilize the intialized renderer stored on
        the `Ctf` object.

        >>> import ctf
        >>> game = ctf.Ctf()
        >>> game.new_game()
        >>> game.render()

        Raises:
            GameNotFoundError: Raised if this method is called prior to
                `new_game`.

        """
        size = (800, 600)
        pad = [60.0, 20.0]

        if self.renderer is None:
            self.renderer = Renderer(
                width=size[0],
                height=size[1],
                x_pad=pad[0],
                y_pad=pad[1],
                box=(size[1] - pad[1] * 2) / self.board.shape[0],
                unit_pad=((size[1] - pad[1] * 2) / self.board.shape[0]) // 5
            )

        self.renderer.init_window()
        self.renderer.draw_scoreboard(
            dims=self.board.shape,
            turn=self.turn,
            score=self.score,
            captures=self.captures
        )
        self.renderer.draw_grid(self.board)
        self.renderer.draw_pieces(self.board, self.units, self.flags)
        self.renderer.show()
