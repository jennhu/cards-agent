from agent import Goal, Card, Deck, History
import numpy as np
import random

def generateGoals():
    return [Goal(start, suit) for start in xrange(13) for suit in xrange(4)]

def initializeDeck():
    deck = map(lambda i : Card(i % 13, np.floor(i/13)), xrange(52))
    random.shuffle(deck)
    return deck

def draw(deck, n):
    return deck[:n]

def reshuffle

def test():
    # g1 = Goal(0,2)
    # print g1.cards
    # g2 = Goal(11,3)
    # print g2.cards
    # C = set([Card(3,2), Card(5,0), Card(11,1), Card(9,0)])
    # G = Goal(0,2)
    # print G.overlap(C)
    goals = generateGoals()
    deck = initializeDeck()

    w = np.zeros(len(goals))

    H = History()
    H.hands = draw(deck, 6)
    H.table = draw(deck[6:], 4)
    visible = H.hands + H.table
    H.update(visible, 0)

    print H

test()
