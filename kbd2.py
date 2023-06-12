import asyncio
import select
import sys
import termios
import tty

cancel = False

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

async def getkey():
    global cancel

    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        while not cancel:
            if isData():
                c = sys.stdin.read(1)
                return c
            await asyncio.sleep(0.1)

        return None

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

'''
async def getkey():
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            # Handle escape sequences
            ch += sys.stdin.read(2)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
'''
