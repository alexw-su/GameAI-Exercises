import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from behaviourTree import *
from algorithms import dijkstra_or_a_star
from random import choice
from ghosts import GhostGroup
from random import *

class Pacman(Entity):
    def __init__(self, node, nodes, pellets):
        Entity.__init__(self, node)
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)

        # Additional Implementations
        self.directionMethod = self.goalDirectionDij
        self.states = [SEEK_PELLET, FLEE, SEEK_GHOST]
        self.myState = SEEK_PELLET
        self.nodes = nodes
        self.pellets = pellets
        self.eatenPellets = []
        self.currentPellet = None
        self.pelletNodes = []
        self.ghosts = []
        self.currentGhost = None
        self.safeDistance = 10

    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self):
        self.alive = False
        self.direction = STOP

    def setGhosts(self, ghosts):
        # print('getGhosts', ghosts)
        self.ghosts = ghosts

    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP  

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                self.eatenPellets.append(pellet)
                return pellet
        return None    
    
    def updatePellets(self, pelletList):
        self.pellets = pelletList
    
    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False
    
    #############
    # FOR UPDATE AND SEARCH
    def update(self, dt):
        self.sprites.update(dt)

        # Check State
        self.seekPellet()
        # self.updateState()

        self.updateDirection(dt)

    def updateDirection(self, dt):
        self.position += self.directions[self.direction]*self.speed*dt

        if self.overshotTarget():
            self.node = self.target
            directions = self.validDirections()
            direction = self.directionMethod(directions)

            # Set new target
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            # Update position
            self.setPosition()
        
    def updateState(self):
        nearestGhost = self.nearestGhost()
        distance = (nearestGhost.position - self.position).magnitudeSquared()
        self.currentGhost = nearestGhost
        
        if distance > self.safeDistance:
            self.myState = SEEK_PELLET
            self.seekPellet
        else:
            if nearestGhost.mode.current == FREIGHT:
                self.goal = nearestGhost
                self.myState = SEEK_GHOST
                self.directionMethod = self.goalDirectionDij
            else:
                self.goal = nearestGhost
                self.myState = FLEE
                self.directionMethid = self.fleeDirection
        
        print(self.myState)

    def nearestGhost(self):
        shortestDistance = float('inf')
        nearestGhost = None

        for ghost in self.ghosts:
            distance = (ghost.position - self.position).magnitudeSquared()
            if(distance < shortestDistance):
                shortestDistance = distance
                nearestGhost = ghost
            
        return nearestGhost
        
    def seekPellet(self):
        shortestDistance = float('inf')
        nearestPellet = None

        self.myState = SEEK_PELLET
        for pellet in self.pellets:
            if pellet not in self.eatenPellets:
                pelletNode = self.nodes.getNearestNode(pellet.position)
                distance = (pelletNode.position - self.position).magnitudeSquared()
                if(distance < shortestDistance):
                    shortestDistance = distance
                    nearestPellet = pellet
        self.goal = nearestPellet
        self.currentPellet = nearestPellet
        self.directionMethod = self.goalDirectionDij


    #############
    # Executes Dijkstra from Ghost's previous node as start
    # to pacman's target node as target.
    def getDijkstraPath(self, directions):
        currentGoalNode = self.nodes.getNearestNode(self.goal.position)
        currentGoalNode = self.nodes.getVectorFromLUTNode(currentGoalNode)
        currentPositionNode = self.nodes.getNearestNode(self.position)
        currentPositionNode = self.nodes.getVectorFromLUTNode(currentPositionNode)

        # previous_nodes, shortest_path = dijkstra(self.nodes, ghostTarget)
        previous_nodes, shortest_path = dijkstra_or_a_star(self.nodes, currentPositionNode, a_star=True)
        path = []
        node = currentGoalNode
        while node != currentPositionNode:
            path.append(node)
            node = previous_nodes[node]
        path.append(currentPositionNode)
        path.reverse()
        # print(path)
        return path
    
    # Chooses direction in which to turn based on the dijkstra
    # returned path
    def goalDirectionDij(self, directions):
        path = self.getDijkstraPath(directions)
        
        nextNode = path[1] if len(path) > 1 else path[0]
        diff_x = abs(nextNode[0] - round(self.position.x))
        diff_y = abs(nextNode[1] - round(self.position.y))
        if diff_x > diff_y:
            # Left or Right Movement
            if nextNode[0] < round(self.position.x) and 2 in directions: #left
                print("Next node is to the left.")
                return 2
            elif nextNode[0] > round(self.position.x) and -2 in directions: #right
                print("Next node is to the right.")
                return -2
            else:
                return randint(-1,1)
        else:
            # Up or Down Movement
            if nextNode[1] < round(self.position.y) and 1 in directions: #up
                print("Next node is above.")
                return 1
            elif nextNode[1] > round(self.position.y) and -1 in directions:
                print("Next node is below.")
                return -1
            else:
                print("Next node is vertically aligned with the current node.")
                return randint(-2,2)

        # up 1, down -1, left 2, right -2

    
    def behaviouralTree(self):
        distanceToEnemy = (self.position - self.ge).magnitude()

        top_node = Selector(
            [
                Sequence(
                    [
                        InvertDecorator(IsFlagSet(self)),
                        EnemyFar(distanceToEnemy),
                        SeekPellet(self),
                    ]
                ),
                Sequence(
                    [
                        InvertDecorator(EnemyFar(distanceToEnemy)),
                        GoTopLeft(self),
                        SeekPellet(self),
                    ]
                ),
            ]
        )
        top_node.run()
    
class SeekPellet(Task):
    def __init__(self, character):
        self.character = character
    
    def run(self):
        self.character.myState = SEEK_PELLET
        self.currentPellet = self.character.Get
        self.character.goal = self.character.currentPellet.position
        self.character.directionMethod = self.character.getDijkstraPath

class SeekGhost(Task):
    def __init__(self, character, ghosts):
        self.character = character
        self.ghosts = ghosts

    def run(self):
        self.character.myState = SEEK_GHOST
        self.character.goal = self.character.ghost.position
        self.character.directionMethod = self.character.getDijkstraPath