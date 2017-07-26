from sklearn.preprocessing import normalize
import numpy as np
import game

numActions = 34
numFeats = 5

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

    def weightsNorm(self, norm=2):
        return np.linalg.norm(self.theta, norm)

    def phi(self, a, G):
        action = G.player.actions[a]

        overlaps = G.overlapsAfterAction(action)
        newAvg, newMax = np.mean(overlaps), max(overlaps)
        changeAvgOver = newAvg - G.lastAvgOverlap
        changeMaxOver = newMax - G.lastMaxOverlap

        likelihoods = G.likelihoodsAfterAction(action)
        avgLike = np.mean(likelihoods)
        maxLike = max(likelihoods)

        return [1, changeAvgOver, changeMaxOver, avgLike, maxLike]

    def getAction(self, G):
        # unnormalized = [self.phi(a, G) for a in xrange(numActions)]
        # self.feats = normalize(unnormalized, norm='l1')
        self.feats = [self.phi(a, G) for a in xrange(numActions)]
        self.Q = np.dot(self.feats, self.theta)

        if np.random.rand() < self.eps:
            return np.random.randint(numActions)
        else:
            return np.argmax(self.Q)

    def update(self, G):
        # execute last action
        G.execute(self.lastAction)
        # observe reward r and new state s' in the form of G
        r = G.getReward()

        # print 'FEATURES:\n', np.array(self.feats)
        # print 'Q:\n', self.Q
        # print 'last action: ', self.lastAction
        # print

        # store Q(s,a) and phi(s,a) before Q and feats are overwritten
        Q_sa = self.Q[self.lastAction]
        phi_sa = self.feats[self.lastAction]

        # choose next action a' from s' using epsilon-greedy policy
        newAction = self.getAction(G)

        # perform SGD update on theta
        delta = r + self.gamma * np.dot(self.theta, self.phi(newAction, G)) - Q_sa
        self.theta += np.multiply(self.eta * delta, phi_sa)

        # a <-- a'
        self.lastAction = newAction
        self.lastReward = r
