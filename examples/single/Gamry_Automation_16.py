import subprocess
import time
import pyautogui
import re
from datetime import datetime
import serial

"""
This script is used to automate data collection from a Gamry potentiostat. This method uses pyautogui to control the framework GUI.

The script works by emulating a human operator, calling a preset experiment sequence.
The state of the potentiostat is monitored by watching the color of the status light within the framework window.
The status light location is hardcoded but the 'light_finder.py' script can be used to find the location of the light.
When the green light is detected:
    - The script will call for the next channel.
    - Upon confirmation of the channel, the script will update the experiment sequence with the chosen naming convention and run the sequence.
    - The script will repeat until the green light to be detected for the last channel, indicating that the experiment is complete.
"""

# Change these parameters for each device
device = 'MT4'
sequence_path = r"C:\ProgramData\Gamry Instruments\Framework\Scripts\MT_Series.exp"

# Configuration
channel = None
framework_path = r"C:\Program Files (x86)\Gamry Instruments\Framework\framework.exe"
output_folder = r"C:\Users\gardnerlab\Desktop\Gamry 4 Temp"


# Functions
def go_to_channel(ch):
    global channel
    channel = ch
    ser = serial.Serial(
        port='COM4',
        baudrate=9600,
        timeout=2
        )
    while True:
        response = ser.readline().decode().strip()
        print(">>", response)
        if 'enter channel number' in response.lower():
            break
    ser.write(f'{channel}\r'.encode())
    while True:
        response = ser.readline().decode().strip()
        print(">>", response)
        if 'ok' in response.lower() or f"channel {channel} reached" in response.lower():
            break
    ser.close()
    print(f"Channel {channel} confirmed.")

def update_sequence(sequence_path, device, electrode):
    date_str = datetime.now().strftime("%Y%m%d")
    pattern = r'"(\d{8})_[^_]+_([^_]+)_(.+?\.DTA)"'
    def replace_filename(match):
        new_filename = f'{date_str}_{device}_{electrode}_{match.group(3)}'
        return f'"{new_filename}"'
    with open(sequence_path, 'r') as file:
        lines = file.readlines()

    updated_lines = []
    for line in lines:
        if 'OUTPUT.New' in line and '.DTA' in line:
            updated_line = re.sub(pattern, replace_filename, line)
            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)

    with open(sequence_path, 'w') as file:
        file.writelines(updated_lines)

def launch_framework():
    subprocess.Popen([framework_path])
    time.sleep(10)

def run_sequence(sequence_path):
    pyautogui.hotkey('ctrl', 'n')
    time.sleep(1)
    pyautogui.write(sequence_path)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(3)
    pyautogui.press('enter')
    time.sleep(3)
    pyautogui.press('enter')
    time.sleep(3)
    pyautogui.press('enter')

def is_green(rgb, tol=30):
    r, g, b = rgb
    return r < tol and g > tol and b < tol

def wait_for_green_light(pos=(133,87), poll_interval=1, stable_count=5):
    print(f'Watching pixel at {pos} for green light')
    green_count = 0
    while True:
        pixel = pyautogui.screenshot().getpixel(pos)
        if is_green(pixel):
            green_count += 1
        else:
            green_count = 0

        if green_count >= stable_count:
            print("Green light detected. Experiment complete.")
            break
        time.sleep(poll_interval)

# MAIN SCRIPT

if __name__ == "__main__":

    launch_framework()

    for ch in range(1,17):
        go_to_channel(ch)
        if ch < 10:
            site = f'E0{ch}'
        elif ch >= 10:
            site = f'E{ch}'
        
        update_sequence(sequence_path, device, site)
        run_sequence(sequence_path)
        wait_for_green_light()

    print('All channels complete')































    
    
        
    
