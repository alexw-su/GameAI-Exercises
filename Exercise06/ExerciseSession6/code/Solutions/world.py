import copy

from goalAndActions import Goal, Action


class WorldModel(object):
    def __init__(self, goals: list[Goal], timer, actions: list[Action]):
        self.goals = copy.copy(goals)
        self.actions = copy.copy(actions)
        self.timer = timer
        self.unvisitedActions = copy.copy(self.actions)

        self.setHighestGoal()

    # Finds the goal with highest priority
    def setHighestGoal(self):
        self.highestGoal = max(self.goals, key=lambda goal: goal.value)

    # Returns square of goal with max priority
    def calculateDiscontentment(self):
        return self.highestGoal.getDiscontentment()

    # Returns the next unvisited action.
    # Uses counter to keep track of visited actions.
    def nextAction(self):
        if len(self.unvisitedActions) > 0:
            return self.unvisitedActions.pop(0)
        else:
            return None

    def applyAction(self, action: Action):
        action.getGoalChange(self.highestGoal)
