from sklearn.preprocessing import normalize
import numpy as np
import game

numActions = 34
numFeats = 4

'''
Class for the SARSA learner. Follows an epsilon-greedy policy and uses
a linear function approximation.
'''
class Learner:
    def __init__(self):
        self.eps = 0.1
        self.eta = 0.9
        self.gamma = 0.75
        self.lastAction = None
        self.lastReward = None
        self.theta = np.random.rand(numFeats)

    def overlapsAfterAction(self, action, G):
        handCopy, tableCopy = G.player.hand[:], G.table[:]
        game.swap(handCopy, tableCopy, action[0], action[1])
        overlaps = [g.overlap(handCopy + G.other.hand) for g in G.goals]
        return filter(lambda x : x > 0, overlaps)

    def likelihoodsAfterAction(self, action, G):
        cardsPickedUp = [G.table[i] for i in action[1]]
        relGoals = [c.overlappingGoals() for c in cardsPickedUp]
        flattened = set([g for glist in relGoals for g in glist])
        return [g.likelihood(G) for g in flattened]

    def phi(self, a, G):
        action = G.player.actions[a]

        overlaps = self.overlapsAfterAction(action, G)
        newAvg, newMax = np.mean(overlaps), max(overlaps)
        changeAvgOver = newAvg - G.lastAvgOverlap
        changeMaxOver = newMax - G.lastMaxOverlap

        likelihoods = self.likelihoodsAfterAction(action, G)
        avgLike = np.mean(likelihoods)
        maxLike = max(likelihoods)

        return [changeAvgOver, changeMaxOver, avgLike, maxLike]

    def getAction(self, G):
        unnormalized = [self.phi(a, G) for a in xrange(numActions)]
        self.feats = normalize(unnormalized, norm='l1')
        self.actionWeights = np.dot(self.feats, self.theta)

        if np.random.rand() < self.eps:
            return np.random.randint(numActions)
        else:
            return np.argmax(self.actionWeights)

    def update(self, G):
        # execute last action
        G.execute(self.lastAction)
        # observe reward r and new state s' in the form of G
        r = G.getReward()

        # store Q(s,a) and phi(s,a) before actionWeights and feats are overwritten
        Q_sa = self.actionWeights[self.lastAction]
        phi_sa = self.feats[self.lastAction]

        # choose next action a' from s' using epsilon-greedy policy
        newAction = self.getAction(G)

        # perform SGD update on theta
        delta = r + self.gamma * np.dot(self.theta, self.phi(newAction, G)) - Q_sa
        self.theta += np.multiply(self.eta * delta, phi_sa)

        # a <-- a'
        self.lastAction = newAction
        self.lastReward = r
