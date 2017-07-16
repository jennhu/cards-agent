from agent import Goal, Card, Deck, History
import numpy as np

def generateGoals():
    return [Goal(start, suit) for start in xrange(13) for suit in xrange(4)]

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
        print H
        print "Deck size after reshuffle: ", len(deck.cards)
        print

test()
