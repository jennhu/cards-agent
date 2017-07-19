import numpy as np
import random
import game

def runGame(verbose=False):
    goals, deck, w, H, P1, P2 = game.initialize()
    optimalGoals = []
    numRounds = 0

    P1.hand = deck.draw(3)
    P2.hand = deck.draw(3)

    while not game.goalAchieved(goals, P1, P2):
        # assign current player and draw new cards
        player = P1 if H.P1Turn else P2
        other = P2 if H.P1Turn else P1
        H.table = deck.draw(4)

        # player takes action
        if verbose:
            print "---> Table: ", H.table
            print "---> Player's hand: ", player.hand
            print "---> Other's hand: ", other.hand
            print
        player.act(optimalGoals, H)

        # reshuffle and update card history, weights, & optimal goals
        r = deck.reshuffle(H.table)
        H.update(P1.hand + P2.hand + H.table, r)

        assert H.deckSize(H.curRound) + r == len(deck.cards)

        if len(deck.cards) < 4:
            if verbose:
                print '\x1b[0;30;41m' + 'Failure!' + '\x1b[0m'
                print ' * Ran out of cards in %d rounds.' % numRounds
                numAway = 6 - optimalGoals[0].overlap(P1.hand + P2.hand)
                print ' * %d cards away from goal.' % numAway
            return False, numRounds

        game.updateWeights(w, H, P1, P2, goals, [1,1,1])
        # if verbose:
        #     print "weights: \n", w
        optimalGoals = game.getOptimalGoals(w, goals)

        # print new history and optimal goals
        if verbose:
            print H
            print " * Player 1's hand: ", P1.hand
            print " * Player 2's hand: ", P2.hand
            print " * Optimal goals: ", optimalGoals
            print

        # prepare for next player's turn
        H.P1Turn = not H.P1Turn
        numRounds += 1

    if verbose:
        print '\x1b[6;30;42m' + 'Success!' + '\x1b[0m'
        print optimalGoals[0].cards
        print ' * Goal achieved in %d rounds.' % numRounds
    return True, numRounds

if __name__ == '__main__':
    numTrials = 1
    successes = []
    roundsPlayed = []
    for _ in xrange(numTrials):
        success, numRounds = runGame(verbose=True)
        successes.append(success)
        roundsPlayed.append(numRounds)
    percentWin = sum([1 for s in successes if s]) / float(numTrials)
    meanRoundsPlayed = np.mean(roundsPlayed)

    print 'Percentage of games won: ', percentWin
    print 'Mean number of rounds played: ', meanRoundsPlayed
