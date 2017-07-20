'''
run.py runs the card game with two agents playing each other.
It supports options to plot and print metrics such as success rate
and mean number of rounds taken per game.
'''

import matplotlib.pyplot as plt
import numpy as np
import time
import game

def runGame(p=0.5, verbose=False, alpha=[1,1,1]):
    goals, deck, w, H, P1, P2 = game.initialize(p)
    optimalGoals = []
    P1.hand = deck.draw(3)
    P2.hand = deck.draw(3)

    while not game.goalAchieved(goals, P1, P2):
        if len(deck.cards) < 4:
            if verbose:
                print '\x1b[0;30;41m' + 'Failure!' + '\x1b[0m'
                print ' * Ran out of cards in %d rounds.' % (H.curRound-1)
                numAway = 6 - optimalGoals[0].overlap(P1.hand + P2.hand)
                print ' * %d cards away from goal.' % numAway
                print
            return False, H.curRound

        player = P1 if H.P1Turn else P2
        other = P2 if H.P1Turn else P1
        H.table = deck.draw(4)
        w = game.getWeights(H, P1, P2, goals, alpha)
        optimalGoals = game.getOptimalGoals(w, goals)

        # player takes action
        if verbose:
            print "---> Table: ", H.table
            print "---> Player's hand: ", player.hand
            print "---> Other's hand: ", other.hand
            print "---> Optimal goals: ", optimalGoals
            print

        player.act(optimalGoals, H)

        # reshuffle and update card history
        r = deck.reshuffle(H.table)
        H.update(P1.hand + P2.hand + H.table, r)
        assert H.deckSize(H.curRound) + r == len(deck.cards)

        if verbose:
            print H
            print " * Player 1's hand: ", P1.hand
            print " * Player 2's hand: ", P2.hand
            print

        # prepare for next player's turn
        H.P1Turn = not H.P1Turn

    if verbose:
        print '\x1b[6;30;42m' + 'Success!' + '\x1b[0m'
        print optimalGoals[0].cards
        print ' * Goal achieved in %d rounds.' % (H.curRound-1)
        print
    return True, H.curRound

if __name__ == '__main__':
    numTrials = 50

    alphas = [[1,1,1], [1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]]
    ps = [0, 0.25, 0.5, 0.75]

    # create plot
    fig, ax = plt.subplots()
    fig2, ax2 = plt.subplots()

    alphaNames = map(lambda l : str(l), alphas)
    y_pos = np.arange(len(alphaNames))
    n_groups = len(alphas)
    index = np.arange(n_groups)
    bar_width = 1/float(5)
    opacity = 0.6
    colors = ['b', 'r', 'g', 'y', 'm']

    # successRates = []
    # meanRounds = []
    successResults = np.zeros((len(ps), len(alphas)))
    meanRoundResults = np.zeros((len(ps), len(alphas)))
    for (i,p) in enumerate(ps):
        print 'p = %f...' % p
        for (j,a) in enumerate(alphas):
            print 'alpha =', a
            gameResults = []
            roundsPlayed = []
            times = []
            for _ in xrange(numTrials):
                start = time.time()
                win, numRounds = runGame(p=p, alpha=a)
                end = time.time()
                gameResults.append(win)
                roundsPlayed.append(numRounds)
                times.append(end - start)
            numGamesWon = sum([1 for s in gameResults if s])
            success = numGamesWon / float(numTrials)
            meanRoundsPlayed = np.mean(roundsPlayed)
            meanTime = np.mean(times)

            print ' * %d/%d games won:\t%f%% success' % (numGamesWon, numTrials, success)
            print ' * Mean rounds/game:\t%f' % meanRoundsPlayed
            print ' * Mean seconds/game:\t%f' % meanTime
            print ' * Total time (secs):\t%f' % np.sum(times)
            print

            successResults[i][j] = success
            meanRoundResults[i][j] = meanRoundsPlayed

        ax.bar(index + i * bar_width, successResults[i], bar_width,
               alpha=opacity, facecolor=colors[i], label='$p=' + str(p) + '$')
        ax2.bar(index + i * bar_width, meanRoundResults[i], bar_width,
               alpha=opacity, facecolor=colors[i], label='$p=' + str(p) + '$')

        # for plot
        # successRates.append(success)
        # meanRounds.append(meanRoundsPlayed)

    # plt.bar(y_pos, successRates, align='center', alpha=0.5)
    # plt.xticks(y_pos, alphaNames)
    # plt.ylabel('Success rate')
    # plt.xlabel('$\mathbf{\\alpha}$')
    # plt.title('Success rates across values of $\mathbf{\\alpha}$')
    # plt.savefig('plots/successRates.png', dpi=300)

    # plt.bar(y_pos, meanRounds, align='center', alpha=0.5)
    # plt.xticks(y_pos, alphaNames)
    # plt.ylabel('Mean $\#$ of rounds played')
    # plt.xlabel('$\mathbf{\\alpha}$')
    # plt.title('Mean $\#$ of rounds played across values of $\mathbf{\\alpha}$')
    # plt.savefig('plots/meanRounds.png', dpi=300)

    ax.set_xlabel('$\mathbf{\\alpha}$')
    ax.set_ylabel('Success rate')
    ax.set_title('Success rates over $\mathbf{\\alpha}, p$ for random actions')
    ax.set_xticks(map(lambda x : x + 2*bar_width, index))
    ax.set_xticklabels(alphaNames)
    ax.legend()

    ax2.set_xlabel('$\mathbf{\\alpha}$')
    ax2.set_ylabel('Mean $\#$ rounds per game')
    ax2.set_title('Mean $\#$ rounds per game over $\mathbf{\\alpha}, p$ for random actions')
    ax2.set_xticks(map(lambda x : x + 2*bar_width, index))
    ax2.set_xticklabels(alphaNames)
    ax2.legend()

    fig.savefig('plots/successAlphaP_RANDOM.png', dpi=300)
    fig2.savefig('plots/roundsAlphaP_RANDOM.png', dpi=300)
