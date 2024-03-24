class GOAP(object):
    # EXERCISE 9
    def __init__(self, depth):
        self.depth = depth
        # GOALS

        # ACTIONS FOR GOAL: KILL_GHOST

        # ACTIONS FOR GOAL: EAT_SUPERPELLETS

        return

    # EXERCISE 10
    def updateWorldState(self):
        return

    # EXERCISE 3
    def planAction(self, worldModel, maxDepth):
        # Create storage for world models at each depth, and
        # actions that correspond to them
        models = [None] * int(self.depth + 1)
        actions = [None] * int(self.depth)

        # IMPLEMENT THE REST OF THE METHOD BELOW:
        return

    # EXERCISE 11
    def updateActionsValues(self):
        return

    # EXERCISE 12
    # Method for checking if goal values have to change.
    def updateGoalsValues(self):
        return

    # EXERCISE 13
    def run(self):
        return
