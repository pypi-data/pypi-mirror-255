# coding: utf-8

from __future__ import annotations

from pathlib import Path
import time
import curses
import json

import pyautogui as pyag


class Click:
    def __init__(self, pos):
        self.pos = pos

    def __repr__(self):
        return f'Click({self.pos})'

    def __call__(self):
        pyag.moveTo(self.pos)
        time.sleep(0.01)
        pyag.mouseDown()
        time.sleep(0.05)
        pyag.mouseUp()


def main():
    # make a directory for the config file if necessary
    config_file = Path('~/.config/click_outside_the_box/config.json').expanduser()
    config_file.parent.mkdir(exist_ok=True, parents=True)

    # use screen go capture keypresses, gives you a blank screen in the terminal
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    screen.keypad(True)

    pyag.PAUSE = 0.01
    try:
        data = json.load(config_file.open())
    except:
        data = {}
    actions = []
    command = pyag.Point(**data['command']) if 'command' in data else None
    outside = pyag.Point(**data['outside']) if 'outside' in data else None
    score = pyag.Point(**data['score']) if 'score' in data else None

    try:
        while True:
            char = chr(screen.getch())
            if char == 'Q':              # quit the program nicely
                break
            if char == 'f':  # click
                actions.append(Click(pyag.position()))
            elif char == 'c':            # clean the click buffer
                # print(actions)
                actions = []
            elif char == 'r':            # replay the clicks
                last_pos = pyag.position()
                if not actions:
                    continue
                for idx, action in enumerate(actions):
                    if idx == 0:
                        # activate window by clicking 
                        pyag.click(outside)
                        time.sleep(0.5)
                        # activate the actual play area
                        pyag.click(score)
                        time.sleep(0.01)
                    action()
                    time.sleep(0.09)
                pyag.click(outside)   # deactivate play eare
                time.sleep(0.1)
                pyag.click(command)   # make sure keypresses go the command terminal
                pyag.moveTo(last_pos) # hover above the last, user determined, position of the mouse
                actions = []
            elif char == 'z':
                command = pyag.position()
                data['command'] = command._asdict()
                json.dump(data, config_file.open('w'))
                continue
            elif char == 'x':
                outside = pyag.position()
                data['outside'] = outside._asdict()
                json.dump(data, config_file.open('w'))
                continue
            elif char == 'X':
                score = pyag.position()
                data['score'] = score._asdict()
                json.dump(data, config_file.open('w'))
                continue
            else:
                print('\n', char, ord(char))
            if outside is None:
                print('second use "x" to set the cursor position outside of, but close to, the play aread')
                continue
            if score is None:
                print('second use "X" to set the cursor position in a non-active part of the play area')
                continue
            if command is None:
                print('first use "z" to set the cursor position of the command window')
                continue
    finally:
        # restore terminal to normality
        curses.nocbreak();
        screen.keypad(0);
        curses.echo()
        curses.endwin()
    return 0

if __name__ == '__main__':
    sys.exit(main())
