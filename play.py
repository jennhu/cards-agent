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
def runGame(agent, learner, p, verbose, alpha):
    if agent == 'human' and not verbose:
        print 'WARNING: turn on verbose mode to play as a human.'

    # initialize new game
    G = game.CardGame(p)
    start = time.time()

    if learner:
        learner.lastGoal = learner.getGoal(G)
        learner.lastAction = learner.getAction(learner.lastGoal, G)
    else:
        G.updateWeightsGoals(alpha)

    # main game loop
    while True:
        if G.goalAchieved():
            end = time.time()
            if verbose:
                G.successMessage()
            if agent == 'sarsa':
                return ((1, G.numRounds, G.lastMaxOverlap, end - start)
                        + tuple(learner.theta))
            else:
                return (1, G.numRounds, G.lastMaxOverlap, end - start)
        elif G.deckSize() < 4:
            end = time.time()
            if verbose:
                G.failMessage()
            if agent == 'sarsa':
                return ((0, G.numRounds, G.lastMaxOverlap, end - start)
                        + tuple(learner.theta))
            else:
                return (0, G.numRounds, G.lastMaxOverlap, end - start)
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
Prints a summary of information from hist, a list of tuples.
'''
def summarize(hist):
    successes, rounds, overlaps, times = [np.mean(l) for l in zip(*hist)][:4]
    numGames = len(hist)
    succRate, succNum = successes*100, int(successes*numGames)
    print '* Success rate:\t\t{}% ({}/{})'.format(succRate, succNum, numGames)
    print '* Mean rounds per game:\t{}'.format(rounds)
    print '* Mean final overlap:\t{}'.format(overlaps)
    print '* Mean secs per game:\t{}'.format(times)

'''
Writes data in hist to a specified output file as a csv. Make sure to change
the column labels if you change what values runGame returns.
'''
def write(hist, outfile, agent):
    with open(outfile, 'wb') as out:
        csvOut = csv.writer(out)
        if agent == 'sarsa':
            csvOut.writerow(['success', 'numRounds', 'finalMaxOverlap',
                             'seconds', 'overlap', 'likelihood', 'goodAction'])
        else:
            csvOut.writerow(['success', 'numRounds', 'finalMaxOverlap',
                             'seconds', 'alphaOverlap', 'alphaLike', 'alphaAction'])
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
                        help='type of agent', choices=['human','base','sarsa'])
    parser.add_argument('-p', type=float, default=0.75,
                        help='probability of reshuffling a card')
    parser.add_argument('-N', type=int, default=1,
                        help='number of games to run')
    parser.add_argument('-o', '--out', default=None,
                        help='file path to write history csv')
    parser.add_argument('-alpha', nargs=3, type=float, default=[1,1,1])
    args = parser.parse_args()

    # initialize learner and hist
    learner = sarsa.Learner() if args.agent == 'sarsa' else None
    hist = [None] * args.N

    # # run game for specified amount of time
    # for i in xrange(args.N):
    #     print 'Playing game {}...'.format(i)
    #     res = runGame(args.agent, learner, args.p, args.verbose, args.alpha)
    #     hist[i] = res
    # print 'Done.'
    #
    # # write hist to csv and print summary of results
    # if args.out:
    #     write(hist, args.out, args.agent)
    # summarize(hist)

    incs = np.arange(0, 1.1, 0.1)
    alphas = [[x,y,z] for x in incs for y in incs for z in incs]
    numAlphas = len(alphas)

    for (a,alpha) in enumerate(alphas):
        print 'alpha {}/{}'.format(a, numAlphas)
        # run game for specified amount of time
        for i in xrange(args.N):
            print 'Playing game {}...'.format(i)
            res = runGame(args.agent, learner, args.p, args.verbose, alpha) + tuple(alpha)
            hist[i] = res
        print 'Done.\n'

        # write hist to csv and print summary of results
        write(hist, 'runs/sarsa-goal/alpha2/goal6_alpha{}.csv'.format(a), args.agent)
