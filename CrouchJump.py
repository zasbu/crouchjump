import keyboard
import threading
import time
import configparser
import os
import colorama
from colorama import Fore, Style
import ctypes
import win32gui

colorama.init()

ctrl_pressed = False
release_delay = 0.85  # Default release delay in seconds
paused = False

def release_ctrl():
    global ctrl_pressed, release_delay
    time.sleep(release_delay)
    if ctrl_pressed:
        keyboard.release('left ctrl')
        ctrl_pressed = False

def on_space_press(event):
    global ctrl_pressed, paused
    if paused:
        return

    if event.event_type == keyboard.KEY_DOWN:
        if event.name == 'space':
            keyboard.press('space')
            keyboard.press('left ctrl')
            ctrl_pressed = True
            threading.Thread(target=release_ctrl).start()
    elif event.event_type == keyboard.KEY_UP:
        if event.name == 'space':
            keyboard.release('space')

def toggle_pause():
    global paused
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    window_title = win32gui.GetWindowText(hwnd)
    if window_title.endswith('.exe'):
        paused = not paused
        print(Fore.YELLOW + Style.BRIGHT + 'Script ' + ('paused.' if paused else 'unpaused.') + Style.RESET_ALL)

# Load configuration from file
config = configparser.ConfigParser(comment_prefixes=';', allow_no_value=True)
config_file = 'config.ini'

if os.path.exists(config_file):
    config.read(config_file)
    if 'Settings' in config:
        if 'release_delay' in config['Settings']:
            release_delay = float(config['Settings']['release_delay'])
else:
    config.add_section('Settings')
    config.set('Settings', 'release_delay', str(release_delay))

    with open(config_file, 'w') as configfile:
        config.write(configfile)

print(Fore.RED + "Crouch Jump activated. " + Fore.WHITE + Style.BRIGHT + "The script will automatically let go of crouch for you after a specified delay." + Style.RESET_ALL)
print(Fore.WHITE + Style.BRIGHT + "You can change the uncrouch timing in the " + Fore.BLUE + Style.BRIGHT + "config.ini " + Fore.WHITE + Style.BRIGHT + "file. The default value is " + Fore.BLUE + Style.BRIGHT + "0.85" + Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " seconds." + Style.RESET_ALL)
print(Fore.YELLOW + Style.BRIGHT + "Press " + Fore.GREEN + Style.BRIGHT + "Enter" + Fore.YELLOW + Style.BRIGHT + " to toggle pause/unpause." + Style.RESET_ALL)

keyboard.add_hotkey('enter', toggle_pause)

while True:
    try:
        keyboard.hook(on_space_press)
        keyboard.wait()
    except KeyboardInterrupt:
        break
    finally:
        keyboard.unhook_all()
