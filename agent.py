import numpy as np
import random

class Goal:
    def __init__(self, start, suit):
        self.start = start
        self.suit = suit
        self.cards = self.toCards()
    def toCards(self):
        return set([Card(v,self.suit) for v in xrange(self.start,self.start+6)])
    def overlap(self, C):
        return len(C & self.cards)
    def likelihood(self, H):
        return sum([1 - g.probDiscarded(H) for g in self.cards])
    def __repr__(self):
        return 'Goal(%d,%d)' % (self.start, self.suit)

class Card:
    def __init__(self, val, suit):
        self.val = val % 13
        self.suit = suit
    def probDiscarded(self, H):
        if self in H.hands or self in H.table or self not in H.seenDict.keys():
            return 0
        else:
            s = H.lastRoundSeen(self)
            r_s = H.R[s]
            prod = 1
            for i in xrange(s, H.curRound):
                prod = prod * (1 - 4/(H.deckSize(i)))
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
    def __init__(self):
        self.seenDict = {}
        self.hands = []
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
        s1 = ' * Round: %d' % self.curRound
        s2 = ' * Hands: ' + self.hands.__repr__()
        s3 = ' * Table: ' + self.table.__repr__()
        s4 = ' * Seen: ' + self.seenDict.__repr__()
        s5 = ' * R: ' + self.R.__repr__()
        s6 = ' * Deck size: %d' % self.D
        return 'HISTORY\n%s\n%s\n%s\n%s\n%s\n%s' % (s1,s2,s3,s4,s5,s6)
