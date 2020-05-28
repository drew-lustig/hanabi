from random import shuffle


class CardDeck(object):
    variations = {
        'classic': (
            ['r', 'b', 'g', 'y', 'w'],
            {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}
        )
    }

    def __init__(self, variation='classic'):
        self._variation = variation
        self.colors, self.numbers = self.variations[variation]
        self.discarded = {color: [] for color in self.colors}
        self.played = {color: 0 for color in self.colors}
        self.deck = self.full_deck(variation=variation)
        shuffle(self.deck)

    @property
    def variation(self):
        return self._variation

    @variation.setter
    def variation(self, value):
        if len(self.deck) < len(self.full_deck()):
            raise AttributeError('Cannot change variation after game has started.')
        else:
            self.colors, self.numbers = self.variations[value]
            self._variation = value
            self.deck = self.full_deck(variation=variation)
            shuffle(self.deck)

    @classmethod
    def full_deck(cls, variation='classic'):
        full_deck = []
        colors, numbers = cls.variations[variation]
        for color in colors:
            for number, quantity in numbers.items():
                full_deck.extend([(color, number)] * quantity)
        return full_deck

    @classmethod
    def single_possibilities(cls, variation='classic'):
        colors, numbers = cls.variations[variation]
        return [set(colors), set(x for x in numbers.keys())]

    @classmethod
    def all_possibilities(cls, hand_size, variation='classic'):
        return [
            cls.single_possibilities(variation) for i in range(hand_size)
        ]

    @classmethod
    def max_score(cls, variation='classic'):
        colors, numbers = cls.variations[variation]
        return len(colors) * len(numbers)


class Player(object):

    def __init__(self, name, hand):
        self.name = name
        self.hand = hand
        self.possibilities = CardDeck.all_possibilities(len(hand))


class Game(CardDeck):

    def __init__(self, players=['Player 1', 'Player 2', 'Player 3'],
                 variation='classic'):
        CardDeck.__init__(self, variation)
        self._tokens = 8
        self._fuses = 0
        self.score = 0
        self.current_max = self.max_score(variation=variation)
        if len(players) < 4:
            self.hand_size = 5
        else:
            self.hand_size = 4
        self.players = []
        for player in players:
            self.players.append(Player(player, self.deck[:self.hand_size]))
            self.deck = self.deck[self.hand_size:]

    @property
    def tokens(self):
        return self._tokens

    @tokens.setter
    def tokens(self, value):
        if value >= 9:
            raise ValueError('Cannot have more than 8 tokens.')
        elif value < 0:
            raise ValueError('Out of tokens')
        else:
            self._tokens = value

    @property
    def fuses(self):
        return self._fuses

    @fuses.setter
    def fuses(self, value):
        if value > 2:
            raise ValueError('Game Over! Bomb went off.')
        elif value < 0:
            raise ValueError('Cannot have negative fuses.')
        else:
            self._fuses = value

    def update_score(self):
        self.score = sum(self.played.values(), 0)

    def update_max(self, color, number):
        quantity = self.numbers[number]
        max_number = max(self.numbers.keys())
        if self.discarded[color].count(number) == quantity:
            deduction = number - max_number - 1
            self.current_max += deduction

    def remove_hint(self, player, index):
        player.possibilities.pop(index)
        player.possibilities.append(self.single_possibilities(variation=self.variation))

    def hint(self, player, hint):
        self.tokens += -1
        if type(hint) == str:
            index = 0
        else:
            index = 1
        indices = [i for i, card in enumerate(player.hand) if card[index] == hint]
        set_hint = set([hint])
        for i in range(len(player.possibilities)):
            if i in indices:
                player.possibilities[i][index] = set_hint
            else:
                player.possibilities[i][index] = player.possibilities[i][index] - set_hint

    def play(self, player, index):
        color, number = player.hand.pop(index)
        if number - self.played[color] == 1:
            self.played[color] += 1
            if number == 5 and self.tokens < 8:
                self.tokens += 1
            self.update_score()
        else:
            self.discarded[color].append(number)
            self.fuses += 1
            self.update_max(color, number)
        player.hand.append(self.deck.pop())
        self.remove_hint(player, index)

    def discard(self, player, index):
        self.tokens += 1
        color, number = player.hand.pop(index)
        self.discarded[color].append(number)
        self.remove_hint(player, index)

    def turn(self, player, choice, value, hint_player=None):
        if choice == 'hint':
            if player == hint_player:
                raise ValueError('Cannot give yourself a hint! :)')
            else:
                self.hint(hint_player, value)
        elif choice == 'play':
            self.play(player, value)
        elif choice == 'discard':
            self.discard(player, value)
        else:
            raise ValueError('Must give a hint, play a card, or discard.')
        return True
