from vector import Vector2

# EXERCISE 2
class Task(object):
    def run(self) -> bool:
        raise NotImplementedError()

    def __str__(self) -> str:
        return self.__class__.__name__
    


# EXERCISE 3
class Selector(Task):
    def __init__(self, children) -> None:
        self.children = children

    def run(self) -> bool:
        for c in self.children:
            if c.run() :
                return True
        return False

class Sequence(Task):
    def __init__(self, children) -> None:
        self.children = children

    def run(self) -> bool:
        for c in self.children:
            if not c.run():
                return False
        return True

enemyCloseDistance = 15

# EXERCISE 4
class EnemyFar(Task):
    def __init__(self, distanceToEnemy: float):
        self.distanceToEnemy = distanceToEnemy

    def run(self):
        if self.distanceToEnemy > enemyCloseDistance:
            return True
        else:
            return False



# EXERCISE 5
class Wander(Task):
    pass



# EXERCISE 6
class EnemyNear(Task):
    pass



# EXERCISE 8
class GoTopLeft(Task):
    pass



# EXERCISE 9
class Freeze(Task):
    pass
        

class IsFlagSet(Task):
    def __init__(self, character):
        self.character = character
    def run(self):
        if self.character.setFlag:
            return False
        else:
            return True