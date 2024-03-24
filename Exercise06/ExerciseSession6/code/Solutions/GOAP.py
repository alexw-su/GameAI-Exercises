import copy
import sys
from world import WorldModel
from constants import (
    ACCELERATE,
    EAT_SUPERPELLETS,
    FOLLOW_PATH_TO_TARGET,
    GO_CLOSEST_CORNER,
    GO_IN_SAME_QUADRANT,
    KILL_GHOST,
    VISIT_ANOTHER_QUADRANT,
    WANDER,
)
from goalAndActions import (
    Accelerate,
    Action,
    Dummy,
    FollowPathToTarget,
    GoClosestCorner,
    GoInSameQuadrant,
    Goal,
    VisitAnotherQuadrant,
    Wander,
)


class GOAP(object):
    def __init__(self, depth):
        self.depth = depth
        self.timer = 0

        # GOALS
        self.killGhost = Goal(KILL_GHOST, 1)
        # self.wander = Goal(WANDER, 2)
        self.eatSuperpellets = Goal(EAT_SUPERPELLETS, 100)
        self.goals = [self.killGhost, self.eatSuperpellets]

        # ACTIONS FOR GOAL: KILL_GHOST
        self.followPathToTarget = FollowPathToTarget(FOLLOW_PATH_TO_TARGET)
        self.goInSameQuadrant = GoInSameQuadrant(GO_IN_SAME_QUADRANT)
        self.accelerate = Accelerate(ACCELERATE)

        # ACTIONS FOR GOAL: EAT_SUPERPELLETS
        self.visitAnotherQuadrant = VisitAnotherQuadrant(VISIT_ANOTHER_QUADRANT)
        self.wander = Wander(WANDER)
        self.goClosestCorner = GoClosestCorner(GO_CLOSEST_CORNER)
        self.dummy = Dummy("DUMMY")

        self.actionsKILL = [
            self.followPathToTarget,
            self.goInSameQuadrant,
            self.accelerate,
        ]
        self.actionsEAT = [self.visitAnotherQuadrant, self.wander, self.goClosestCorner]
        self.actions = self.actionsKILL + self.actionsEAT + [self.dummy]
        # self.actions = self.actionsEAT

        self.updateWorldState()

    def updateWorldState(self):
        self.worldState = WorldModel(self.goals, self.timer, self.actions)

    def planAction(self, worldModel, maxDepth):
        # Create storage for world models at each depth, and
        # actions that correspond to them
        models: list[None | WorldModel] = [None] * int(self.depth + 1)
        actions: list[None | Action] = [None] * int(self.depth)

        # Set up the initial data.
        models[0] = worldModel
        currentDepth = 0

        # Keep track of the best action.
        bestAction = None
        bestValue = sys.maxsize

        # Iterate all actions at depth zero.
        while currentDepth >= 0:
            currentModel = models[currentDepth]
            assert currentModel
            # Check if we’re at maximum depth.
            if currentDepth >= maxDepth:
                # Calculate discontentment at the deepest level.
                currentValue = currentModel.calculateDiscontentment()

                # If the current value is the best, store the first step of how we got here.
                if currentValue < bestValue:
                    bestValue = currentValue
                    assert actions[0]
                    bestAction = actions[0]

                # We’re done at this depth, so drop back.
                currentDepth -= 1
            else:
                # Otherwise, we need to try the next action.
                nextAction = currentModel.nextAction()

                # We have an action to apply, copy the current model.
                if nextAction:
                    modelCopy = copy.deepcopy(currentModel)

                    # and apply the action to the copy.
                    actions[currentDepth] = nextAction
                    modelCopy.applyAction(nextAction)
                    models[currentDepth + 1] = modelCopy

                    # and process it on the next iteration.
                    currentDepth += 1

                # Otherwise we have no action to try, so we’re done at this level.
                else:
                    # Drop back to the next highest level.
                    currentDepth -= 1

        return bestAction

    # Method for checking if goal values have to change.
    # In this implementation, it's based on killFlag.
    def updateGoalsValues(self, killFlag):
        if killFlag:
            self.killGhost.value = 1
            self.eatSuperpellets.value = 1000
        else:
            self.killGhost.value = 1000
            self.eatSuperpellets.value = 1

    def updateActionsValues(self, myQuadrant, enemyQuadrant):
        # KILL ENEMY ACTIONS
        # If I am in same quadrant
        if myQuadrant == enemyQuadrant:
            self.follow_acc_quad()
        # If I am in diagonally opposite quadrant of enemy
        elif myQuadrant == enemyQuadrant * -1:
            self.quad_acc_follow()
        else:
            self.acc_quad_follow()

        # EAT PELLETS ACTIONS
        # Rotate between actions:
        # 1) go to closest corner
        # 2) wander
        # 3) go to different quadrant
        # 4) repeat

        if self.timer >= 0.0 and self.timer <= 2.0:
            self.corner_wander_changequad()
        elif self.timer > 2.0 and self.timer <= 6.0:
            self.wander_changequad_corner()
        elif self.timer > 6.0 and self.timer <= 11.0:
            self.changequad_wander_corner()
        else:
            self.timer = 0.0

    def run(self, killFlag, quadrant, enemyQuadrant, dt):
        self.timer += dt
        self.updateWorldState()
        self.updateGoalsValues(killFlag)
        self.updateActionsValues(quadrant, enemyQuadrant)
        nextAction = self.planAction(self.worldState, self.depth)
        return nextAction

    def quad_acc_follow(self):
        self.goInSameQuadrant.value = 100
        self.accelerate.value = 5
        self.followPathToTarget.value = 1

    def acc_quad_follow(self):
        self.accelerate.value = 100
        self.goInSameQuadrant.value = 5
        self.followPathToTarget.value = 2

    def follow_acc_quad(self):
        self.followPathToTarget.value = 100
        self.accelerate.value = 5
        self.goInSameQuadrant.value = 2

    ##############################################
    def changequad_wander_corner(self):
        self.visitAnotherQuadrant.value = 100
        self.wander.value = 5
        self.goClosestCorner.value = 1

    def wander_changequad_corner(self):
        self.wander.value = 100
        self.visitAnotherQuadrant.value = 5
        self.goClosestCorner.value = 1

    def corner_wander_changequad(self):
        self.goClosestCorner.value = 100
        self.wander.value = 5
        self.visitAnotherQuadrant.value = 1
