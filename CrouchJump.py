import keyboard
import threading
import time
import configparser
import os
import colorama
from colorama import Fore, Style
import ctypes
import win32gui
import tkinter as tk
from tkinter import messagebox

colorama.init()

ctrl_pressed = False
release_delay = 0.85  # Default release delay in seconds
paused = False
pause_hotkey = "enter"  # Default pause/unpause hotkey
duck_key = "left ctrl"  # Default +duck key

def release_ctrl():
    global ctrl_pressed, release_delay
    time.sleep(release_delay)
    if ctrl_pressed:
        keyboard.release(duck_key)
        ctrl_pressed = False

def on_space_press(event):
    global ctrl_pressed, paused, duck_key
    if paused:
        if event.name == 'space' or event.name == duck_key:
            keyboard.release(event.name)
        return

    if event.event_type == keyboard.KEY_DOWN:
        if event.name == 'space':
            if keyboard.is_pressed('w'):
                keyboard.release('w')
            keyboard.press('space')
            keyboard.press(duck_key)
            ctrl_pressed = True
            threading.Thread(target=release_ctrl).start()
    elif event.event_type == keyboard.KEY_UP:
        if event.name == 'space':
            keyboard.release('space')

def toggle_pause():
    global paused, pause_hotkey
    if pause_hotkey == "enter":
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        if window_title.endswith('.exe'):
            if paused:
                if keyboard.is_pressed('space'):
                    keyboard.release('space')
                if keyboard.is_pressed(duck_key):
                    keyboard.release(duck_key)
                paused = False
                print(Fore.YELLOW + Style.BRIGHT + 'Script unpaused.' + Style.RESET_ALL)
            else:
                paused = True
                print(Fore.YELLOW + Style.BRIGHT + 'Script paused.' + Style.RESET_ALL)
    else:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        if window_title.endswith('.exe') or 'Counter-Strike' in window_title or 'Momentum' in window_title:
            paused = not paused
            print(Fore.YELLOW + Style.BRIGHT + 'Script ' + ('paused.' if paused else 'unpaused.') + Style.RESET_ALL)

def release_enter(event):
    if event.name == 'enter':
        keyboard.release('enter')

keyboard.on_press(release_enter)

# Load configuration from file
config = configparser.ConfigParser(comment_prefixes=';', allow_no_value=True)
config_file = 'config.ini'
first_launch = False

if os.path.exists(config_file):
    config.read(config_file)
    if 'Settings' in config:
        if 'release_delay' in config['Settings']:
            release_delay = float(config['Settings']['release_delay'])
        if 'pause_hotkey' in config['Settings']:
            pause_hotkey = config['Settings']['pause_hotkey']
        if 'duck_key' in config['Settings']:
            duck_key = config['Settings']['duck_key']
        if 'first_launch' in config['Settings']:
            first_launch = config.getboolean('Settings', 'first_launch')
else:
    config.add_section('Settings')
    config.set('Settings', 'release_delay', str(release_delay))
    config.set('Settings', 'pause_hotkey', pause_hotkey)
    config.set('Settings', 'duck_key', duck_key)
    config.set('Settings', 'first_launch', 'True')

    with open(config_file, 'w') as configfile:
        config.write(configfile)
    first_launch = True

if first_launch:
    # Display warning message box
    message = "Don't forget to pause/close the script when you aren't playing or else typing is going to be buggy.\n\nMake sure your crouch jump key is bound to +jump only!\n\nYou can now set a custom hotkey in config.ini that will let you pause the script while in-game. I recommend a function key (f1, f2, f3 etc.) or something you don't use while typing."
    messagebox.showwarning("crouchjump.exe", message)
    config.set('Settings', 'first_launch', 'False')
    with open(config_file, 'w') as configfile:
        config.write(configfile)

print(Fore.RED + "Crouch Jump activated. " + Fore.WHITE + Style.BRIGHT + "The script will automatically let go of crouch for you after a specified delay." + Style.RESET_ALL)
print(Fore.WHITE + Style.BRIGHT + "You can change the uncrouch timing in the " + Fore.BLUE + Style.BRIGHT + "config.ini " + Fore.WHITE + Style.BRIGHT + "file. The default value is " + Fore.BLUE + Style.BRIGHT + "0.85" + Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " seconds." + Style.RESET_ALL)
print(Fore.WHITE + Style.BRIGHT + "You can change the " + Fore.BLUE + Style.BRIGHT + "+duck " + Fore.WHITE + Style.BRIGHT +  "key in the " + Fore.BLUE + Style.BRIGHT + "config.ini " + Fore.WHITE + Style.BRIGHT + "file. The default value is " + Fore.BLUE + Style.BRIGHT + "left ctrl." + Style.RESET_ALL)
print(Fore.YELLOW + Style.BRIGHT + f"Press {Fore.GREEN}{Style.BRIGHT}{pause_hotkey.capitalize()}{Fore.YELLOW}{Style.BRIGHT} to toggle pause/unpause." + Style.RESET_ALL)

keyboard.add_hotkey(pause_hotkey, toggle_pause, suppress=True)

while True:
    try:
        keyboard.hook(on_space_press)
        keyboard.wait()
    except KeyboardInterrupt:
        break
    finally:
        keyboard.unhook_all()
