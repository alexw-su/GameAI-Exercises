from constants import EAT_SUPERPELLETS, KILL_GHOST


# EXERCISE 4
class Goal(object):
    def __init__(self, name, value):
        # TO IMPLEMENT
        pass

    def getDiscontentment(self):
        # TO IMPLEMENT
        return

    def updateValue(self, newValue):
        # TO IMPLEMENT
        return


class Action(object):
    # EXERCISE 5
    def __init__(self, name):
        # TO IMPLEMENT
        pass

    def getGoalChange(self, goal):
        return


######
class FollowPathToTarget(Action):
    def __init__(self, name):
        Action.__init__(self, name)
        self.value = 5

    def getGoalChange(self, goal):
        if goal.name == KILL_GHOST:
            goal.value -= self.value
        else:
            goal.value += 100


class GoInSameQuadrant(Action):
    def __init__(self, name):
        Action.__init__(self, name)
        self.value = 4

    def getGoalChange(self, goal):
        if goal.name == KILL_GHOST:
            goal.value -= self.value
        else:
            goal.value += 100


class Accelerate(Action):
    def __init__(self, name):
        Action.__init__(self, name)
        self.value = 2

    def getGoalChange(self, goal):
        if goal.name == KILL_GHOST:
            goal.value -= self.value
        else:
            goal.value += 100


####
class VisitAnotherQuadrant(Action):
    def __init__(self, name):
        Action.__init__(self, name)
        self.value = 4

    def getGoalChange(self, goal):
        if goal.name == EAT_SUPERPELLETS:
            goal.value -= self.value
        else:
            goal.value += 100


class Wander(Action):
    def __init__(self, name):
        Action.__init__(self, name)
        self.value = 10

    def getGoalChange(self, goal):
        if goal.name == EAT_SUPERPELLETS:
            goal.value -= self.value
        else:
            goal.value += 100


class GoClosestCorner(Action):
    def __init__(self, name):
        Action.__init__(self, name)
        self.value = 2

    def getGoalChange(self, goal):
        if goal.name == EAT_SUPERPELLETS:
            goal.value -= self.value
        else:
            goal.value += 100


class Dummy(Action):
    def __init__(self, name):
        Action.__init__(self, name)
        self.value = 1

    def getGoalChange(self, goal):
        goal.value -= self.value
