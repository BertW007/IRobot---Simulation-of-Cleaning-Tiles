import math
import random

import visualize
import pylab

class Position(object):
    # A Position represents a location in a two-dimensional room.
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
    
    def getNewPosition(self, angle, speed):
        """
        angle: number representing angle in degrees, 0 <= angle < 360
        speed: positive float representing speed
        """
        old_x, old_y = self.getX(), self.getY()
        angle = float(angle)
        # Compute the change in position
        delta_y = speed * math.cos(math.radians(angle))
        delta_x = speed * math.sin(math.radians(angle))
        # Add that to the existing position
        new_x = old_x + delta_x
        new_y = old_y + delta_y
        return Position(new_x, new_y)

    def __str__(self):  
        return "(%0.2f, %0.2f)" % (self.x, self.y)


class RectangularRoom(object):
    """
    A RectangularRoom represents a rectangular region containing clean or dirty
    tiles.
    """
    def __init__(self, width, height):
        """
        Initializes a rectangular room with the specified width and height.
        width: an integer > 0
        height: an integer > 0
        """
        self.width = width
        self.height = height
        self.total_tiles = width * height
        self.clean_tiles = []

    
    def cleanTileAtPosition(self, pos):
        """
        Mark the tile under the position POS as cleaned.
        pos: a Position
        """
        tile = (int(pos.getX()), int(pos.getY()))
        if tile not in self.clean_tiles:
            self.clean_tiles.append(tile)

    def isTileCleaned(self, m, n):
        """
        Assumes that (m, n) represents a valid tile inside the room.
        m: an integer
        n: an integer
        """
        check_tile = (int(m), int(n))
        if check_tile in self.clean_tiles:
            return True
        else:
            return False

    def getNumTiles(self):
        return self.total_tiles

    def getNumCleanedTiles(self):
        return len(self.clean_tiles)

    def getRandomPosition(self):
        # Return a random position inside the room.
        return Position(random.random() * self.width, random.random() * self.height)

    def isPositionInRoom(self, pos):
        if 0 <= pos.getX() < self.width and 0 <= pos.getY() < self.height:
            return True
        else:
            return False

class Robot(object):
    """
    Represents a robot cleaning a particular room.
    At all times the robot has a particular position and direction in the room.
    The robot also has a fixed speed.
    """
    def __init__(self, room, speed):
        """
        Initializes a Robot with the given speed in the specified room. The
        robot initially has a random direction and a random position in the
        room. The robot cleans the tile it is on.

        room:  a RectangularRoom object.
        speed: a float (speed > 0)
        """
        self.room = room
        self.speed = speed
        self.position = room.getRandomPosition()
        self.direction = random.random() * 360
        self.clean_tiles = room.cleanTileAtPosition(self.position)

    def getRobotPosition(self):
        return self.position

    def getRobotDirection(self):
        return self.direction

    def setRobotPosition(self, position):
        self.position = position

    def setRobotDirection(self, direction):
        self.direction = direction

    def updatePositionAndClean(self):
        pass


class StandardRobot(Robot):
    """ A StandardRobot is a Robot with the standard movement strategy.
        Move the robot to a new position and mark the tile it is on as having
        been cleaned.
    """
    def updatePositionAndClean(self):
        # Simulate the passage of a single time-step.
        new_position = self.position.getNewPosition(self.direction, self.speed)
        if self.room.isPositionInRoom(new_position):
            self.position = new_position
            self.room.cleanTileAtPosition(new_position)
        else:
            while not self.room.isPositionInRoom(new_position):
                self.direction = random.random() * 360
                new_position = self.position.getNewPosition(self.direction, self.speed)
        return new_position


