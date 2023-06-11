import sys
import select
import tty
import termios

import sys
import select
import tty
import termios
import asyncio

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

async def getkey():
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        while True:
            if isData():
                c = sys.stdin.read(1)
                return c
            await asyncio.sleep(0.1)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

