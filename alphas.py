import numpy as np
import pandas as pd
from pylab import *
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

def analyzeAlphas(outfile):
    results = [[] for i in xrange(125)]

    for i in xrange(125):
        df = pd.read_csv('runs/sarsa-goal/alpha/goal6_alpha{}.csv'.format(i))
        success = df.success
        results[i] = [sum(success), df.alphaOverlap[0], df. alphaLike[0],
                        df.alphaAction[0]]

    results = pd.DataFrame(results)
    results.to_csv(outfile, header = ['success', 'alphaOverlap',
                    'alphaLike','alphaAction'])

def plotAlphaSuccesses(infile, outfile):
    df = pd.read_csv(infile)

    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111,projection='3d')

    xs = df.alphaOverlap
    ys = df.alphaLike
    zs = df.alphaAction
    colors = cm.Reds(df.success/max(df.success))
    colmap = cm.ScalarMappable(cmap=cm.Reds)
    colmap.set_array(df.success)

    yg = ax.scatter(xs, ys, zs, c=colors, marker='o')
    cb = fig.colorbar(colmap)

    ax.set_xlabel('overlap')
    ax.set_ylabel('likelihood')
    ax.set_zlabel('goodAction')

    plt.savefig(outfile, dpi=300)
    # plt.show()

if __name__ == '__main__':
    # analyzeAlphas('runs/sarsa-goal/alpha/goal6_alphaSUMMARY.csv')
    plotAlphaSuccesses('runs/sarsa-goal/alpha/goal6_alphaSUMMARY.csv',
                        'plots/sarsa-goal/success_alpha_goal6_N100_2.png')
