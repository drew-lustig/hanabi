import unittest
from functools import reduce

import hanabi


class TestDeck(unittest.TestCase):

    def test_fullDeck(self):
        each_color = 10
        each_number = [15, 10, 10, 10, 5]
        deck = hanabi.CardDeck()
        full_deck = deck.full_deck()

        # Check colors
        for i in range(len(deck.colors)):
            color = deck.colors[i]
            matches = len(list(filter(
                lambda x: True if x[0] == color else False, full_deck
            )))
            msg = f'Color: {color}'
            self.assertEqual(each_color, matches, msg)

        # Check numbers
        numbers = list(set(deck.numbers))
        for i in range(len(numbers)):
            matches = len(list(filter(
                lambda x: True if x[1] == numbers[i] else False, full_deck
            )))
            msg = f'Number: {numbers[i]}'
            self.assertEqual(each_number[i], matches, msg)

    def test_variation(self):
        deck = hanabi.CardDeck(variation='classic')
        with self.assertRaises(KeyError):
            deck.variation = 'test_KeyError'

        game = hanabi.Game()
        self.assertEqual(game.variation, 'classic')
        with self.assertRaises(AttributeError):
            game.variation = 'test_AttributeError'


class TestPlayer(unittest.TestCase):

    def test_possibilities(self):
        game = hanabi.Game()
        player = game.players[0]
        possibilities = player.possibilities
        self.assertEqual(
            possibilities,
            [
                [set(game.colors), set([1, 2, 3, 4, 5])],
                [set(game.colors), set([1, 2, 3, 4, 5])],
                [set(game.colors), set([1, 2, 3, 4, 5])],
                [set(game.colors), set([1, 2, 3, 4, 5])],
                [set(game.colors), set([1, 2, 3, 4, 5])]
            ]
        )


class TestGame(unittest.TestCase):

    def test_gameStart(self):
        tokens = 8
        fuses = 0
        hand_size = 5

        game = hanabi.Game()
        self.assertEqual(tokens, game.tokens, msg='tokens')
        self.assertEqual(fuses, game.fuses, msg='fuses')
        for player in game.players:
            self.assertEqual(hand_size, len(player.hand), msg='hand size')
        self.assertEqual(len(game.deck), len(game.full_deck())-15)
        self.assertEqual(game.current_player, game.players[0])

    def test_hint(self):
        game = hanabi.Game()
        hand = [('r', 1), ('w', 4), ('w', 3), ('b', 1), ('y', 1)]

        red_hint = [
            [set(['r']), set(range(1, 6))],
            [set(['b', 'g', 'y', 'w']), set(range(1, 6))],
            [set(['b', 'g', 'y', 'w']), set(range(1, 6))],
            [set(['b', 'g', 'y', 'w']), set(range(1, 6))],
            [set(['b', 'g', 'y', 'w']), set(range(1, 6))]
        ]
        white_hint = [
            [set(['r', 'b', 'g', 'y']), set(range(1, 6))],
            [set(['w']), set(range(1, 6))],
            [set(['w']), set(range(1, 6))],
            [set(['r', 'b', 'g', 'y']), set(range(1, 6))],
            [set(['r', 'b', 'g', 'y']), set(range(1, 6))]
        ]
        one_hint = [
            [set(game.colors), set([1])],
            [set(game.colors), set(range(2, 6))],
            [set(game.colors), set(range(2, 6))],
            [set(game.colors), set([1])],
            [set(game.colors), set([1])]
        ]

        player1 = game.players[0]
        player1.hand = hand
        game.hint(player1, 'r')
        self.assertEqual(red_hint, player1.possibilities)

        player1.possibilities = hanabi.CardDeck.all_possibilities(len(hand))
        game.hint(player1, 'w')
        self.assertEqual(white_hint, player1.possibilities)

        player1.possibilities = hanabi.CardDeck.all_possibilities(len(hand))
        game.hint(player1, 1)
        self.assertEqual(one_hint, player1.possibilities)

        self.assertEqual(game.tokens, 5)
        for i in range(5):
            game.hint(player1, 1)
        with self.assertRaises(ValueError):
            game.hint(player1, 1)

    def test_discard(self):
        game = hanabi.Game()
        player = game.players[0]
        card = player.hand[0]
        with self.assertRaises(ValueError):
            game.discard(player, 0)
        game.hint(player, 'g')
        game.discard(player, 0)
        discarded = game.discarded[card[0]][0]
        self.assertEqual(card[1], discarded)
        self.assertEqual(game.tokens, 8)
        self.assertEqual(player.possibilities[-1],
                         game.single_possibilities(variation=game.variation))
        self.assertEqual(len(player.hand), 5)

    def test_play(self):
        game = hanabi.Game()
        player = game.players[0]
        hand = [('r', 1), ('w', 4), ('w', 4), ('b', 5), ('y', 3)]
        player.hand = hand

        played = {'r': 1, 'g': 0, 'w': 0, 'b': 0, 'y': 0}
        discarded = {'r': [], 'g': [], 'w': [], 'b': [], 'y': []}
        game.play(player, 0)
        self.assertEqual(game.played, played, 'playable')
        self.assertEqual(game.discarded, discarded, 'playable')
        self.assertEqual(game.score, 1, 'playable 1')
        self.assertEqual(game.current_max, 25, 'playable')
        self.assertEqual(game.tokens, 8, 'playable')
        self.assertEqual(game.fuses, 0, 'playable')

        discarded['w'].append(4)
        game.play(player, 0)
        self.assertEqual(game.played, played, 'unplayable 1')
        self.assertEqual(game.discarded, discarded, 'unplayable 1')
        self.assertEqual(game.current_max, 25, 'unplayable 1')
        self.assertEqual(game.tokens, 8, 'unplayable 1')
        self.assertEqual(game.fuses, 1, 'unplayable 1')

        discarded['w'].append(4)
        game.play(player, 0)
        self.assertEqual(game.played, played, 'unplayable 2')
        self.assertEqual(game.discarded, discarded, 'unplayable 2')
        self.assertEqual(game.current_max, 23, 'unplayable 2')
        self.assertEqual(game.tokens, 8, 'unplayable 2')
        self.assertEqual(game.fuses, 2, 'unplayable 2')

        game.played['b'] = 4
        game.tokens = 4
        played = {'r': 1, 'g': 0, 'w': 0, 'b': 5, 'y': 0}
        game.play(player, 0)
        self.assertEqual(game.played, played, 'playable 5')
        self.assertEqual(game.discarded, discarded, 'playable 5')
        self.assertEqual(game.current_max, 23, 'playable 5')
        self.assertEqual(game.tokens, 5, 'playable 5')
        self.assertEqual(game.fuses, 2, 'playable 5')

        discarded['y'].append(3)
        game.play(player, 0)
        self.assertEqual(game.played, played, 'unplayable 3')
        self.assertEqual(game.discarded, discarded, 'unplayable 3')
        self.assertEqual(game.score, 6, 'unplayable 3')
        self.assertEqual(game.current_max, 23, 'unplayable 3')
        self.assertEqual(game.tokens, 5, 'unplayable 3')
        self.assertEqual(game.fuses, 2, 'unplayable 3')

        def test_turn(self):
            game = hanabi.Game()
            player = game.players[0]
            # TODO

