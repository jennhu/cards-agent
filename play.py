import argparse
import numpy as np
import random
import time
import sarsa
import game
import csv

'''
Runs a single instance of the card game.
'''
def runGame(agent, learner, p, verbose, alpha=[1,1,1]):
    if agent == 'human' and not verbose:
        print 'WARNING: turn on verbose mode to play as a human.'

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
            return (1, G.numRounds, G.lastMaxOverlap, end - start)
            # return (1, G.numRounds, G.lastMaxOverlap, learner.lastReward,
            #         learner.weightsNorm(), end - start)
        elif G.deckSize() < 4:
            end = time.time()
            if verbose:
                G.failMessage()
            return (0, G.numRounds, G.lastMaxOverlap, end - start)
            # return (0, G.numRounds, G.lastMaxOverlap, learner.lastReward,
            #         learner.weightsNorm(), end - start)
        else:
            if verbose:
                G.playMessage(learner)
            if agent == 'sarsa':
                learner.update(G)
            else:
                G.updateWeightsGoals(alpha)
                if agent == 'human':
                    G.humanAction()
                elif agent == 'base':
                    G.player.act(G)
            G.nextRound()

'''
Prints a summary of information from hist, a list of
(<1 if success else 0>, <number of rounds>) tuples.
'''
def summarize(hist):
    successes, rounds, overlaps, times = [np.mean(l) for l in zip(*hist)]
    numGames = len(hist)
    succRate, succNum = successes*100, int(successes*numGames)
    print '* Success rate:\t\t{}% ({}/{})'.format(succRate, succNum, numGames)
    print '* Mean rounds per game:\t{}'.format(rounds)
    print '* Mean final overlap:\t{}'.format(overlaps)
    print '* Mean secs per game:\t{}'.format(times)

'''
Writes data in hist to a specified output file as a csv.
'''
def write(hist, outfile):
    with open(outfile, 'wb') as out:
        csvOut = csv.writer(out)
        csvOut.writerow(['success', 'numRounds', 'finalMaxOverlap',
                         'seconds'])
        for row in hist:
            csvOut.writerow(row)

'''
Main function. Simulates learning for a specified number of epochs.
There are three types of agents:
 * 'human' allows a human user to manually play the card game by specifying
    the indices of cards they want to swap at each round.
 * 'base' runs the card game with two baseline agents playing each other.
 * 'sarsa' runs the card game with a SARSA agent learning from the environment.

'''
if __name__ == '__main__':
    # parse command-line flags
    parser = argparse.ArgumentParser(description='Play the card game!')
    parser.add_argument('-v', '--verbose',
                        help='toggle verbosity', action='store_true')
    parser.add_argument('-a', '--agent', default='human',
                        help='type of agent', choices=['human', 'base', 'sarsa'])
    parser.add_argument('-p', type=float, default=0.5,
                        help='probability of reshuffling a card')
    parser.add_argument('-N', type=int, default=1,
                        help='number of trials/epochs to run')
    parser.add_argument('-o', '--out', default=None,
                        help='file path to write history csv')
    args = parser.parse_args()

    # initialize learner and hist
    learner = sarsa.Learner() if args.agent == 'sarsa' else None
    hist = [None] * args.N

    # run game for specified amount of time
    for i in xrange(args.N):
        res = runGame(args.agent, learner, args.p, args.verbose)
        hist[i] = res
        # for debugging
        if learner:
            print 'theta #{}:\n{}'.format(i, learner.theta)
            print 'last reward: {}\n'.format(learner.lastReward)

    # write hist to csv and print summary of results
    if args.out:
        write(hist, args.out)
    summarize(hist)
