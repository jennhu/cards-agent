'''
Returns a list of all subsets of a set s.
'''
def powerset(s):
    return reduce(lambda z, x: z + [y + [x] for y in z], s, [[]])

class Goal:
    def __init__(self, start, suit):
        self.start = start
        self.suit = suit
    def weight(history):
        # TODO
        pass
    def __repr__(self):
        return 'Goal(%d,%d)' % (self.start, self.suit)

class Card:
    def __init__(self, val, suit):
        self.val = val
        self.suit = suit
    def __repr__(self):
        return 'Card(%d,%d)' % (self.val, self.suit)

goals = [Goal(i, j) for i in xrange(13) for j in xrange(4)]

'''
Returns true iff cards is a subset of goal.
'''
def overlap(goal, cards):
    for c in cards:
        print c
        if c.suit != goal.suit:
            return False
        elif c.val < goal.start and goal.start + 5 < 13:
            return False
        elif c.val > (goal.start + 5) % 13:
            return False
    return True

'''
Distance. Returns the minimum number of cards needed to obtain a goal.
'''
def dist(cards):
    pass

'''
Flexibility. Returns the number of possible goals that use
every subset of cards.
'''
def flex(cards):
    # remove [] from powerset
    subsets = filter(None, powerset(cards))
    possibleGoals = {g for g in goals for s in subsets if overlap(g,s)}
    return len(possibleGoals)

'''
Testing.
'''
def runTests():
    g1 = Goal(0,0)
    c1 = [Card(2,0), Card(5,0)]
    g2 = Goal(0,0)
    c2 = [Card(2,1)]
    g3 = Goal(0,0)
    c3 = [Card(2,0), Card(5,0), Card(11,0)]
    g4 = Goal(10,0)
    c4 = [Card(0,0)]
    print overlap(g1,c1)
    print overlap(g2,c2)
    print overlap(g3,c3)
    print overlap(g4,c4)
    print flex([Card(0,0), Card(4,0), Card(8,0)])
    print flex([Card(5,0), Card(6,0)])
    print flex([Card(0,0), Card(5,1)])
    print flex([Card(0,0)])
    print flex([Card(5,1)])
    print flex([Card(4,3)])
    print flex([Card(1,0)])

# runTests()

# numSuit = 12
# straights = []
# for i in xrange(numSuit):
#     straights.append([(i + j) % numSuit for j in range(6)])
