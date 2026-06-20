import curses
from curses import wrapper
from enum import Enum


class Direction(Enum):
    UP = ord("k")
    RIGHT = ord("l")
    DOWN = ord("j")
    LEFT = ord("h")


class Player:
    x_coord: int
    y_coord: int
    display: str = "@"

    def __init__(self, x=0, y=0):
        self.y_coord = y
        self.x_coord = x

    def move(self, x: str):
        if x == Direction.UP.value:
            self.x_coord += 0
            self.y_coord += -1
        if x == Direction.RIGHT.value:
            self.x_coord += 1
            self.y_coord += 0
        if x == Direction.DOWN.value:
            self.x_coord += 0
            self.y_coord += 1
        if x == Direction.LEFT.value:
            self.x_coord += -1
            self.y_coord += 0


def main():
    wrapper(start)


def start(stdscr):
    curses.curs_set(0)  # hide cursor
    curses.start_color()

    stdscr.refresh()

    player = Player(10, 10)
    stdscr.addstr(player.y_coord, player.x_coord, player.display)

    stdscr.addstr(curses.LINES - 1, 0, "Press Q to quit")
    index = 0
    while True:
        ch = stdscr.getch()
        if ch in (ord("Q"), ord("q")):
            break
        stdscr.clear()
        stdscr.addstr(curses.LINES - 1, 0, "Press Q to quit")
        player.move(ch)
        stdscr.addstr(player.y_coord, player.x_coord, player.display)
        index += 1


if __name__ == "__main__":
    main()
