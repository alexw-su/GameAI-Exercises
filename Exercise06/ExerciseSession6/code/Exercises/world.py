from goalAndActions import Goal, Action


class WorldModel(object):
    # EXERCISE 7
    def __init__(self, goals: list[Goal], timer, actions: list[Action]):
        # TO IMPLEMENT
        pass

    # Finds the goal with highest priority
    def setHighestGoal(self):
        return

    # EXERCISE 8
    # Returns square of goal with max priority
    def calculateDiscontentment(self) -> int:
        raise NotImplementedError()

    # Returns the next unvisited action.
    def nextAction(self) -> Action | None:
        raise NotImplementedError()

    # Simulates chosen action
    def applyAction(self, action):
        return
