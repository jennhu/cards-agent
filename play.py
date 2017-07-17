from agent import Goal, Card, Deck, History, swapIndices
import numpy as np

def generateGoals():
    return [Goal(start, suit) for start in xrange(13) for suit in xrange(4)]

def initialize():
    goals = generateGoals()
    deck = Deck(0.5)
    w = np.zeros(len(goals))
    H = History(True)
    return goals, deck, w, H

def updateWeights(w, H, goals, alpha):
    C = H.myHand + H.yourHand
    for (i,g) in enumerate(goals):
        feats = [g.overlap(C), g.likelihood(H), g.goodAction(H)]
        w[i] = np.dot(alpha, feats)

def getOptimalGoals(w, goals):
    return [goals[i] for i, x in enumerate(w) if x == max(w)]

if __name__ == '__main__':
    goals, deck, w, H = initialize()
    H.myHand = deck.draw(3)
    H.yourHand = deck.draw(3)

    while not any(g.overlap(H.myHand + H.yourHand) == 6 for g in goals):
        # draw new cards
        H.table = deck.draw(4)
        r = deck.reshuffle(H.table)

        # update text and hand based on turn
        turnText = 'MY' if H.myTurn else 'YOUR'
        hand = H.myHand if H.myTurn else H.yourHand

        # print updated cards
        print "----> It's %s turn." % turnText
        print "----> My hand: ", H.myHand
        print "----> Your hand: ", H.yourHand
        print "----> Table: ", H.table

        # prompt user to enter which cards to swap
        hand_inds = input('Enter list of indices to swap from %s hand: ' % turnText)
        table_inds = input('Enter list of indices to swap from table: ')
        swapIndices(hand, H.table, hand_inds, table_inds)

        # update card history, weights, and optimal goals
        H.update(H.myHand + H.yourHand + H.table, r)
        updateWeights(w, H, goals, [1,2,1])
        optimalGoals = getOptimalGoals(w, goals)

        # print new history and optimal goals
        print
        print H
        print "Optimal goals: ", optimalGoals
        print

        # next player's turn
        H.myTurn = not H.myTurn

    print 'CONGRATULATIONS! You\'ve found a straight flush!'
    print optimalGoals(w, goals)[0].cards
