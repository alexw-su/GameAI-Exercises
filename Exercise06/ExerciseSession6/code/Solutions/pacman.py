from typing import Never
from vector import Vector2
from random import choice
from constants import (
    ACCELERATE,
    BOT_LEFT,
    BOT_RIGHT,
    FOLLOW_PATH_TO_TARGET,
    GO_CLOSEST_CORNER,
    GO_IN_SAME_QUADRANT,
    PACMAN,
    SCREENHEIGHT,
    SCREENWIDTH,
    TOP_LEFT,
    TOP_RIGHT,
    VISIT_ANOTHER_QUADRANT,
    WANDER,
    YELLOW,
)
from entity import Entity
from GOAP import GOAP


class Pacman(Entity):
    def __init__(self, node, nodes):
        Entity.__init__(self, node, nodes)
        self.name = PACMAN
        self.color = YELLOW
        self.goal = Vector2()
        self.speed = 150
        self.directionMethod = self.wanderBiased
        self.collideRadius = 5

        # self.myState = FLEE

        self.start_dt = self.timer
        self.cornerReached = False

        self.GOAP = GOAP(depth=3)
        self.GOAPtimer = 0
        self.killedFlag = False
        self.killedTimer = 0

        self.accelerateTimer = 0

    def getGhostObject(self, ghost):
        self.ghost = ghost
        self.enemy = self.ghost

    def update(self, dt):
        self.execGOAP(dt)
        self.goal = self.ghost.position
        self.GOAPtimer += dt
        self.killedTimer += dt
        self.timer += dt
        self.accelerateTimer += dt
        self.position += self.directions[self.direction] * self.speed * dt

        if self.overshotTarget():
            self.node = self.target
            directions = self.validDirections()
            direction = self.directionMethod(directions)
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            self.setPosition()

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            d = self.position - pellet.position
            dSquared = d.magnitudeSquared()
            rSquared = (pellet.radius + self.collideRadius) ** 2
            if dSquared <= rSquared:
                return pellet
        return None

    # EXERCISE 14
    def updateKillFlag(self):
        if self.killedFlag:
            if int(self.killedTimer) >= 15:
                self.killedFlag = False
        else:
            distanceToEnemy: Vector2 = self.position - self.enemy.position
            if distanceToEnemy.magnitude() < 10.0:
                # Set flag to true
                self.killedFlag = True
                # Restart timer from 0, so that it counts how long
                # it has been since enemy was killed.
                self.killedTimer = 0

    def updateQuadrant(self, relevantPosition):
        inLeftHalf = relevantPosition.x <= (SCREENWIDTH / 2)

        inTopHalf = relevantPosition.y <= (SCREENHEIGHT / 2)

        if inTopHalf:
            if inLeftHalf:
                return TOP_LEFT
            else:
                return TOP_RIGHT
        else:
            if inLeftHalf:
                return BOT_LEFT
            else:
                return BOT_RIGHT

    def execGOAP(self, dt):
        self.updateKillFlag()
        self.quadrant = self.updateQuadrant(self.position)
        self.enemyQuadrant = self.updateQuadrant(self.enemy.position)
        nextAction = self.GOAP.run(
            self.killedFlag, self.quadrant, self.enemyQuadrant, dt
        )

        if nextAction is not None:
            if nextAction.name == FOLLOW_PATH_TO_TARGET:
                self.execFollowTarget()
            elif nextAction.name == GO_IN_SAME_QUADRANT:
                self.execGoTargetQuadrant()
            elif nextAction.name == ACCELERATE:
                self.execAccelerate()
            elif nextAction.name == VISIT_ANOTHER_QUADRANT:
                self.execGoDifferentQuadrant()
            elif nextAction.name == WANDER:
                self.execWander()
            elif nextAction.name == GO_CLOSEST_CORNER:
                self.execCorner()

    def execFollowTarget(self):
        self.goal = self.enemy.position
        self.directionMethod = self.goalDirectionDij

    def execAccelerate(self):
        if self.accelerateTimer <= 3:
            self.speed = 200
        else:
            self.speed = 150
            self.accelerateTimer = 0

    def execGoTargetQuadrant(self):
        self.goal = self.goalFromQuadrant(self.enemyQuadrant)

    def execGoDifferentQuadrant(self):
        quads = [TOP_LEFT, TOP_RIGHT, BOT_LEFT, BOT_RIGHT]
        quads.remove(self.quadrant)
        quad = choice(quads)
        self.goal = self.goalFromQuadrant(quad)
        return quad

    def execWander(self):
        self.directionMethod = self.wanderBiased

    def execCorner(self):
        self.goal = self.goalFromQuadrant(self.quadrant)

    def goalFromQuadrant(self, quadrant):
        if self.quadrant == TOP_LEFT:
            return Vector2(16, 64)
        elif self.quadrant == TOP_RIGHT:
            return Vector2(416, 64)
        elif self.quadrant == BOT_LEFT:
            return Vector2(16, 464)
        elif self.quadrant == BOT_RIGHT:
            return Vector2(416, 464)
        return None
