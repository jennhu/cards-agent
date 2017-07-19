import numpy as np
import itertools
import random

def swapIndices(A, B, A_indices, B_indices):
    if len(A_indices) != len(B_indices):
        print 'Must enter same number of indices to swap.'
    else:
        for (i, j) in itertools.product(A_indices, B_indices):
            A[i], B[j] = B[j], A[i]

def generateGoals():
    return [Goal(start, suit) for start in xrange(13) for suit in xrange(4)]

def initialize(p=0.5, meFirst = True):
    goals = generateGoals()
    deck = Deck(p)
    w = np.zeros(len(goals))
    H = History(meFirst)
    P1 = Player()
    P2 = Player()
    return goals, deck, w, H, P1, P2

def updateWeights(w, H, P1, P2, goals, alpha):
    C = P1.hand + P2.hand
    for (i,g) in enumerate(goals):
        feats = [g.overlap(C), g.likelihood(H, P1, P2), g.goodAction(H, P1, P2)]
        w[i] = np.dot(alpha, feats)

def getOptimalGoals(w, goals):
    return [goals[i] for i, x in enumerate(w) if x == max(w)]

def goalAchieved(goals, P1, P2):
    return any(g.overlap(P1.hand + P2.hand) == 6 for g in goals)

class Goal:
    def __init__(self, start, suit):
        self.start = start
        self.suit = suit
        self.cards = self.toCards()
        self.goodActions = []
    def toCards(self):
        return [Card(v,self.suit) for v in xrange(self.start,self.start+6)]
    def overlap(self, C):
        return len(set(C) & set(self.cards))
    def likelihood(self, H, P1, P2):
        prod = 1
        for g in self.cards:
            prod = prod * g.probInPlay(H, P1, P2)
        return prod
        # return sum([np.log(g.probInPlay(H, P1, P2)) for g in self.cards])
        # return sum([np.log(1 - g.probDiscarded(H, P1, P2)) for g in self.cards])
    def getGoodActions(self, C, T):
        goodActions, neutralActions = [], []
        curOverlap = self.overlap(C)
        C_temp, T_temp = C[:], T[:]
        for i in xrange(1,len(C)+1):
            i_subsets_C = itertools.combinations(xrange(len(C)), i)
            i_subsets_T = itertools.combinations(xrange(len(T)), i)
            for s_C in i_subsets_C:
                for s_T in i_subsets_T:
                    swapIndices(C_temp, T_temp, s_C, s_T)
                    if self.overlap(C_temp) > curOverlap:
                        goodActions.append((s_C, s_T))
                    elif self.overlap(C_temp) == curOverlap:
                        neutralActions.append((s_C, s_T))
                    # reset values
                    C_temp = C[:]
                    T_temp = T[:]
        return goodActions, neutralActions
    def existsAction(self, C, T):
        return True if self.getGoodActions(C,T) else False
    def goodAction(self, H, P1, P2):
        P1Action = H.P1Turn and self.existsAction(P1.hand, H.table)
        P2Action = (not H.P1Turn) and self.existsAction(P2.hand, H.table)
        return int(P1Action or P2Action)
    def __repr__(self):
        return 'Goal(%d,%d)' % (self.start, self.suit)

class Card:
    def __init__(self, val, suit):
        self.val = val % 13
        self.suit = suit
    def probInPlay(self, H, P1, P2):
        visible = P1.hand + P2.hand + H.table
        if self in visible or self not in H.seenDict.keys():
            return 1
        else:
            s = H.lastRoundSeen(self)
            r_s = H.R[s]
            prod = 1
            for i in xrange(s+1, H.curRound):
                D = H.deckSize(i) + H.R[i]
                prod = prod * ((D-4)/float(D))
            return prod * r_s / 4.0
    # def probDiscarded(self, H, P1, P2):
    #     visible = P1.hand + P2.hand + H.table
    #     if self in visible or self not in H.seenDict.keys():
    #         return 0
    #     else:
    #         s = H.lastRoundSeen(self)
    #         r_s = H.R[s]
    #         prod = 1
    #         for i in xrange(s+1, H.curRound):
    #             D = deckSize(H.R, i)
    #             prod = prod * ((D - 4) / float(D))
    #         result = (4 - r_s) / float(4 - r_s + r_s * prod)
    #         assert 0 <= result and result <= 1
    #         return result
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
    def __init__(self, P1First):
        self.P1Turn = P1First
        self.curRound = 0
        self.seenDict = {}
        self.table = []
        self.R = [0]
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
    def deckSize(self, i):
        return 46 + sum(self.R[:i]) - 4*i
    def __repr__(self):
        turn = 1 if self.P1Turn else 2
        D = self.deckSize(self.curRound)
        s1 = 'ROUND #%d: Player %d\'s turn' % (self.curRound, turn)
        s2 = ' * Table: ' + self.table.__repr__()
        s3 = ' * R: ' + self.R.__repr__()
        s4 = ' * Deck size: %d -> %d' % (D, D + self.R[self.curRound])
        return '%s\n%s\n%s\n%s' % (s1,s2,s3,s4)

class Player:
    def __init__(self):
        self.hand = []
    def act(self, optimalGoals, H):
        # randomize order of optimalGoals
        random.shuffle(optimalGoals)
        neutralActions = []
        for g in optimalGoals:
            good, neutral = g.getGoodActions(self.hand, H.table)
            neutralActions += neutral
            if good:
                print 'Good action taken.\n'
                action = random.choice(good)
                swapIndices(self.hand, H.table, action[0], action[1])
                return
        if neutralActions:
            print 'Neutral action taken.\n'
            action = random.choice(neutralActions)
            swapIndices(self.hand, H.table, action[0], action[1])
        else:
            print 'Random action taken.\n'
            numToSwap = random.choice(xrange(3)) + 1
            combsHand = itertools.combinations(xrange(len(self.hand)), numToSwap)
            combsTable = itertools.combinations(xrange(len(H.table)), numToSwap)
            handIndices = random.choice(list(combsHand))
            tableIndices = random.choice(list(combsTable))
            swapIndices(self.hand, H.table, handIndices, tableIndices)
