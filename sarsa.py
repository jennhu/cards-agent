import numpy as np
import game

numActions = 34
numFeats = 4

'''
Class for the SARSA learner. Follows an epsilon-greedy policy.
'''
class Learner:
    def __init__(self):
        self.eps = 0.1
        self.eta = 0.9
        self.gamma = 0.75
        # self.lastState  = None
        self.lastAction = None
        self.lastReward = None
        # self.w = np.random.rand(numStates, numActions)
        # for feature representation
        self.theta = np.random.rand(numFeats)

    def reset(self):
        # self.lastState  = None
        self.lastAction = None
        self.lastReward = None

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
        self.feats = [self.phi(a, G) for a in xrange(numActions)]
        self.actionWeights = np.dot(self.feats, self.theta)

        if np.random.rand() < self.eps:
            return np.random.randint(numActions)
        else:
            return np.argmax(self.actionWeights)
            # return np.argmax(self.w[s,:])
            # prob distribution over actions, pass in state, take argmax

    # def takeAction(self, G):
    #     G.execute(self.lastAction)
    #     return G.getReward(), G.getState()

    def update(self, G):
        # agent takes last action; observes reward r and new state s' in the form of G
        G.execute(self.lastAction)
        r = G.getReward()

        # choose next action a' from s' using eps-greedy policy
        newAction = self.getAction(G)

        # update w with SGD
        Q_sa = self.actionWeights[self.lastAction]
        delta = r + self.gamma * np.dot(self.theta, self.phi(newAction, G)) - Q_sa
        self.theta += np.multiply(self.eta * delta, self.feats[self.lastAction])

        # delta = r + self.gamma * np.dot(self.theta, self.phi(newAction, G)) - np.dot(self.theta, self.phi(self.lastAction, G))
        # for i in xrange(numFeats):
        #     self.theta[i] += self.eta * delta * self.phi(self.lastAction, G)[i]

        # s <-- s'; a <-- a'
        # self.lastState = newState
        self.lastAction = newAction
        self.lastReward = r

    # def update(self, G):
    #     # agent takes last action; observes reward r and new state s'
    #     r, newState = self.takeAction(G)
    #
    #     # choose next action a' from s' using eps-greedy policy
    #     newAction = self.getAction(newState, G)
    #
    #     # update w with SGD
    #     prev = self.w[self.lastState, self.lastAction]
    #     grad = prev - (r + self.gamma * self.w[newState, newAction])
    #     self.w[agent.lastState, self.lastAction] -= self.eta * grad
    #
    #     # s <-- s'; a <-- a'
    #     self.lastState = newState
    #     self.lastAction = newAction
    #     self.lastReward = r
