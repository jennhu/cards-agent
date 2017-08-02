from sklearn.preprocessing import normalize
import numpy as np
import random
import game

numGoals = 52
numFeats = 3

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
        self.lastGoal = None
        self.lastAction = None
        self.lastReward = None
        self.theta = np.zeros(numFeats)

    def weightsNorm(self, norm=2):
        return np.linalg.norm(self.theta, norm)

    def phi(self, g, G):
        overlap = g.overlap(G.player.hand + G.other.hand)
        likelihood = g.likelihood(G)
        bestImp = g.bestImprovement(G)
        return [overlap, likelihood, bestImp]

    def getGoal(self, G):
        self.feats = normalize([self.phi(g, G) for g in G.goals], norm='l2')
        self.Q = np.dot(self.feats, self.theta)
        # epsilon greedy policy
        if np.random.rand() < self.eps:
            return np.random.randint(numGoals)
        else:
            return np.argmax(self.Q)

    '''
    Given a goal g, select the best action to take according to the
    baseline rule (first look for a good action, then suit action,
    then random action).
    '''
    def getAction(self, g, G):
        goal = G.goals[g]
        imp = G.player.evaluateActions([goal], G)
        best = imp.max()
        if best >= 0:
            aIndex, gIndex = np.unravel_index(imp.argmax(), imp.shape)
            goodAction = G.player.actions[aIndex]
            return goodAction
        else:
            suitAction = next((a
                for a in G.player.actions
                if G.player.incSuitOverlap(a, goal.suit, G) >= 0), None)
            if suitAction:
                return suitAction
            else:
                randAction = random.choice(G.player.actions)
                return randAction

    def update(self, G):
        # execute last action chosen
        G.execute(self.lastAction)
        # observe reward r and new state s' in the form of G
        r = G.getReward()

        # store Q(s,a) and phi(s,a) before Q and feats are overwritten
        Q_sa = self.Q[self.lastGoal]
        phi_sa = self.feats[self.lastGoal]

        # choose next action a' from s' using epsilon greedy policy
        newGoal = self.getGoal(G)

        # perform SGD update on theta now that Q has been updated
        delta = r + self.gamma * self.Q[newGoal] - Q_sa
        self.theta += self.eta * delta * phi_sa # - self.C * self.theta

        # g <-- g', a <-- a'
        self.lastGoal = newGoal
        self.lastAction = self.getAction(self.lastGoal, G)
        self.lastReward = r
