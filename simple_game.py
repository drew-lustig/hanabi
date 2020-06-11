import hanabi


def main():
    players = []
    while True:
        num = len(players) + 1
        player = input(f'Player {num} name: ')
        if player == '':
            if num <= 2:
                print('Must have at least two players')
                continue
            else:
                break
        players.append(player)
    game = hanabi.Game(players=players)
    turn_val = game.current_player
    while type(turn_val) == hanabi.Player:
        # Reset Values
        hint_player = None
        value_prompt = 'card number: '
        choice = None
        value = None

        print(game)
        while choice is None:
            choice = input('Choose hint, play, or discard: ')
            if choice not in ['hint', 'play', 'discard']:
                print('Please select between hint, play, and discard.')
                choice = None
        if choice == 'hint':
            while hint_player is None:
                val = input('Choose hint target: ')
                for player in game.players:
                    if val == player.name:
                        hint_player = player
                if hint_player is None:
                    print('Player not found. Please re-select a player.')
            value_prompt = 'hint: '
        value = input(f'Choose {value_prompt}')
        try:
            value = int(value)
        except Exception:
            pass
        turn_val = game.turn(turn_val, choice, value, hint_player)
    print('Final Score: ', turn_val)


if __name__ == "__main__":
    main()
