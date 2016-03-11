import random
# make a list of words
words = [
    'apple',
    'banana',
    'orange',
    'coconut',
    'strawberry',
    'lime',
    'grapefruit',
    'lemon',
    'kumquat',
    'bleuberry',
    'melon'
]
while True:
    start = raw_input("Press enter/return to start, or enter Q to quit.")
    if start.lower() == 'q':
        break

    # pick a random word
    secret_word = random.choice(words)
    bad_guesses = []
    good_guesses = []
    while len(bad_guesses) < 7 and len(good_guesses) != len(list(secret_word)):
        # drw spaces
        for letter in secret_word:
            if letter in good_guesses:
                print letter
            else:
                print '_'*len(letter)
        print ""
        print "Strikes:{}/7".format(len(bad_guesses))
        print ""
        # take guess
        guess = raw_input('Guess a letter:').lower()
        if len(guess) != 1:
            print 'You can only guess a single letter!'
            continue
        elif guess in bad_guesses or guess in good_guesses:
            print '''You've already guess that letter'''
        elif not guess.isalpha():
            print 'You can only guess letters'
            continue
        # print out win / lose
        if guess in secret_word:
            good_guesses.append(guess)
            if len(good_guesses) == len(secret_word):
                print 'You win! The word was {}'.format(secret_word)
                break
            else:
                bad_guesses.append(guess)
        else:
            print '''You didn't guess it! My secret word was {}'''.format(secret_word)
