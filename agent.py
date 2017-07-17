import numpy as np
import itertools
import random

def swapIndices(A, B, A_indices, B_indices):
    if len(A_indices) != len(B_indices):
        print 'Must enter same number of indices to swap.'
    else:
        for (i, j) in itertools.product(A_indices, B_indices):
            A[i], B[j] = B[j], A[i]

class Goal:
    def __init__(self, start, suit):
        self.start = start
        self.suit = suit
        self.cards = self.toCards()
    def toCards(self):
        return [Card(v,self.suit) for v in xrange(self.start,self.start+6)]
    def overlap(self, C):
        return len(set(C) & set(self.cards))
    def likelihood(self, H):
        return sum([1 - g.probDiscarded(H) for g in self.cards])
    def existsAction(self, C, T):
        origOverlap = self.overlap(C)
        C_temp = C[:]
        T_temp = T[:]
        for i in xrange(1,len(C)+1):
            i_subsets_C = itertools.combinations(xrange(len(C)), i)
            i_subsets_T = itertools.combinations(xrange(len(T)), i)
            for s_C in i_subsets_C:
                for s_T in i_subsets_T:
                    swapIndices(C_temp, T_temp, s_C, s_T)
                    if self.overlap(C_temp) > origOverlap:
                        return True
                    # reset values
                    C_temp = C[:]
                    T_temp = T[:]
        return False
    def goodAction(self, H):
        myAction = H.myTurn and self.existsAction(H.myHand, H.table)
        yourAction = (not H.myTurn) and self.existsAction(H.yourHand, H.table)
        return int(myAction) + int(yourAction)
    def __repr__(self):
        return 'Goal(%d,%d)' % (self.start, self.suit)

class Card:
    def __init__(self, val, suit):
        self.val = val % 13
        self.suit = suit
    def probDiscarded(self, H):
        visible = H.myHand + H.yourHand + H.table
        if self in visible or self not in H.seenDict.keys():
            return 0
        else:
            s = H.lastRoundSeen(self)
            r_s = H.R[s]
            prod = 1
            for i in xrange(s, H.curRound):
                try:
                    prod = prod * (1 - 4/(H.deckSize(i)))
                except ZeroDivisionError:
                    print 'No cards left in deck.'
                    break
            return prod
    def __repr__(self):
        return 'Card(%d,%d)' % (self.val, self.suit)
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    def __ne__(self, other):
        return not self.__eq__(other)
    def __hash__(self):
        return hash(self.val)

class Deck:
    def __init__(self, p):
        cards = map(lambda i : Card(i % 13, np.floor(i/13)), xrange(52))
        random.shuffle(cards)
        self.cards = cards
        self.p = p
    def draw(self, n):
        if len(self.cards) < n:
            print 'No cards left in deck.'
        else:
            drawn = self.cards[:n]
            self.cards = self.cards[n:]
            return drawn
    def reshuffle(self, cards):
        r = 0
        for c in cards:
            if random.random() < self.p:
                self.cards.append(c)
                r += 1
        return r

class History:
    def __init__(self, meFirst):
        self.seenDict = {}
        self.myHand = []
        self.yourHand = []
        self.myTurn = meFirst
        self.table = []
        self.R = []
        self.curRound = 0
        self.D = 52
    def lastRoundSeen(self, card):
        try:
            return self.seenDict[card]
        except KeyError:
            print 'ERROR: ' + card.__repr__() + ' hasn\'t been seen before.'
    def update(self, seen, r):
        self.curRound += 1
        for s in seen:
            self.seenDict[s] = self.curRound
        self.R.append(r)
        self.D = self.deckSize(self.curRound)
    def deckSize(self, i):
        if i == 1:
            return 42
        elif i != 0:
            return self.D + self.R[i-2] - 4
    def __repr__(self):
        s1 = ' * Round = %d, myTurn = %s' % (self.curRound, self.myTurn.__repr__())
        s2 = ' * My Hand: ' + self.myHand.__repr__()
        s3 = ' * Your Hand: ' + self.yourHand.__repr__()
        s4 = ' * Table: ' + self.table.__repr__()
        s5 = ' * Seen: ' + self.seenDict.__repr__()
        s6 = ' * R: ' + self.R.__repr__()
        s7 = ' * Deck size: %d -> %d' % (self.D, self.D+self.R[self.curRound-1])
        return 'HISTORY\n%s\n%s\n%s\n%s\n%s\n%s\n%s' % (s1,s2,s3,s4,s5,s6,s7)
