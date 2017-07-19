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

def initialize(p, P1First = True):
    goals = generateGoals()
    deck = Deck(p)
    w = np.zeros(len(goals))
    H = History(P1First)
    P1 = Player()
    P2 = Player()
    return goals, deck, w, H, P1, P2

def getWeights(H, P1, P2, goals, alpha):
    C = P1.hand + P2.hand
    w = []
    for g in goals:
        feats = [g.overlap(C), g.likelihood(H, P1, P2), g.goodAction(H, P1, P2, goals)]
        w.append(np.dot(alpha, feats))
    return w

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
        return np.prod([g.probInPlay(H, P1, P2) for g in self.cards])
        # return np.prod([1-g.probDiscarded(H, P1, P2) for g in self.cards])
        # return sum([np.log(g.probInPlay(H, P1, P2)) for g in self.cards])
        # return sum([np.log(1 - g.probDiscarded(H, P1, P2)) for g in self.cards])
    def actionType(self, a, P, T, goals):
        curOverlap = self.overlap(P.hand)
        handTemp, Ttemp = P.hand[:], T[:]
        swapIndices(handTemp, Ttemp, a[0], a[1])
        newOverlap = self.overlap(handTemp)
        if newOverlap > curOverlap:
            return 1
        elif newOverlap == curOverlap:
            return 0
        elif any(g.overlap(handTemp) >= curOverlap and g.suit == self.suit for g in goals):
            return -1
    def existsAction(self, P, T, goals):
        return any(self.actionType(a, P, T, goals) == 1 for a in P.actions)
    def goodAction(self, H, P1, P2, goals):
        P1Action = H.P1Turn and self.existsAction(P1, H.table, goals)
        P2Action = (not H.P1Turn) and self.existsAction(P2, H.table, goals)
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
    #             D = H.deckSize(i) + H.R[i]
    #             prod = prod * ((D-4)/float(D))
    #         result = (4 - r_s) / float(4 - r_s + r_s * prod)
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
        random.shuffle(self.cards)
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
        self.actions = self.possibleActions()
    def possibleActions(self):
        actions = []
        for i in xrange(1, 4):
            combsC = itertools.combinations(xrange(3), i)
            combsT = itertools.combinations(xrange(4), i)
            for (combC, combT) in itertools.product(combsC, combsT):
                actions.append((combC, combT))
        return actions
    def act(self, goals, optimalGoals, H):
        random.shuffle(optimalGoals)
        random.shuffle(self.actions)
        otherGoals = [g for g in goals if g not in optimalGoals]
        neutral, sameSuit = [], []
        for a in self.actions:
            if any(g.actionType(a, self, H.table, goals) == 1 for g in optimalGoals):
                swapIndices(self.hand, H.table, a[0], a[1])
                return
            elif any(g.actionType(a, self, H.table, goals) == 0 for g in optimalGoals):
                neutral.append(a)
            elif any(g.actionType(a, self, H.table, otherGoals) == -1 for g in optimalGoals):
                sameSuit.append(a)
        if neutral:
            a = random.choice(neutral)
        elif sameSuit:
            a = random.choice(sameSuit)
        else:
            a = random.choice(self.actions)
        # print 'Action: ', a
        swapIndices(self.hand, H.table, a[0], a[1])
