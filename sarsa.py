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
        self.eta = 0.001
        self.gamma = 0.75
        # self.C = 0
        self.lastAction = None
        self.lastReward = None
        self.theta = np.zeros(numFeats)

    def weightsNorm(self, norm=2):
        return np.linalg.norm(self.theta, norm)

    def phi(self, a, G):
        action = G.player.actions[a]

        overlaps = G.overlapsAfterAction(action)
        avgOver, maxOver = np.mean(overlaps), max(overlaps)
        # changeAvgOver = avgOver - G.lastAvgOverlap
        # changeMaxOver = maxOver - G.lastMaxOverlap

        likelihoods = G.likelihoodsAfterAction(action)
        avgLike = np.mean(likelihoods)
        maxLike = max(likelihoods)

        return [1, avgOver, maxOver, avgLike, maxLike]
        # return [1, changeAvgOver, changeMaxOver, avgLike, maxLike]

    def getAction(self, G):
        self.feats = normalize([self.phi(a, G) for a in xrange(numActions)],
                                norm='l2')
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

        # store Q(s,a) and phi(s,a) before Q and feats are overwritten
        Q_sa = self.Q[self.lastAction]
        phi_sa = self.feats[self.lastAction]

        # choose next action a' from s' using epsilon-greedy policy
        newAction = self.getAction(G)

        # perform SGD update on theta now that Q has been updated
        delta = r + self.gamma * self.Q[newAction] - Q_sa

        update = self.eta * delta * phi_sa # - self.C * self.theta
        # negs = [i for i in xrange(numFeats) if update[i] < 0]
        # print 'Negative update in weights {}'.format(negs)

        self.theta += update

        # a <-- a'
        self.lastAction = newAction
        self.lastReward = r
