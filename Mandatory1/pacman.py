import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from behaviourTree import *
from algorithms import dijkstra_or_a_star
from random import choice
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
        self.powerPellets = []
        self.currentPellet = None
        self.ghosts = []
        self.currentGhost = None

        self.turningAllowed = False
        self.safeDistance = 7000    # Decides when Pacman should be aware of the ghosts
        self.nearbyDistance = 12000 # Decides when Pacman should deem a ghost nearby.

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

    def setPowerPellets(self, pellets):
        print(pellets)
        self.powerPellets = pellets

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

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
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
        # Update Sprite
        self.sprites.update(dt)

        # Update State
        self.updateState()

        # Adjust values based on state
        self.updateVariables()
        
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
        distance = self.safeDistance + 1
        # Get the distance between Pacman and the Nearest Ghost that is not spawning
        self.nearestGhost()
        if self.currentGhost != None:
            distance = (self.currentGhost.position - self.position).magnitudeSquared()
        
        # If Ghost further away than the safe distance from Pacman, then seek pellets 
        if all(ghost.mode.current == SPAWN for ghost in self.ghosts) or distance > self.safeDistance:
            self.myState = SEEK_PELLET
        else:
            # Else, begin fleeing from the nearby ghosts.
            self.myState = FLEE

        # If ghost is close and in freight, then seek it.
        if self.currentGhost.mode.current == FREIGHT and distance <= self.nearbyDistance:
            self.myState = SEEK_GHOST


    def updateVariables(self):
        if self.myState == SEEK_PELLET:
            self.turningAllowed = False
            self.goal = self.getNearestPellet()
            self.directionMethod = self.pelletDirection
        
        if self.myState == FLEE:
            self.turningAllowed = True
            self.directionMethod = self.fleeDirection
        
        if self.myState == SEEK_GHOST:
            self.turningAllowed = True
            self.goal = self.currentGhost
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

    def getNearestGhostToNode(self, node):
        shortestDistance = float('inf')
        nearestGhost = None

        for ghost in self.ghosts:
            # If ghost is not in the middle of spawning
            if ghost.mode.current != SPAWN:
                # Get the distance between this ghost and Pacman
                distance = (ghost.position - node.position).magnitudeSquared()
                
                # If the distance is shorter than the currently known distance
                # then set this ghost as the nearest at the moment
                if(distance < shortestDistance):
                    shortestDistance = distance
                    nearestGhost = ghost
        
        # Finally set the nearest ghost as the currently targeted one.
        return nearestGhost
    
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
    
    def getNearestPowerPellet(self):
        shortestDistance = float('inf')
        nearestPellet = None
        
        for pellet in self.powerPellets:
            # Measure the Distance between this pellet and Pacman
            distance = (pellet.position - self.position).magnitudeSquared()
            
            # If this pellet is closer than any other distances known
            # then choose this as the currently nearest pellet.
            if(distance < shortestDistance):
                shortestDistance = distance
                nearestPellet = pellet
        
        # Set new target goal as the pellet
        return nearestPellet


    # Seeks the nearest pellet
    def getNearestPellet(self):
        shortestDistance = float('inf')
        nearestPellet = None
        
        for pellet in self.pellets:
            # Measure the Distance between this pellet and Pacman
            distance = (pellet.position - self.position).magnitudeSquared()

            # If this pellet is closer than any other distances known
            # then choose this as the currently nearest pellet.
            if distance < shortestDistance :
                shortestDistance = distance
                nearestPellet = pellet

        return nearestPellet
            

    #############
    # Executes Dijkstra from Ghost's previous node as start
    # to pacman's target node as target.
    def getDijkstraPath(self, direction):
        goal = self.goal
        goal = (goal.position.x, goal.position.y)
        currentNode = self.node
        currentNode = self.nodes.getNodeFromPixels(currentNode.position.x, currentNode.position.y)

        # previous_nodes, shortest_path = dijkstra(self.nodes, currentNode)
        previous_nodes, shortest_path = dijkstra_or_a_star(self.nodes, currentNode, a_star=True)
        path = []
        node = goal
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
        currentNode = self.node
        currentNode = self.nodes.getPixelsFromNode(currentNode)
        path.append(currentNode)
        nextNode = path[1]

        if currentNode[0] > nextNode[0] and 2 in directions : #left
            return 2
        if currentNode[0] < nextNode[0] and -2 in directions : #right
            return -2
        if currentNode[1] > nextNode[1] and 1 in directions : #up
            return 1
        if currentNode[1] < nextNode[1] and -1 in directions : #down
            return -1
        else:
            if -1 * self.direction in directions:
                return -1 * self.direction
            else:
                return choice(directions)
        # up 1, down -1, left 2, right -2
    
    def pelletDirection(self, directions):
        
        # Setup a new direction list
        newDirections = []

        for direction in directions:
            distance = 0

            # Get the node of the direction
            directionNode = self.node.neighbors[direction]

            # Measure the distance between this node, and the nearest ghost to it
            distance += (self.getNearestGhostToNode(directionNode).position - directionNode.position).magnitudeSquared()
            
            # If the ghost is within the safe distance of this node, then avoid the direction
            if distance > self.safeDistance:
                newDirections.append(direction)
        
        # if there are no directions that are safe, then go back.
        if len(newDirections) == 0:
            newDirections.append(self.direction * -1)

        # Begin A* with the newly set directions
        return self.goalDirectionDij(newDirections)

    def fleeDirection(self, directions):
        
        # Setting up.
        directionsToGhosts = []
        something = []

        ghosts = self.getNearbyGhost()
        powerPellet = self.getNearestPowerPellet()

        for ghost in ghosts:
            distance = 0
            if ghost.mode.current != FREIGHT:
                self.goal = ghost
                
                # Get the direction that leads to the ghost
                direction = self.goalDirectionDij(directions)

                # Get the node of the direction
                directionNode = self.node.neighbors[direction]
                
                # Get the distance from this node to all nearby ghosts
                for ghost in ghosts:
                    distance += (ghost.position - directionNode.position).magnitudeSquared()

                # Add to a list.
                directionsToGhosts.append((direction, distance))
        
        # Get the direction and distance of nearest power pellet
        self.goal = powerPellet
        pelletDirection = self.goalDirectionDij(directions)      
        pelletDistance = (powerPellet.position - self.position).magnitudeSquared()              

        # If there is a direction that does not lead to any of the nearby ghost
        # then go with that direction
        for direction in directions:
            badDir = False

            for pair in directionsToGhosts:
                if direction == pair[0]:
                    badDir = True
        
            if badDir == False:
                return direction
        

        # If all directions lead to ghosts
        # then calculate direction with least ghost
        for direction in directions:
            count = 0
            cost = 0

            for pair in directionsToGhosts:
                if pair[0] == direction:
                    count += 1
                    cost += pair[1]
            
            # Additionally, if there is a power pellet in that direction
            # then this direction is more favored
            if pelletDirection == direction:
                count -= 1
                cost -= pelletDistance * 2

            if pelletDistance < 500:
                count = 0
                cost = 0

            something.append((count, cost))
        
        # Finally choose the best direction
        lowestCount = 5
        lowestCost = 0
        bestDir = 0
        for pair in something:
            if(pair[0] <= lowestCount):
                if pair[1] <= lowestCost:
                    lowestCount = pair[0]
                    lowestCost = pair[1]
                    bestDir = something.index(pair)
                
        return directions[bestDir]