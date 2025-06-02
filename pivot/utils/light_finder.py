import pyautogui
import time

"""
This script is used to find the location of the status light on the Gamry potentiostat.
The script will print the x and y coordinates of the mouse position every second for 5 seconds.
"""

print('Hover over status light')

for i in range(5):
    x,y = pyautogui.position()
    print(f'Position: {x}, {y}')
    time.sleep(1)
