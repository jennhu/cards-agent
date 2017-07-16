from agent import Goal, Card, Deck, History
import numpy as np

def generateGoals():
    return [Goal(start, suit) for start in xrange(13) for suit in xrange(4)]

def updateWeights(w, H, goals, alpha_0, alpha_1):
    C = H.hands + H.table
    for (i,g) in enumerate(goals):
        w[i] = alpha_0 * g.overlap(C) + alpha_1 * g.likelihood(H)
    return w

def test():
    goals = generateGoals()
    deck = Deck(0.5)
    w = np.zeros(len(goals))
    H = History()

    H.hands = deck.draw(6)

    for i in xrange(5):
        H.table = deck.draw(4)
        r = deck.reshuffle(H.table)
        H.update(H.hands + H.table, r)
        w = updateWeights(w, H, goals, 1, 1)
        optimalGoals = [goals[i] for i, x in enumerate(w) if x == max(w)]
        print H
        print "Optimal goals: ", optimalGoals
        print

test()
