import random
from django.db import models
from utils import base58
from datetime import datetime



class GameState(models.Model):
    """
    By keeping game state on the server, this makes it easier to build other dummy clients (iOS/Android) and helps
    resolve game game state issues if you want to build multi-player functionality. Also, using easy to read columns
    and rows makes it easier to read than using bitmasks.

    |A|B|C|
    -------
    |O|X|X|
    |X|O|O|
    |X|O|X|

    """
    number_of_moves = models.IntegerField()
    a1 = models.CharField(max_length=1, null=True)
    a2 = models.CharField(max_length=1, null=True)
    a3 = models.CharField(max_length=1, null=True)
    b1 = models.CharField(max_length=1, null=True)
    b2 = models.CharField(max_length=1, null=True)
    b3 = models.CharField(max_length=1, null=True)
    c1 = models.CharField(max_length=1, null=True)
    c2 = models.CharField(max_length=1, null=True)
    c3 = models.CharField(max_length=1, null=True)

    def cells(self):
        """
        |  A |  B |  C |
        ---------------
        |{a1}|{b1}|{c1}|
        |{a2}|{b2}|{c2}|
        |{a2}|{b3}|{c3}|
        :return: A list in Matrix like order.
        """
        return [self.a1, self.b1, self.c1, self.a2, self.b2, self.c2, self.a3, self.b3, self.c3]

    def crosses(self):
        return [self.isCross(v) for v in self.cells()]

    def crosses_bitmask(self):
        return int("".join(str(x) for x in self.crosses()), 2)

    def noughts(self):
        return [self.isNought(v) for v in self.cells()]

    def noughts_bitmask(self):
        return int("".join(str(x) for x in self.noughts()), 2)

    def isNought(self, value):
        if value is None:
            return 0
        else:
            return 1 if value.lower() == "o" else 0

    def isCross(self, value):
        if value is None:
            return 0
        else:
            return 1 if value.lower() == "x" else 0

    def reset(self):
        self.a1 = self.a2 = self.a3 = None
        self.b1 = self.b2 = self.b3 = None
        self.c1 = self.c2 = self.c3 = None

    def __str__(self):
        return """
            |A|B|C|
            -------
            |{a1}|{b1}|{c1}|
            |{a2}|{b2}|{c2}|
            |{a2}|{b3}|{c3}|
        """.format(**self.__dict__)


class PlayerType(models.Model):
    """
    Keeps track of Player information.
    """
    # NOUGHT or CROSS
    team = models.CharField(max_length=1)
    is_human = models.BooleanField(default=False)


class TicTacToeGame(models.Model):
    """
    By keeping game state on the server, this makes it easier to build other dummy clients (iOS/Android) and helps resolve
    game game state issues if you want to build multi-player functionality.
    """
    token = models.CharField(max_length=60)
    state = models.OneToOneField(GameState, related_name='state')
    # For now player_1 is always human
    player_1 = models.OneToOneField(PlayerType, related_name='player_1')
    player_2 = models.OneToOneField(PlayerType, related_name='player_2')
    created = models.DateTimeField(default=datetime.utcnow())

    @classmethod
    def create(cls, **kwargs):
        game = cls(**kwargs)
        game.state = GameState()
        game.token = base58.b58encode(str(random.randrange(999, 9999999, 2)))
        return game