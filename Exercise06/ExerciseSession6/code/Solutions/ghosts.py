from behaviourTree import (
    EnemyFar,
    Freeze,
    GoTopLeft,
    InvertDecorator,
    IsFlagSet,
    Selector,
    Sequence,
    Wander,
)
from vector import Vector2
from constants import (
    GHOST,
    WHITE,
)
from entity import Entity


class Ghost(Entity):
    def __init__(self, node, nodes, pacman: Entity):
        Entity.__init__(self, node, nodes)
        self.name = GHOST
        self.color = WHITE
        self.speed = 150
        self.pacman = pacman
        self.enemy = self.pacman
        self.goal = Vector2()
        self.directionMethod = self.goalDirection

        self.freeze = False
        self.flag = False

    def update(self, dt):
        self.behaviouralTree()
        if not self.freeze:
            self.timer += dt
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

    def freezeChar(self):
        self.freeze = True

    def setFlag(self):
        self.flag = True

    def behaviouralTree(self):
        distanceToEnemy = (self.position - self.pacman.position).magnitude()

        top_node = Selector(
            [
                Sequence(
                    [
                        InvertDecorator(IsFlagSet(self)),
                        EnemyFar(distanceToEnemy),
                        Wander(self),
                    ]
                ),
                Sequence(
                    [
                        InvertDecorator(EnemyFar(distanceToEnemy)),
                        GoTopLeft(self),
                        Freeze(self),
                    ]
                ),
            ]
        )
        top_node.run()
