"""Pieces used in Capture The Flag (Ctf) game."""
from ctf.q_learning.actor import Actor


class Piece(object):
    def __init__(self, team, position, initial_position=None):
        """This class initializes the storage of standard attributes,
        shared amongst the other pieces.

        Args:
            team (:obj:`int`): The team this piece belongs to.
            position (:obj:`tuple`): Location of the piece on the board.

        """
        self.team = team
        self.position = position
        self.initial_position = initial_position if initial_position is not None else position

    def __hash__(self):
        prime = 31
        hashcode = 1
        hashcode = prime * hashcode + self.team
        hashcode = prime * hashcode + self.position[0]
        hashcode = prime * hashcode + self.position[1]
        return hashcode

    def __eq__(self, other):
        return self.team == other.team and self.position == other.position

    def is_flag(self):
        raise NotImplementedError

    def is_unit(self):
        raise NotImplementedError

    def reset(self):
        self.position = self.initial_position


class Unit(Piece, Actor):
    def __init__(self, name, team, position, impexp, initial_position=None, has_flag=False, jail_timer=0, q_values=None):
        """Unit piece, representing a controllable character on the board.
        """
        Piece.__init__(self, team, position, initial_position)
        Actor.__init__(self, 5, q_values if q_values is not None else {}, impexp)
        self.name = name
        self.has_flag = has_flag
        self.jail_timer = jail_timer

    def __hash__(self):
        prime = 31
        hashcode = 1
        hashcode = prime * hashcode + Piece.__hash__(self)
        hashcode = prime * hashcode + self.has_flag
        hashcode = prime * hashcode + self.in_jail()
        return hashcode

    def __eq__(self, other):
        return Piece.__eq__(self, other) and self.has_flag == other.has_flag and self.in_jail() == other.in_jail()

    def copy(self):
        return Unit(
            name=self.name,
            team=self.team,
            position=(self.position[0], self.position[1]),
            impexp=self.impexp,
            initial_position=(self.initial_position[0], self.initial_position[1]),
            has_flag=self.has_flag,
            jail_timer=self.jail_timer,
            q_values=self.q_values
        )

    def is_flag(self):
        return False

    def is_unit(self):
        return True

    def in_jail(self):
        return self.jail_timer > 0

    def reset(self):
        super().reset()
        self.has_flag = False
        self.jail_timer = 0


class Flag(Piece):
    def __init__(self, team, position, grounded=True):
        """Flag piece, representing one of the team's flags.

        Args:
            grounded (:obj:`bool`, optional): Whether or not this flag is on
                the ground. `True` meaning this flag is on the ground,
                `False` meaning a unit is currently carrying this flag.
                Defaults to `True`.

        """
        super().__init__(team, position)
        self.grounded = grounded

    def __hash__(self):
        prime = 31
        hashcode = 1
        hashcode = prime * hashcode + super().__hash__()
        hashcode = prime * hashcode + self.grounded
        return hashcode

    def __eq__(self, other):
        return super().__eq__(other) and self.grounded == other.grounded

    def copy(self):
        return Flag(
            team=self.team,
            position=(self.position[0], self.position[1]),
            grounded=self.grounded
        )

    def is_flag(self):
        return True

    def is_unit(self):
        return False

    def reset(self):
        super().reset()
        self.grounded = True
