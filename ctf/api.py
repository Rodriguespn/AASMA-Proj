"""Catpure The Flag (Ctf) state machine and game logic."""
import itertools

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

    def _rotate_position(self, position):
        height, width = self.board.shape
        return height - position[0] - 1, width - position[1] - 1

    def observation(self, unit):
        """result is orientation independent"""
        allies = self.units[unit.team][:]
        allies.remove(unit)
        if unit.team == 0:
            return (
                unit.position,
                tuple([unit.position for unit in sorted(allies)]),
                tuple([unit.position for unit in sorted(self.units[1])])
            )
        else:
            return (
                self._rotate_position(unit.position),
                tuple([self._rotate_position(unit.position) for unit in sorted(allies)]),
                tuple([self._rotate_position(unit.position) for unit in sorted(self.units[0])])
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

    @staticmethod
    def manhattan_distance(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def cost(self, unit, direction):
        cost = 0.5

        new_position = self._new_position(unit, direction)

        if new_position == self.flags[~unit.team].position:
            cost -= 0.5

        for enemy in self.units[~unit.team]:
            if self.manhattan_distance(enemy.position, self.flags[unit.team].position) == 1:
                cost += 0.5
                break

        return cost

    def _new_position(self, unit, direction, inverted=False):
        """result is semi orientation independent"""
        y, x = unit.position

        if not inverted:
            if direction == UP and self.board[y - 1][x] == 0:
                return y - 1, x
            elif direction == DOWN and self.board[y + 1][x] == 0:
                return y + 1, x
            elif direction == LEFT and self.board[y][x - 1] == 0:
                return y, x - 1
            elif direction == RIGHT and self.board[y][x + 1] == 0:
                return y, x + 1
        else:
            if direction == DOWN and self.board[y - 1][x] == 0:
                return y - 1, x
            elif direction == UP and self.board[y + 1][x] == 0:
                return y + 1, x
            elif direction == RIGHT and self.board[y][x - 1] == 0:
                return y, x - 1
            elif direction == LEFT and self.board[y][x + 1] == 0:
                return y, x + 1

        return y, x

    def apply_actions(self, actions):
        """result is orientation independent"""
        for unit, action in actions:
            if unit.in_jail():
                unit.jail_timer -= 1
            else:
                unit.position = self._new_position(unit, action, inverted=unit.team == 1)

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

    def new_game(self, board, units, flags):
        self.board = board
        self.units = units
        self.flags = flags

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