class RandomWalkRobot(Robot):
    """
    A RandomWalkRobot is a robot with the "random walk" movement strategy: itu
    chooses a new direction at random at the end of each time-step.
    """
    def updatePositionAndClean(self):
        new_position = self.position.getNewPosition(self.direction, self.speed)
        if self.room.isPositionInRoom(new_position):
            self.position = new_position
            self.room.cleanTileAtPosition(new_position)
            self.direction = random.random() * 360
        else:
            while not self.room.isPositionInRoom(new_position):
                self.direction = random.random() * 360
                new_position = self.position.getNewPosition(self.direction, self.speed)


def run_simulation(num_robots, speed, width, height, min_coverage, num_trials, robot_type):
    """
    Runs NUM_TRIALS trials of the simulation and returns the mean number of
    time-steps needed to clean the fraction MIN_COVERAGE of the room.

    The simulation is run with NUM_ROBOTS robots of type ROBOT_TYPE, each with
    speed SPEED, in a room of dimensions WIDTH x HEIGHT.

    num_robots: an int (num_robots > 0)
    speed: a float (speed > 0)
    width: an int (width > 0)
    height: an int (height > 0)
    min_coverage: a float (0 <= min_coverage <= 1.0)
    num_trials: an int (num_trials > 0)
    robot_type: class of robot to be instantiated (e.g. StandardRobot or
                RandomWalkRobot)
    """
    times = []

    def trial():
        animation = visualize.RobotVisualization(num_robots, width, height)
        room = RectangularRoom(width, height)
        robots = []

        for i in range(num_robots):
            robots.append(robot_type(room, speed))

        time_in_sec = 0
        room_size = room.getNumTiles()
        ratio = room.getNumCleanedTiles() / room_size
        while ratio < min_coverage:
            time_in_sec += 1
            for robot in robots:
                robot.updatePositionAndClean()
            ratio = room.getNumCleanedTiles() / room_size
            animation.update(room, robots)
        animation.done()
        return time_in_sec

    for i in range(num_trials):
        times.append(trial())
    return int(sum(times) / num_trials)


def show_plot1(title, x_label, y_label):
    num_robot_range = range(1, 11)
    times1 = []
    times2 = []
    for num_robots in num_robot_range:
        print("Plotting", num_robots, "robots...")
        times1.append(run_simulation(num_robots, 1.0, 20, 20, 0.8, 20, StandardRobot))
        times2.append(run_simulation(num_robots, 1.0, 20, 20, 0.8, 20, RandomWalkRobot))
    pylab.plot(num_robot_range, times1)
    pylab.plot(num_robot_range, times2)
    pylab.title(title)
    pylab.legend(('StandardRobot', 'RandomWalkRobot'))
    pylab.xlabel(x_label)
    pylab.ylabel(y_label)
    pylab.show()


def show_plot2(title, x_label, y_label):
    aspect_ratios = []
    times1 = []
    times2 = []
    for width in [10, 20, 25, 50]:
        height = 300//width
        print("Plotting cleaning time for a room of width:", width, "by height:", height)
        aspect_ratios.append(float(width) / height)
        times1.append(run_simulation(2, 1.0, width, height, 0.8, 200, StandardRobot))
        times2.append(run_simulation(2, 1.0, width, height, 0.8, 200, RandomWalkRobot))
    pylab.plot(aspect_ratios, times1)
    pylab.plot(aspect_ratios, times2)
    pylab.title(title)
    pylab.legend(('StandardRobot', 'RandomWalkRobot'))
    pylab.xlabel(x_label)
    pylab.ylabel(y_label)
    pylab.show()
    return aspect_ratios

# print(run_simulation(1, 1.0, 5, 5, 1, 1, StandardRobot))
# print(run_simulation(1, 1.0, 5, 5, 1, 1, RandomWalkRobot))

# print(show_plot1('Time It Takes 1 - 10 Robots To Clean 80% Of A Room correct', 'Number of Robots', 'Time-steps'))
# print(show_plot2('Time It Takes Two Robots To Clean 80% Of Variously Shaped Rooms', 'Aspect Ratio', 'Time-steps'))
