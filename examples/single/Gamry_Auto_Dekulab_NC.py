import subprocess
import time
import pyautogui
import re
import os
from datetime import datetime
import serial
import json

"""
This script is used to automate data collection from a Gamry potentiostat. This method uses pyautogui to control the framework GUI.

Similar to the Gamry_Automation_16.py script, but designed for the Dekulab naming convention with a persistent test ID counter.
Test ID information is stored in the 'pivot\utils\test_id_counter.json' file.
"""

# Change these parameters for each device
wafer = "waferID"
device = "deviceID"
electrolyte = "electrolyteID"

# Configuration
channel = None
framework_path = r"C:\Program Files (x86)\Gamry Instruments\Framework\framework.exe"
output_folder = r"C:\Users\Tim\Documents\GAMRY 3_RawData"
sequence_path = r"C:\ProgramData\Gamry Instruments\Framework\Scripts\HL_Series_Script.exp"

# Functions

def go_to_channel(ch):
    global channel
    channel = ch
    ser = serial.Serial(
        port='COM3',
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

def get_test_ids(date_str, count, counter_file=r'pivot\utils\test_id_counter.json'):
    # Load or initialize persistent counter storage
    if os.path.exists(counter_file):
        try:
            with open(counter_file, 'r') as f:
                counter_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            counter_data = {}
    else:
        counter_data = {}

    start = counter_data.get(date_str, 0)

    # Convert numbers to testIDs
    def number_to_test_id(n):
        if n < 0:
            return 'A'
        result = ''
        while True:
            result = chr(ord('A') + (n % 26)) + result
            n = n // 26 - 1
            if n < 0:
                break
        prefix = 'Z' * (len(result) - 1)
        return prefix + result

    test_ids = [number_to_test_id(i) for i in range(start, start + count)]
    counter_data[date_str] = start + count

    with open(counter_file, 'w') as f:
        json.dump(counter_data, f)

    return test_ids

def update_sequence(sequence_path, wafer, device, electrolyte, site):
    date_str = datetime.now().strftime("%Y%m%d")
    pattern = r'"(\d{8})_[^_]+_[^_]+_[^_]+_[^_]+_[^_]+_(.+?\.DTA)"'

    with open(sequence_path, 'r') as file:
        lines = file.readlines()

    # Count how many lines will be updated
    target_line_indices = [
        i for i, line in enumerate(lines)
        if 'OUTPUT.New' in line and '.DTA' in line.upper()
    ]
    test_ids = get_test_ids(date_str, len(target_line_indices))

    updated_lines = []
    test_id_index = 0

    for i, line in enumerate(lines):
        if i in target_line_indices:
            def replace_filename(match):
                original_filename = match.group(2)
                test_id = test_ids[test_id_index]
                return f'"{date_str}_{wafer}_{device}_{electrolyte}_{site}_{test_id}_{original_filename}"'

            updated_line = re.sub(pattern, replace_filename, line, flags=re.IGNORECASE)
            updated_lines.append(updated_line)
            test_id_index += 1
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
        #print(f"Pixel color: {pixel}")
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
        
        update_sequence(sequence_path, wafer, device, electrolyte, site)
        run_sequence(sequence_path)
        wait_for_green_light()

    print('All channels complete')































    
    
        
    
