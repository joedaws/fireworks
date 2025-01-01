import curses
import math
import random
from time import sleep
from enum import Enum, auto


class Phase(Enum):
    RISE = auto()
    EXPAND = auto()
    SPARK = auto()


class PhaseSequence:
    def __init__(self):
        self.index = 0
        self.phase_index = 0
        self.current = Phase.RISE
        self.lengths = {
            Phase.RISE: 8,
            Phase.EXPAND: 10,
            Phase.SPARK: 30,
        }
        self.order = [Phase.RISE, Phase.EXPAND, Phase.SPARK]
        self.bounds = [0] + [sum([self.lengths[p] for p in self.order[:i + 1]]) for i in range(len(self.order))]
        self.total = sum(self.lengths.values())

    def increment(self):
        self.index += 1
        self.phase_index += 1
        self.index = self.index % self.total
        old_phase = self.current
        for i in range(len(self.bounds) - 1):
            if self.bounds[i] <= self.index < self.bounds[i + 1]:
                self.current = self.order[i]
                new_phase = self.current

        if old_phase != new_phase:
            self.phase_index = 0


class Firework:
    def __init__(self, x, max_height):
        self.x = x
        self.max_height = max_height
        self.ps = PhaseSequence()
        self.sparks = []

    def draw(self, stdscr, height, width):
        if self.ps.current == Phase.RISE:
            firework_y = height - 1 - (self.ps.index * (self.max_height // self.ps.lengths[Phase.RISE]))
            if 0 <= firework_y < height and 0 <= self.x < width:
                stdscr.addstr(firework_y, self.x, '*')
        elif self.ps.current == Phase.EXPAND:
            radius = (min(height, width) // 4 / self.ps.lengths[Phase.EXPAND]) * (self.ps.index - self.ps.bounds[1])
            center_y = self.max_height   # Ensure this is the center of the explosion
            for angle in range(0, 360, 10):
                radian = math.radians(angle)
                y = height - int(center_y - radius * math.sin(radian))  # Centered vertically
                x = int(self.x + radius * math.cos(radian))
                if 0 <= y < height and 0 <= x < width:
                    stdscr.addstr(y, x, '*')

        elif self.ps.current == Phase.SPARK:
            if not self.sparks:
                # Initialize sparks at the edge of the explosion ring
                radius = min(height, width) // 4
                for _ in range(30):
                    angle = random.uniform(0, 2 * math.pi)
                    y = self.max_height - radius * math.sin(angle)
                    x = self.x + radius * math.cos(angle)
                    dr = random.uniform(0.2, 0.8)  # Downward velocity
                    dc = random.uniform(-0.2, 0.2)  # Horizontal drift
                    self.sparks.append([y, x, dr, dc])

            for spark in self.sparks:
                if self.ps.phase_index > 0:
                    spark[0] += spark[2]  # Move downward (positive `dr`)
                    spark[1] += spark[3]  # Move horizontally
                y = int(spark[0])
                x = int(spark[1])
                if 0 <= y < height and 0 <= x < width:
                    stdscr.addstr(y, x, '*')

        self.ps.increment()

    def is_done(self):
        return self.ps.current == Phase.SPARK and self.ps.index == self.ps.total - 1


def firework_animation(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Ensure minimum size
    if height < 20 or width < 50:
        stdscr.addstr(0, 0, "Window too small! Please resize to at least 20x50.")
        stdscr.refresh()
        sleep(2)
        return

    fireworks = []
    max_fireworks = 8
    frame_delay = 0.1

    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break

        # Clear screen
        stdscr.clear()

        # Add new fireworks randomly
        if len(fireworks) < max_fireworks and random.random() < 0.1:
            new_x = random.randint(10, width - 10)
            max_height = random.randint(int(height * 0.4), int(height * 0.84))
            fireworks.append(Firework(new_x, max_height))

        # Draw and update fireworks
        for firework in fireworks[:]:
            firework.draw(stdscr, height, width)
            if firework.is_done():
                fireworks.remove(firework)

        stdscr.refresh()
        sleep(frame_delay)


if __name__ == "__main__":
    curses.wrapper(firework_animation)

