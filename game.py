'''
game.py contains the basic functionality of the game, including functions
for updating weights and getting optimal goals as well as the implementation
of classes representing goals, cards, decks, and players.
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

class Goal:
    def __init__(self, start, suit):
        self.start = start
        self.suit = suit
        self.cards = self.toCards()

    def toCards(self):
        return [Card(v,self.suit) for v in xrange(self.start,self.start+6)]

    def overlap(self, C):
        return len(set(C) & set(self.cards))

    def likelihood(self, G):
        return np.prod([c.probInPlay(G) for c in self.cards])

    def bestImprovement(self, P, T):
        improvements = P.evaluateActions([self], T)
        return improvements.max()

    def goodAction(self, G):
        return self.bestImprovement(G.player, G.table)

    def __repr__(self):
        return 'Goal(%d,%d)' % (self.start, self.suit)

class Card:
    def __init__(self, val, suit):
        self.val = val % 13
        self.suit = suit

    def overlappingGoals(self):
        return [Goal(self.val + i, self.suit) for i in xrange(-5, 1)]

    def probInPlay(self, G):
        visible = G.P1.hand + G.P2.hand + G.table
        if self in visible or self not in G.seenDict.keys():
            return 1
        else:
            s = G.roundLastSeen(self)
            return G.R[s] / 4.0

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
        self.generateCards()
        self.p = p

    def generateCards(self):
        self.cards = [Card(i % 13, np.floor(i/13)) for i in xrange(52)]
        random.shuffle(self.cards)

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

class Player:
    def __init__(self):
        self.hand = []
        self.generateActions()

    def generateActions(self):
        actions = []
        for i in xrange(1, 4):
            combsC = itertools.combinations(xrange(3), i)
            combsT = itertools.combinations(xrange(4), i)
            for (combC, combT) in itertools.product(combsC, combsT):
                actions.append((combC, combT))
        self.actions = actions

    def act(self, G):
        imp = self.evaluateActions(G.optimalGoals, G.table)
        best = imp.max()
        if best >= 0:
            aIndex, gIndex = np.unravel_index(imp.argmax(), imp.shape)
            goodAction = self.actions[aIndex]
            swap(self.hand, G.table, goodAction[0], goodAction[1])
        else:
            suits = [g.suit for g in G.optimalGoals]
            modeSuit = max(set(suits), key=suits.count)
            suitAction = next((a for a in self.actions if self.suitImprovement(a, modeSuit, G.table) >= 0), None)
            if suitAction:
                swap(self.hand, G.table, suitAction[0], suitAction[1])
            else:
                randAction = random.choice(self.actions)
                swap(self.hand, G.table, randAction[0], randAction[1])

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

'''
Class for the card game. Implements game logic (e.g. drawing new cards and
reshuffling) as well as rewards and transitions for the SARSA agent.
'''
class CardGame:
    def __init__(self, p):
        self.generateGoals()
        self.deck = Deck(p)
        self.P1 = Player()
        self.P2 = Player()

        self.P1Turn = True
        self.player = self.P1
        self.other = self.P2
        self.numRounds = 0

        self.P1.hand = self.deck.draw(3)
        self.P2.hand = self.deck.draw(3)
        self.table = self.deck.draw(4)

        self.lastAvgOverlap, self.lastMaxOverlap = self.avgMaxOverlap()
        self.seenDict = {}
        self.R = [0]

    def roundLastSeen(self, card):
        try:
            return self.seenDict[card]
        except KeyError:
            print 'ERROR: ' + card.__repr__() + ' hasn\'t been seen before.'

    def generateGoals(self):
        self.goals = [Goal(start, suit) for start in xrange(13) for suit in xrange(4)]

    def goalAchieved(self):
        return any(g.overlap(self.P1.hand+self.P2.hand) == 6 for g in self.goals)

    def deckSize(self):
        return len(self.deck.cards)

    def reshuffle(self):
        return self.deck.reshuffle(self.table)

    def updateWeightsGoals(self, alpha):
        self.updateWeights(alpha)
        self.updateOptimalGoals()

    def updateWeights(self, alpha):
        C = self.P1.hand + self.P2.hand
        w = np.zeros(len(self.goals))
        for (i,g) in enumerate(self.goals):
            feats = [g.overlap(C), g.likelihood(self), g.goodAction(self)]
            w[i] = np.dot(alpha, feats)
        self.goalWeights = w

    def updateOptimalGoals(self):
        self.optimalGoals = [self.goals[i] for i, x in enumerate(self.goalWeights) if x == max(self.goalWeights)]

    def nextRound(self):
        self.lastAvgOverlap, self.lastMaxOverlap = self.avgMaxOverlap()
        r = self.reshuffle()
        self.R.append(r)
        self.numRounds += 1

        for s in self.table + self.P1.hand + self.P2.hand:
            self.seenDict[s] = self.numRounds

        self.P1Turn = not self.P1Turn
        self.player = self.P1 if self.P1Turn else self.P2
        self.other = self.P2 if self.P1Turn else self.P1
        self.table = self.deck.draw(4)

    def avgMaxOverlap(self):
        overlaps = [g.overlap(self.P1.hand + self.P2.hand) for g in self.goals]
        nonZeroOverlaps = filter(lambda x : x > 0, overlaps)
        return np.mean(nonZeroOverlaps), max(nonZeroOverlaps)

    def getReward(self):
        if self.goalAchieved():
            return 100
        else:
            newAvgOver, _ = self.avgMaxOverlap()
            return newAvgOver - self.lastAvgOverlap

    def execute(self, a):
        action = self.player.actions[a]
        swap(self.player.hand, self.table, action[0], action[1])

    def successMessage(self):
        print '\x1b[6;30;42m' + 'Success!' + '\x1b[0m'
        print ' * Goal achieved in {} rounds.'.format(self.numRounds)

    def failMessage(self):
        print '\x1b[0;30;41m' + 'Failure!' + '\x1b[0m'
        print ' * Ran out of cards in {} rounds.'.format(self.numRounds)

    def playMessage(self, learner):
        print 'Round {}'.format(self.numRounds)
        print ' * Table:\t\t{}'.format(self.table)
        print ' * Player hand:\t\t{}'.format(self.player.hand)
        print ' * Other hand:\t\t{}'.format(self.other.hand)
        if learner:
            print ' * Action:\t\t{}\n'.format(self.player.actions[learner.lastAction])
        else:
            print ' * Optimal goals:\t', self.optimalGoals
