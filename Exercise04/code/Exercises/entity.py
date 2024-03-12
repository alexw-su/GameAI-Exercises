import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from algorithms import dijkstra, print_result, dijkstra_or_a_star
from random import randint, choice

class Entity(object):
    def __init__(self, node):
        self.name = None
        self.directions = {UP:Vector2(0, -1),DOWN:Vector2(0, 1), 
                          LEFT:Vector2(-1, 0), RIGHT:Vector2(1, 0), STOP:Vector2()}
        self.direction = STOP
        self.setSpeed(100)
        self.radius = 10
        self.collideRadius = 5
        self.color = WHITE
        self.node = node
        self.setPosition()
        self.target = node
        self.visible = True
        self.disablePortal = False
        self.goal = None
        self.directionMethod = self.wanderBiased
        self.states = [SEEK, FLEE, WANDER, ELSE]
        self.myState = 0

    def setPosition(self):
        self.position = self.node.position.copy()
          
    def validDirection(self, direction):
        if direction is not STOP:
            if self.node.neighbors[direction] is not None:
                return True
        return False

    def getNewTarget(self, direction):
        if self.validDirection(direction):
            return self.node.neighbors[direction]
        return self.node

    def overshotTarget(self):
        if self.target is not None:
            vec1 = self.target.position - self.node.position
            vec2 = self.position - self.node.position
            node2Target = vec1.magnitudeSquared()
            node2Self = vec2.magnitudeSquared()
            return node2Self >= node2Target
        return False

    def reverseDirection(self):
        self.direction *= -1
        temp = self.node
        self.node = self.target
        self.target = temp
        
    def oppositeDirection(self, direction):
        if direction is not STOP:
            if direction == self.direction * -1:
                return True
        return False

    def goalDirection(self, directions):
        distances = []
        for direction in directions:
            vec = self.goal - self.node.position + self.directions[direction]*TILEWIDTH
            distances.append(vec.magnitudeSquared())
        index = distances.index(max(distances))
        return directions[index]


    def setSpeed(self, speed):
        self.speed = speed * TILEWIDTH / 16

    def render(self, screen):
        if self.visible:
            p = self.position.asInt()
            pygame.draw.circle(screen, self.color, p, self.radius)

    def update(self, dt):
        self.position += self.directions[self.direction]*self.speed*dt
         
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
        
    def validDirections(self):
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.validDirection(key):
                if key != self.direction * -1:
                    directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions

    def randomDirection(self, directions):
        return directions[randint(0, len(directions)-1)]


    # EXERCISE 1
    def wanderRandom(self, directions):
        return directions[randint(0, len(directions)-1)]

    # EXERCISE 2
    def wanderBiased(self, directions):
        prevDirection = self.direction
        remainingDirections = []

        for dir in directions:
            if not self.oppositeDirection(dir):
                if not dir == self.direction:
                    remainingDirections.append(dir)

        decision = randint(0, 9)

        if decision <= 4:
            return prevDirection
        else:
            if len(remainingDirections) == 1: 
                return remainingDirections[0]
            else: 
                return remainingDirections[randint(0, len(remainingDirections) - 1)]

    # EXERCISE 3
    def FSMstateChecker(self):
        if self.myState == SEEK:
            self.directionMethod = self.goalDirectionDij
            print("SEEK")
        if self.myState == FLEE:
            self.directionMethod = self.goalDirection
            print("FLEE")
        if self.myState == WANDER:
            self.directionMethod = self.wanderBiased
            print("WANDER")
        if self.myState == ELSE:
            self.myState = choice(self.states)

    #############
    # Executes Dijkstra from Ghost's previous node as start 
    # to pacman's target node as target.
    def getDijkstraPath(self, directions):
        lastPacmanNode = self.pacman.target
        lastPacmanNode = self.nodes.getPixelsFromNode(lastPacmanNode)
        ghostTarget = self.target
        ghostTarget = self.nodes.getPixelsFromNode(ghostTarget)

        # previous_nodes, shortest_path = dijkstra(self.nodes, ghostTarget)
        previous_nodes, shortest_path = dijkstra_or_a_star(self.nodes, ghostTarget, a_star=True)
        path = []
        node = lastPacmanNode
        while node != ghostTarget:
            path.append(node)
            node = previous_nodes[node]
        path.append(ghostTarget)
        path.reverse()
        # print(path)
        return path

    # Chooses direction in which to turn based on the dijkstra
    # returned path
    def goalDirectionDij(self, directions):
        path = self.getDijkstraPath(directions)
        print(path)
        ghostTarget = self.target
        ghostTarget = self.nodes.getPixelsFromNode(ghostTarget)
        path.append(ghostTarget)
        nextGhostNode = path[1]
        if ghostTarget[0] > nextGhostNode[0] and 2 in directions : #left
            return 2
        if ghostTarget[0] < nextGhostNode[0] and -2 in directions : #right
            return -2
        if ghostTarget[1] > nextGhostNode[1] and 1 in directions : #up
            return 1
        if ghostTarget[1] < nextGhostNode[1] and -1 in directions : #down
            return -1
        else:
            print(self.pacman.direction)
            print(directions)
            if -1 * self.pacman.direction in directions:
                return -1 * self.pacman.direction
            else: 
                return choice(directions)
        # up 1, down -1, left 2, right -2
