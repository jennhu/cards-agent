import argparse
import numpy as np
import random
import time
import sarsa
import game

'''
Runs a single instance of the card game.
'''
def runGame(agent, learner, p=0.5, alpha=[1,1,1], verbose=False):
    if agent == 'sarsa':
        assert learner
    elif agent == 'human':
        assert verbose

    # initialize new game
    G = game.CardGame(p)
    start = time.time()

    if learner:
        learner.lastAction = learner.getAction(G)
    else:
        G.updateWeightsGoals(alpha)

    # main game loop
    while True:
        if G.goalAchieved():
            end = time.time()
            if verbose:
                G.successMessage()
            if learner:
                learner.reset()
            return (1, G.numRounds, G.lastMaxOverlap, end - start)
        elif G.deckSize() < 4:
            end = time.time()
            if verbose:
                G.failMessage()
            if learner:
                learner.reset()
            return (0, G.numRounds, G.lastMaxOverlap, end - start)
        else:
            if verbose:
                G.playMessage(learner)
            if learner:
                learner.update(G)
            else:
                G.updateWeightsGoals(alpha)
                if agent == 'human':
                    # prompt user to enter which cards to swap
                    handInds = input('Enter list of indices to swap from player hand: ')
                    tableInds = input('Enter list of indices to swap from table: ')
                    game.swap(G.player.hand, G.table, handInds, tableInds)
                elif agent == 'base':
                    G.player.act(G)
            G.nextRound()

'''
Returns the success rate and mean number of rounds per game from hist,
a list of (<1 if success else 0>, <number of rounds>) tuples.
'''
def getResults(hist):
    return [np.mean(l) for l in zip(*hist)]
    # successes, rounds, endMaxOverlaps, times = zip(*hist)
    # return np.mean(successes), np.mean(rounds), np.mean(endMaxOverlaps), np.mean(times)

'''
Main function. Simulates learning for a specified number of epochs.

Agent types:
 * 'human' allows a human user to manually play the card game by specifying
    the indices of cards they want to swap at each round.
 * 'base' runs the card game with two baseline agents playing each other.
 * 'sarsa' runs the card game with a SARSA agent learning from the environment.

'''
if __name__ == '__main__':
    # parse command-line flags
    parser = argparse.ArgumentParser(description='Plays the card game with different types of agents.')
    parser.add_argument('-v', '--verbose', help='toggle verbosity', action='store_true')
    parser.add_argument('-a', '--agent', choices=['human', 'base', 'sarsa'], help='select type of agent')
    parser.add_argument('-p', type=float, help='probability of reshuffling a card')
    parser.add_argument('-t', type=int, help='number of trials/epochs to run')
    args = parser.parse_args()

    if args.agent == 'sarsa':
        learner = sarsa.Learner()
    else:
        learner = None

    hist = [None] * args.t
    for i in xrange(args.t):
        res = runGame(args.agent, learner, p=args.p, verbose=args.verbose)
        hist[i] = res
        # print 'theta after epoch {}: {}'.format(i, agent.theta)
    successRate, meanNumRounds, meanEndMaxOverlaps, meanSecs = getResults(hist)
    print '\nhist:\n{}\n'.format(np.array(hist))
    print '* Success rate:\t\t{}%'.format(successRate * 100)
    print '* Mean rounds per game:\t{}'.format(meanNumRounds)
    print '* Mean final overlap:\t{}'.format(meanEndMaxOverlaps)
    print '* Mean secs per game:\t{}'.format(meanSecs)
