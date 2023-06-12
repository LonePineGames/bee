#!/usr/bin/env python3

import datetime
import pytz

def conway_moon_phase(year, month, day):
    r = year % 100
    r %= 19
    if r > 9:
        r -= 19
    r = ((r * 11) % 30) + month + day
    if month < 3:
        r += 2
    r -= int(year < 2000)  # Subtract 1 for 1900-1999, 0 for 2000-2099
    if month > 2:
        r += int(year % 4 == 0) - int((year % 100 == 0) and (year % 400 != 0))

    return (r + 30) % 30

def get_moon_phase_string(moon_phase):
    if moon_phase == 0:
        return "new moon"
    elif moon_phase < 8:
        return "waxing crescent"
    elif moon_phase == 8:
        return "first quarter"
    elif moon_phase < 15:
        return "waxing gibbous"
    elif moon_phase == 15:
        return "full moon"
    elif moon_phase < 22:
        return "waning gibbous"
    elif moon_phase == 22:
        return "last quarter"
    else:
        return "waning crescent"

def main():
    today = datetime.datetime.now(pytz.timezone("US/Pacific"))
    moon_phase = conway_moon_phase(today.year, today.month, today.day)
    moon_phase_string = get_moon_phase_string(moon_phase)

    print(f"Today is {today.strftime('%A, %B %d, %Y')}.")
    print(f"The time is {today.strftime('%I:%M %p %Z')}.")
    print(f"The moon phase is {moon_phase_string}.")

if __name__ == "__main__":
    main()

