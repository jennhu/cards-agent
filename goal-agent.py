class Goal:
    def __init__(self, start, suit):
        self.start = start
        self.suit = suit
        self.cards = self.toCards()
    def toCards(self):
        return set([Card(v,self.suit) for v in xrange(self.start,self.start+6)])
    def overlap(self, C):
        return len(C & self.cards)
    def __repr__(self):
        return 'Goal(%d,%d)' % (self.start, self.suit)

class Card:
    def __init__(self, val, suit):
        self.val = val % 13
        self.suit = suit
    def __repr__(self):
        return 'Card(%d,%d)' % (self.val, self.suit)
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    def __ne__(self, other):
        return not self.__eq__(other)
    def __hash__(self):
        return hash(self.val)

class History:
    def __init__(self):
        self.seen = []
        self.R = []
        self.curRound = 0
        self.deckSize = 52
    def lastRoundSeen(self, card):
        for (i,s) in enumerate(self.seen):
            if card in s:
                return i
        return -1
    def update(self, seen, r):
        self.curRound += 1
        self.seen.append(seen)
        self.R.append(r)
        self.updateDeckSize(self.curRound)
    def updateDeckSize(self, i):
        if i == 1:
            self.deckSize = 42
        elif i != 0:
            self.deckSize += self.R[i-1] - 4

g1 = Goal(0,2)
print g1.cards
g2 = Goal(11,3)
print g2.cards
C = set([Card(3,2), Card(5,0), Card(11,1), Card(9,0)])
G = Goal(0,2)
print G.overlap(C)

def likelihood(G,H):
    pass
