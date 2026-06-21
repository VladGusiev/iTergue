import curses
from curses import wrapper

from Player import Player


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
