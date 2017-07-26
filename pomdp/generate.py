'''
generate.py is a script for generating a .POMDP file to feed into
a POMDP solver (see http://www.pomdp.org/ for more details).
'''

# import numpy as np

# get header text
def getHeader(headerFile):
    with open(headerFile) as myfile:
        header = ''.join(line for line in myfile)
        return header

# concatenates a prefix string to every element of a list
def addPrefix(prefix, l):
    return map(lambda i : prefix+str(i), l)

# makes the preamble text
def makePreamble(d):
    v_str = 'values: {}'.format(d['vals'])
    d_str = 'discount: {}'.format(d['disc'])
    s_str = 'states: {}'.format(' '.join(addPrefix('s', d['states'])))
    a_str = 'actions: {}'.format(' '.join(addPrefix('a', d['actions'])))
    o_str = 'observations: {}'.format(' '.join(addPrefix('o', d['obs'])))
    start_str = 'start: {}'.format(d['start'])
    # start_str = 'start: {}'.format(' '.join(map(str, d['start'])))
    preamble_strs = [v_str, d_str, s_str, a_str, o_str, start_str]
    preamble = '\n'.join(s for s in preamble_strs)
    return preamble

'''
variables
'''

numStates = 20
numActions = 34 # (3 choose 1)*(4 choose 1) + (3 choose 2)*(4 choose 2) + (3 choose 3)*(4 choose 3)
numObs = 8

'''
preamble
'''
preambleDict = {
    'vals'      : 'reward',
    'disc'      : 0.9,
    'states'    : xrange(numStates),
    'actions'   : xrange(numActions),
    'obs'       : xrange(numObs),
    'start'     : 'uniform'
}
preamble = makePreamble(preambleDict)
print preamble

'''
transition probabilities
'''
#
# transDict = {i : np.zeros((numStates, numStates)) for i in xrange(numActions)}
#
# for i in xrange(numActions):
#     transDict[i] = np.random.random((numStates, numStates))
