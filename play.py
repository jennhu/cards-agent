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
        elif G.deckSize() < 4:
            end = time.time()
            if verbose:
                G.failMessage()
            return (0, G.numRounds, G.lastMaxOverlap, end - start)
        else:
            if verbose:
                G.playMessage(learner)
            if agent == 'sarsa':
                learner.update(G)
            else:
                G.updateWeightsGoals(alpha)
                if agent == 'human':
                    # prompt user to enter which cards to swap
                    handInds = input('List of indices to swap from hand: ')
                    tableInds = input('List of indices to swap from table: ')
                    game.swap(G.player.hand, G.table, handInds, tableInds)
                elif agent == 'base':
                    G.player.act(G)
            G.nextRound()

'''
Prints a summary of information from hist, a list of
(<1 if success else 0>, <number of rounds>) tuples.
'''
def summarize(hist):
    successes, rounds, overlaps, times = [np.mean(l) for l in zip(*hist)]
    succRate, succNum, numGames = successes*100, int(successes*len(hist)), len(hist)
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
        csvOut.writerow(['success', 'numRounds', 'finalMaxOverlap', 'seconds'])
        for row in hist:
            csvOut.writerow(row)

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
    parser = argparse.ArgumentParser(description='Play the card game!')
    parser.add_argument('-v', '--verbose',
                        help='toggle verbosity', action='store_true')
    parser.add_argument('-a', '--agent', choices=['human', 'base', 'sarsa'],
                        help='type of agent')
    parser.add_argument('-p', type=float, default=0.5,
                        help='probability of reshuffling a card')
    parser.add_argument('-N', type=int, default=1,
                        help='number of trials/epochs to run')
    parser.add_argument('-o', '--out', default='hist.csv',
                        help='file path to write history csv')
    args = parser.parse_args()

    # initialize learner and hist
    learner = sarsa.Learner() if args.agent == 'sarsa' else None
    hist = [None] * args.N

    for i in xrange(args.N):
        res = runGame(args.agent, learner, args.p, args.verbose)
        hist[i] = res
        if learner:
            print 'theta #{}: {}'.format(i, learner.theta)
            print 'last reward: {}\n'.format(learner.lastReward)

    # write hist to csv and print summary of results
    write(hist, args.out)
    summarize(hist)
