import os
import sys

if os.environ['PATH'].lower().find('python') != -1:
    print("Python is in PATH. Script will be executed correctly.")
    in_path = True
else:
    print("Python is not in PATH. Pls specify the PATH of python: ")
    in_path = False
    py_path = input()
    try:
        os.system(f"{py_path} -V")
    except:
        print("Incorrect PATH.")
        exit()

print("The libs necessary to run bot.py will now be downloaded...")

if in_path == True:
    if sys.platform == "win32":
        py_path = "python"
    else:
        py_path = "python3"
os.system(f"{py_path} -m pip install --upgrade pip") # Upgrade before installing anything
#os.system(f"{py_path} -m pip install discord.py") # Main discord lib
#os.system(f"{py_path} -m pip install -U git+https://github.com/Rapptz/discord.py") # Updating main discord lib
#os.system(f"{py_path} -m pip install -U discord-py-slash-command") # Salsh commands, buttons and dropdown
os.system(f"{py_path} -m pip install python-dotenv") # To use .env file to store your token
os.system(f"{py_path} -m pip install PyNaCl") # Used for bot voice features
#os.system(f"{py_path} -m pip install youtube_dl") # Play music from youtube
#os.system(f"{py_path} -m pip install youtube_search") # Search music from youtube
os.system(f"{py_path} -m pip install asyncio") # Support qsynchronous functions
os.system(f"{py_path} -m pip install requests") # Download content from http/https pages (used in scan.py)
os.system(f"{py_path} -m pip install urllib3") # Download content from http/https pages (used in scan.py)
os.system(f"{py_path} -m pip install numpy") # More complete gestion of tabs (used in p4.py)
os.system(f"{py_path} -m pip install Pillow") # Creating and editing images (used in p4.py)
os.system(f"{py_path} -m pip install lxml") # Create and Parse xml files (used in music.py for playlists)

print("Installation finished.")
