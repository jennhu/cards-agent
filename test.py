import numpy as np
import random
import game

def runGame(p=0.5, verbose=False, alpha=[1,1,1]):
    goals, deck, w, H, P1, P2 = game.initialize(p)
    optimalGoals = []
    P1.hand = deck.draw(3)
    P2.hand = deck.draw(3)

    while not game.goalAchieved(goals, P1, P2):
        if len(deck.cards) < 4:
            if verbose:
                print '\x1b[0;30;41m' + 'Failure!' + '\x1b[0m'
                print ' * Ran out of cards in %d rounds.' % (H.curRound-1)
                numAway = 6 - optimalGoals[0].overlap(P1.hand + P2.hand)
                print ' * %d cards away from goal.' % numAway
                print
            return False, H.curRound

        player = P1 if H.P1Turn else P2
        other = P2 if H.P1Turn else P1
        H.table = deck.draw(4)
        w = game.getWeights(H, P1, P2, goals, alpha)
        optimalGoals = game.getOptimalGoals(w, goals)

        # player takes action
        if verbose:
            print "---> Table: ", H.table
            print "---> Player's hand: ", player.hand
            print "---> Other's hand: ", other.hand
            print "---> Optimal goals: ", optimalGoals
            print

        player.act(goals, optimalGoals, H)

        # reshuffle and update card history
        r = deck.reshuffle(H.table)
        H.update(P1.hand + P2.hand + H.table, r)
        assert H.deckSize(H.curRound) + r == len(deck.cards)

        if verbose:
            print H
            print " * Player 1's hand: ", P1.hand
            print " * Player 2's hand: ", P2.hand
            print

        # prepare for next player's turn
        H.P1Turn = not H.P1Turn

    if verbose:
        print '\x1b[6;30;42m' + 'Success!' + '\x1b[0m'
        print optimalGoals[0].cards
        print ' * Goal achieved in %d rounds.' % (H.curRound-1)
        print
    return True, H.curRound

if __name__ == '__main__':
    numTrials = 100
    alphas = [[1,1,1]] # [1,5,5], [5,1,1]]
    for a in alphas:
        print '---> alpha =', a
        successes = []
        roundsPlayed = []
        for _ in xrange(numTrials):
            success, numRounds = runGame(p=0.75, verbose=False, alpha=a)
            successes.append(success)
            roundsPlayed.append(numRounds)
        gamesWon = sum([1 for s in successes if s])
        meanRoundsPlayed = np.mean(roundsPlayed)
        print 'Games won: %d/%d = %f%% success' % (gamesWon, numTrials, 100*gamesWon/float(numTrials))
        print 'Mean number of rounds played: ', meanRoundsPlayed
