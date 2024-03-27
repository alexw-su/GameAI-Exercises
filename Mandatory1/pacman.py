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
    def __init__(self, node, nodes):
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
        self.pellets = []
        self.eatenPellets = []
        self.currentPellet = None
        self.ghosts = []
        self.currentGhost = None
        self.timer = 0

        self.turningAllowed = False
        self.safeDistance = 7000    # Decides when Pacman should be aware of the ghosts
        self.nearbyDistance = 10000 # Decides when Pacman should deem a ghost nearby.
        self.huntingTime = 5        # Decides how long Pacman should seek ghost before stopping

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
        self.ghosts = ghosts

    def setPellets(self, pellets):
        self.pellets = pellets

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
        # Update Timer
        if any(ghost.mode.current == FREIGHT for ghost in self.ghosts):
            self.timer += dt
        else:
            self.timer = 0

        # Update Sprite
        self.sprites.update(dt)

        # Update State
        self.updateState()
        
        # Update Direction
        self.updateDirection(dt)

    # Updates the directions
    def updateDirection(self, dt):

        if self.overshotTarget():
            self.node = self.target
            directions = self.validDirections()
            direction = self.directionMethod(directions)

            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]

            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            # Update position
            self.setPosition()
        
        # Add to position based on direction
        self.position += self.directions[self.direction]*self.speed*dt
    
    # Updates state
    def updateState(self):
        # Get the distance between Pacman and the Nearest Ghost that is not spawning
        self.nearestGhost()
        distance = (self.currentGhost.position - self.position).magnitudeSquared()
        
        # If Ghost further away than the safe distance from Pacman, then seek pellets 
        if distance > self.safeDistance or all(ghost.mode.current == SPAWN for ghost in self.ghosts):
            self.myState = SEEK_PELLET
            self.turningAllowed = False
            self.seekPellet()
        else:
            # Else, begin fleeing from the nearby ghosts.
            self.myState = FLEE
            self.turningAllowed = True
            self.directionMethod = self.fleeDirection
        
        # If ghost is close and in freight, then seek it.
        if self.currentGhost.mode.current == FREIGHT and distance <= self.nearbyDistance and 0 < self.timer < self.huntingTime:
            self.myState = SEEK_GHOST
            self.turningAllowed = True
            self.goal = self.currentGhost
            # Use A* to seek this ghost.
            self.directionMethod = self.goalDirectionDij

    # Get the nearest ghost that is not spawning
    def nearestGhost(self):
        shortestDistance = float('inf')
        nearestGhost = None

        for ghost in self.ghosts:
            # If ghost is not in the middle of spawning
            if ghost.mode.current != SPAWN:
                # Get the distance between this ghost and Pacman
                distance = (ghost.position - self.position).magnitudeSquared()
                
                # If the distance is shorter than the currently known distance
                # then set this ghost as the nearest at the moment
                if(distance < shortestDistance):
                    shortestDistance = distance
                    nearestGhost = ghost
        
        # Finally set the nearest ghost as the currently targeted one.
        self.currentGhost = nearestGhost
    
    
    def getNearbyGhost(self):
        nearbyGhost = []

        for ghost in self.ghosts:
            # If ghost is not in the middle of spawning
            if ghost.mode.current != SPAWN:
                # Get the distance between this ghost and Pacman
                distance = (ghost.position - self.position).magnitudeSquared()
                
                # If the distance is shorter than the currently known distance
                # then set this ghost as the nearest at the moment
                if(distance < self.nearbyDistance):
                    nearbyGhost.append(ghost)
        
        # Finally set the nearest ghost as the currently targeted one.
        return nearbyGhost
        

    # Seeks the nearest pellet
    def seekPellet(self):
        shortestDistance = float('inf')
        nearestPellet = None
        self.myState = SEEK_PELLET
        
        for pellet in self.pellets:
            # Measure the Distance between this node and Pacman
            distance = (pellet.position - self.position).magnitudeSquared()
            
            # If this node of a pellet is closer than any other distances known
            # then choose this as the currently nearest pellet.
            if(distance < shortestDistance):
                shortestDistance = distance
                nearestPellet = pellet
        
        # Set new target goal as the pellet
        self.goal = nearestPellet
        self.currentPellet = nearestPellet

        # Use A* to seek this pellet
        self.directionMethod = self.goalDirectionDij


    #############
    # Executes Dijkstra from Ghost's previous node as start
    # to pacman's target node as target.
    def getDijkstraPath(self, directions):
        goal = self.goal
        goalNode = (goal.position.x, goal.position.y)
        currentNode = self.target
        currentNode = self.nodes.getNodeFromPixels(currentNode.position.x, currentNode.position.y)

        # previous_nodes, shortest_path = dijkstra(self.nodes, currentNode)
        previous_nodes, shortest_path = dijkstra_or_a_star(self.nodes, currentNode, a_star=True)
        path = []
        node = goalNode
        while node != currentNode:
            path.append(node)
            if node in previous_nodes:
                node = previous_nodes[node]
            else:
                break
        path.append(currentNode)
        path.reverse()
        # print(path)
        return path
    
    # Chooses direction in which to turn based on the dijkstra
    # returned path
    def goalDirectionDij(self, directions):
        path = self.getDijkstraPath(directions)
        currentTarget = self.target
        currentTarget = self.nodes.getVectorFromLUTNode(currentTarget)
        path.append(currentTarget)
        nextNode = path[1]

        if currentTarget[0] > nextNode[0] and 2 in directions : #left
            return 2
        if currentTarget[0] < nextNode[0] and -2 in directions : #right
            return -2
        if currentTarget[1] > nextNode[1] and 1 in directions : #up
            return 1
        if currentTarget[1] < nextNode[1] and -1 in directions : #down
            return -1
        else:
            if -1 * self.direction in directions:
                return -1 * self.direction
            else:
                return choice(directions)
        # up 1, down -1, left 2, right -2

    def fleeDirection(self, directions):
        vec = 0
        distances = []
        for direction in directions:
            for ghost in self.getNearbyGhost() :
                vec += (self.position + self.directions[direction]*TILEWIDTH - ghost.position).magnitudeSquared()
            distances.append(vec)
            vec = 0
        index = distances.index(max(distances))
        print("Distances :"+str(distances))
        print("Choice :"+str(directions[index]))
        return directions[index]
    
    def validDirections(self):
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.validDirection(key):
                if key == self.direction * -1 and self.turningAllowed:
                    directions.append(key)
                elif key != self.direction * -1:
                    directions.append(key)

        if len(directions) == 0 : 
            directions.append(self.direction * -1)
        return directions