#!/usr/bin/env python3

import os.path
import shutil
import re
import json

# Ask user for the directory to the nhl-led-scoreboard path
print('')
nhl_path = input('Enter the full path to `nhl-led-scoreboard`: ')

# Verify the path
if nhl_path[-1] == '/':
    nhl_path = nhl_path[0:-1]
if not os.path.isdir(nhl_path):
    print(f"\nERROR: Supplied path does not exist - {nhl_path}")
    quit()
print(f"INFO: Working path for nhl-led-scoreboard is: {nhl_path}")

# Copy 'stonks.py' to 'src/boards/'
print(f"Copying 'stonks.py' to new location... ",end='')
shutil.copyfile('stonks.py',f"{nhl_path}/src/boards/stonks.py")
print("done.")

# Modify the 'src/boards/boards.py' file
print(f"Updating '{nhl_path}/src/boards/boards.py'... ",end='')
with open(f"{nhl_path}/src/boards/boards.py",'r+') as boards:
    text = boards.read()
    text = re.sub("from time import sleep\n","from time import sleep\nfrom boards.stonks import Stonks\n",text)
    text += "\n\n    def stonks(self, data, matrix, sleepEvent):\n        Stonks(data, matrix, sleepEvent)"
    boards.seek(0)
    boards.write(text)
    boards.close()
print("done.")

# Modify the 'config/config.schema.json' file
print(f"Updating '{nhl_path}/config/config.schema.json'... ",end='')
schema = json.load(open(f"{nhl_path}/config/config.schema.json"))
schema['definitions']['boards_list']['enum'].append('stonks')
with open(f"{nhl_path}/config/config.schema.json","w") as json_out:
    json.dump(schema,json_out,indent=4)
    json_out.close()
print("done.")

# Modify the 'src/data/scoreboard_config.py' file
new_config_data = '''        # Stonks
        self.stonks_tickers = json["boards"]["stonks"]["tickers"]
        self.stonks_rotation_rate = json["boards"]["stonks"]["rotation_rate"]
        self.stonks_logo_enabled = json["boards"]["stonks"]["logo_enabled"]
        self.stonks_chart_enabled = json["boards"]["stonks"]["chart_enabled"]

'''
print(f"Updating '{nhl_path}/src/data/scoreboard_config.py'... ",end='')
with open(f"{nhl_path}/src/data/scoreboard_config.py",'r+') as sconfig:
    text = sconfig.read()
    text = re.sub("# Fonts\n",new_config_data+"        # Fonts\n",text)
    sconfig.seek(0)
    sconfig.write(text)
    sconfig.close()
print("done.")

# Modify the 'config/config.json' file
print(f"Updating '{nhl_path}/config/config.json'... ",end='')
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

