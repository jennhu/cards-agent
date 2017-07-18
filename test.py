import numpy as np
import random
import game

def runGame():
    goals, deck, w, H, P1, P2 = game.initialize()
    optimalGoals = []
    numRounds = 0

    P1.hand = deck.draw(3)
    P2.hand = deck.draw(3)

    while not game.goalAchieved(goals, P1, P2):
        # assign current player and draw new cards
        player = P1 if H.myTurn else P2
        H.table = deck.draw(4)
        if not H.table:
            print '*** FAILURE!'
            print '*** Ran out of cards in %d rounds.' % numRounds
            return False, numRounds

        # player takes action
        print "Player's hand before acting: ", player.hand
        player.act(optimalGoals, H)
        print "Player's hand after acting: ", player.hand

        # reshuffle and update card history, weights, & optimal goals
        r = deck.reshuffle(H.table)
        H.update(P1.hand + P2.hand + H.table, r)
        game.updateWeights(w, H, P1, P2, goals, [1,3,1])
        optimalGoals = game.getOptimalGoals(w, goals)

        # print new history and optimal goals
        print H
        print "Optimal goals: ", optimalGoals
        print

        # prepare for next player's turn
        H.myTurn = not H.myTurn
        numRounds += 1

    print '*** SUCCESS!'
    print '*** ', optimalGoals[0].cards
    print '*** Goal achieved in %d rounds.' % numRounds
    return True, numRounds

if __name__ == '__main__':
    runGame()
