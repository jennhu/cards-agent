'''
game.py contains the basic functionality of the game, including functions
for updating weights and getting optimal goals as well as the implementation
of classes representing goals, cards, decks, histories, and players.
'''

import numpy as np
import itertools
import random

def swap(A, B, A_indices, B_indices):
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
        feats = [g.overlap(C), g.likelihood(H, P1, P2), g.goodAction(H, P1, P2)]
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
    def toCards(self):
        return [Card(v,self.suit) for v in xrange(self.start,self.start+6)]
    def overlap(self, C):
        return len(set(C) & set(self.cards))
    def likelihood(self, H, P1, P2):
        return np.prod([g.probInPlay(H, P1, P2) for g in self.cards])
        # return np.prod([1-g.probDiscarded(H, P1, P2) for g in self.cards])
        # return sum([np.log(g.probInPlay(H, P1, P2)) for g in self.cards])
        # return sum([np.log(1 - g.probDiscarded(H, P1, P2)) for g in self.cards])
    def bestImprovement(self, P, T):
        improvements = P.evaluateActions([self], T)
        return improvements.max()
    def goodAction(self, H, P1, P2):
        player = P1 if H.P1Turn else P2
        return self.bestImprovement(player, H.table)
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
            return r_s / 4.0
            # prod = np.prod([(H.deckSize(i) + H.R[i] - 4) / float(H.deckSize(i) + H.R[i]) for i in xrange(s+1, H.curRound)])
            # return prod * r_s / 4.0
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
    def act(self, optimalGoals, H):
        imp = self.evaluateActions(optimalGoals, H.table)
        best = imp.max()
        if best >= 0:
            aIndex, gIndex = np.unravel_index(imp.argmax(), imp.shape)
            goodAction = self.actions[aIndex]
            swap(self.hand, H.table, goodAction[0], goodAction[1])
        else:
            suits = [g.suit for g in optimalGoals]
            modeSuit = max(set(suits), key=suits.count)
            suitAction = next((a for a in self.actions if self.suitImprovement(a, modeSuit, H.table) >= 0), None)
            if suitAction:
                swap(self.hand, H.table, suitAction[0], suitAction[1])
            else:
                randAction = random.choice(self.actions)
                swap(self.hand, H.table, randAction[0], randAction[1])
    def suitImprovement(self, a, s, T):
        curSuitOverlap = sum([1 for c in self.hand if c.suit == s])
        handTemp, tableTemp = self.hand[:], T[:]
        swap(handTemp, tableTemp, a[0], a[1])
        newSuitOverlap = sum([1 for c in handTemp if c.suit == s])
        return newSuitOverlap - curSuitOverlap
    def goalImprovement(self, a, g, T):
        curOverlap = g.overlap(self.hand)
        handTemp, tableTemp = self.hand[:], T[:]
        swap(handTemp, tableTemp, a[0], a[1])
        newOverlap = g.overlap(handTemp)
        return newOverlap - curOverlap
    def evaluateActions(self, gList, T):
        improvements = np.zeros((len(self.actions), len(gList)))
        for (i, a) in enumerate(self.actions):
            for (j, g) in enumerate(gList):
                improvements[i][j] = self.goalImprovement(a, g, T)
        return improvements
