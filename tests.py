from agent import Goal, Card, Deck, History
import numpy as np

def generateGoals():
    return [Goal(start, suit) for start in xrange(13) for suit in xrange(4)]

def updateWeights(w, H, goals, alpha_0, alpha_1):
    C = H.hands + H.table
    for (i,g) in enumerate(goals):
        w[i] = alpha_0 * g.overlap(C) + alpha_1 * g.likelihood(H)
    return w

def optimalGoals(w, goals):
    return [goals[i] for i, x in enumerate(w) if x == max(w)]

def initialize():
    goals = generateGoals()
    deck = Deck(0.5)
    w = np.zeros(len(goals))
    H = History()
    return goals, deck, w, H

def play():
    goals, deck, w, H = initialize()
    H.hands = deck.draw(6)

    while not any(g.overlap(H.hands) == 6 for g in goals):
        H.table = deck.draw(4)
        r = deck.reshuffle(H.table)

        print "----> HANDS: ", H.hands
        print "----> TABLE: ", H.table

        optimalBefore = optimalGoals(w, goals)
        print "Optimal goals before swap: ", optimalBefore

        # prompt user to enter which cards to swap
        i_list = input('Enter list of indices to swap from hands: ')
        j_list = input('Enter list of indices to swap from table: ')
        print

        if len(i_list) != len(j_list):
            print 'Must swap same number from hands and table.'
        else:
            for i in i_list:
                for j in j_list:
                    H.hands[i], H.table[j] = H.table[j], H.hands[i]

        H.update(H.hands + H.table, r)
        w = updateWeights(w, H, goals, 1, 1)
        optimalAfter = optimalGoals(w, goals)
        print H
        print "Optimal goals after swap: ", optimalAfter
        print

    print 'CONGRATULATIONS! You\'ve found a straight flush!'
    print optimalGoals(w, goals)[0].cards
    
play()
