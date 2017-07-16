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
    def __init__(self):
        cards = map(lambda i : Card(i % 13, np.floor(i/13)), xrange(52))
        random.shuffle(cards)
        self.cards = cards

class History:
    def __init__(self):
        self.seenDict = {}
        self.hands = []
        self.table = []
        self.R = []
        self.curRound = 0
        self.D = 52
    # def lastRoundSeen(self, card):
    #     for (i,s) in enumerate(self.seen):
    #         if card in s:
    #             return i
    #     return -1
    def lastRoundSeen(self, card):
        try:
            return self.seenDict[card]
        except KeyError:
            print 'ERROR: ' + card.__repr__() + ' has never been seen before.'
    def update(self, seen, r):
        self.curRound += 1
        for s in seen:
            self.seenDict[s] = self.curRound
        self.R.append(r)
        self.D = self.deckSize(self.curRound)
        # self.updateDeckSize(self.curRound)
    def deckSize(self, i):
        if i == 1:
            return 42
        elif i != 0:
            return self.deckSize + self.R[i-1] - 4
    def __repr__(self):
        s1 = ' * Round: %d' % self.curRound
        s2 = ' * Hands: ' + self.hands.__repr__()
        s3 = ' * Table: ' + self.table.__repr__()
        s4 = ' * Seen: ' + self.seenDict.__repr__()
        s5 = ' * R: ' + self.R.__repr__()
        s6 = ' * Deck size: %d' % self.D
        return 'HISTORY\n%s\n%s\n%s\n%s\n%s\n%s' % (s1,s2,s3,s4,s5,s6)
    # def updateDeckSize(self, i):
    #     if i == 1:
    #         self.deckSize = 42
    #     elif i != 0:
    #         self.deckSize += self.R[i-1] - 4

# def probDiscarded(c,H):
#     if c in H.hands or c in H.table or c not in H.seenDict.keys():
#         return 0
#     else:
#         s = H.lastRoundSeen(c)
#         r_s = H.R[s]
#         prod = 1
#         for i in xrange(s, H.curRound):
#             prod = prod * (1 - 4/(H.deckSize(i)))
#         return prod

# def likelihood(G,H):
#     return sum([1 - probDiscarded(g,H) for g in G.cards])
