#!/usr/bin/env python3

import os.path
import shutil
import re
import json
from packaging import version

NHL_LED_SUPPORTED_VERSION = "1.6.5"

# Ask user for the directory to the nhl-led-scoreboard path
print('')
print('Please enter the full path to `nhl-led-scoreboard`. Typically, this is')
print('located in `/home/pi/nhl-led-scoreboard`.')
valid_path = False
while not valid_path:
    nhl_path = input('Enter the full path to `nhl-led-scoreboard`: ')
    cwd = os.path.os.getcwd()
    if nhl_path[-1] == '/':
        nhl_path = nhl_path[0:-1]
    if not os.path.isdir(nhl_path):
        print(f"\nERROR: Supplied path does not exist - {nhl_path}")
        continue
    valid_path = True

print(f"INFO: Working path for nhl-led-scoreboard is: {nhl_path}")

# Verify the nhl-led-scoreboard version
# If the version is higher than what we support, prompt user to continue
ver = open(f"{nhl_path}/VERSION").read().rstrip()
if version.parse(ver) > version.parse(NHL_LED_SUPPORTED_VERSION):
    print("The version of 'nhl-led-scoreboard' installed is greater than the version 'stonks' supports.")
    print(f"Installed: {ver}, Supported: {NHL_LED_SUPPORTED_VERSION}")
    yesno = input("Do you wish to continue installation anyway? (y/n): ")
    if yesno.lower()[0] == 'n':
        print("\nAborting stonks install")
        quit()

# Copy 'stonks.py' to 'src/boards/'
print(f"Copying 'stonks.py' to new location... ",end='')
shutil.copyfile('stonks.py',f"{nhl_path}/src/boards/stonks.py")
print("done.")

# Modify the 'src/boards/boards.py' file
print(f"Updating '{nhl_path}/src/boards/boards.py'... ",end='')
with open(f"{nhl_path}/src/boards/boards.py",'r+') as boards:
    text = boards.read()
    if not 'from boards.stonks import Stonks' in text:
        text = re.sub("from time import sleep\n","from time import sleep\nfrom boards.stonks import Stonks\n",text)
        text += "\n\n    def stonks(self, data, matrix, sleepEvent):\n        Stonks(data, matrix, sleepEvent).render()"
        boards.seek(0)
        boards.write(text)
    else:
        print(f"\n * '{nhl_path}/src/boards/boards.py' not modified as it has already been updated")
    boards.close()
print("done.")

# Modify the 'src/data/scoreboard_config.py' file
new_config_data = '''# Stonks
        self.stonks_tickers = json["boards"]["stonks"]["tickers"]
        self.stonks_rotation_rate = json["boards"]["stonks"]["rotation_rate"]
        self.stonks_logo_enabled = json["boards"]["stonks"]["logo_enabled"]
        self.stonks_chart_enabled = json["boards"]["stonks"]["chart_enabled"]

'''
print(f"Updating '{nhl_path}/src/data/scoreboard_config.py'... ",end='')
with open(f"{nhl_path}/src/data/scoreboard_config.py",'r+') as sconfig:
    text = sconfig.read()
    if not '# Stonks' in text:
        text = re.sub("# Fonts\n",new_config_data+"        # Fonts\n",text)
        sconfig.seek(0)
        sconfig.write(text)
    else:
        print(f"\n * '{nhl_path}/src/data/scoreboard_config.py' not modified as it has already been updated")
    sconfig.close()
print("done.")

# Modify the 'config/config.json' file
print(f"Updating '{nhl_path}/config/config.json'... ")
new_config = dict()
new_config["tickers"] = ["DOGE-USD", "TSLA"]
new_config["rotation_rate"] = 6
new_config["chart_enabled"] = True
new_config["logo_enabled"] = False
config = json.load(open(f"{nhl_path}/config/config.json"))
config['boards']['stonks'] = new_config
with open(f"{nhl_path}/config/config.json","w") as json_out:
    json.dump(config,json_out,indent=4)
    json_out.close()
print("done.")

# Modify the 'config/config.schema.json' file. Checks if changes present to prevent duplicates.
print(f"Updating '{nhl_path}/config/config.schema.json'... ")
with open(f"{nhl_path}/config/config.schema.json", "r") as f:
    schema = json.load(f)
    f.close()
with open(f"{cwd}/stonks.config.schema.json", "r") as f:
    stonks_schema = json.load(f)
    f.close()

# Add stonks board settings from config.schema.json to boards properties.
schema["properties"]["boards"]["properties"]["stonks"] = stonks_schema

# Individual changes
change_list = [
    # Adds stonks to boards list and required boards.
    [ schema["definitions"]["boards_list"]["enum"], "boards_list enum" ],
    [ schema["properties"]["boards"]["required"], "required boards" ],

    # Adds stonks to all board states, because doge
    [ schema["properties"]["states"]["properties"]["off_day"]["default"], "off_day default state"],
    [ schema["properties"]["states"]["properties"]["scheduled"]["default"], "scheduled default state" ], 
    [ schema["properties"]["states"]["properties"]["post_game"]["default"], "post_game default state" ], 
]

# Checks if stonks already present.
def stonks_check(change):
    if not "stonks" in change[0]:
        change[0].append("stonks")
        print(f'  "stonks" added to {str(change[1])}.')
    else:
        print(f'  "stonks" already found in {str(change[1])}. Skipping change.')

# Iterate changes.
for change in change_list:
    stonks_check(change)

# Write out modified schema to nhl directory.
with open(f"{nhl_path}/config/config.schema.json", "w") as outfile:
    json.dump(schema, outfile, indent=4)
    outfile.close()
print("... done.")

