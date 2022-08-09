# stonks
This is a stocks board for the [nhl-led-scoreboard](https://github.com/riffnshred/nhl-led-scoreboard) project. It will fetch and display single day stock price information for a list of tickers. It will display the single day dollar change and percent change, and an intraday price chart. The display assumes a 64x32 LED matrix. See Configuration for details.

<img src="images/DOGE.jpg" width=300></img>
<img src="images/DIS.jpg" width=300></img><br/>
<img src="images/TSLA.jpg" width=300></img>

## Installing
First, you will need to clone the repository:
```
git clone https://github.com/rdefeo/stonks.git
```

Now that you have the code, there are two ways to complete the install of the stonks board for nhl-led-scoreboard: running the install script or modifying the files manually. The install script will install the `yfinance` python package for you.

### Using the install.sh script
To run the `install.sh` script, you will need to do the following:
```
cd stonks
chmod +x nhl-led-scoreboard/install.sh
./nhl-led-scoreboard/install.sh
```
You will be prompted to enter the full path to where your `nhl-led-scoreboard` app is installed. This may typically be `/home/pi/nhl-led-scoreboard`.

If you didn't see any errors, that's it! Now, just add `"stonks"` to one of your board states in your `config/config.json` to see your stock charts. The default installation will seed the stonks charts with Doge Coin and Tesla. Update the `config.json` to suit your investing needs.

Note: If the `nhl-led-scoreboard` source changes significantly, the installation script may fail. If so, try following the manual steps below.

### Manual installation
To use this new board, you will need to make some edits to 3 files within the [nhl-led-scoreboard](https://github.com/riffnshred/nhl-led-scoreboard) source.

1. Copy the `stonks/nhl-led-scoreboard/stonks.py` file into the `nhl-led-scoreboard/src/boards` directory
2. Add the following two edits to `nhl-led-scoreboard/src/boards.py`:

First, add
```
from boards.stonks import Stonks
```
to the top of the file, near the other `from` statements.

Then, add the following lines at the bottom of the file:
```
    def stonks(self, data, matrix, sleepEvent):
        Stonks(data, matrix, sleepEvent).render()
```
Ensure you have the leading spacing correct, because python.

3. Update `nhl-led-scoreboard/config/config.schema.json` so that it will allow `stonks` as a valid board. Simply add `"stonks"` to the json blob `"definitions" \ "boards_list" \ "enum"`. This is near the top of the file, roughly between lines 18 and 30.

4. Add the following 5 lines to `nhl-led-scoreboard/src/data/scoreboard_config.py`:
```
        # Stonks
        self.stonks_tickers = json["boards"]["stonks"]["tickers"]
        self.stonks_rotation_rate = json["boards"]["stonks"]["rotation_rate"]
        self.stonks_logo_enabled = json["boards"]["stonks"]["logo_enabled"]
        self.stonks_chart_enabled = json["boards"]["stonks"]["chart_enabled"]
```
These lines ensure that the configuration data for the `stonks` board is read and made available to the code. I added them around line 140, just after the config section for "Clock".

5. Lastly, add `"stonks"` to one or more of the board `"states"` so that it will appear in your board rotation.

## Configuration
Within the `boards` section of the `config.json` file, you will need a section for `stonks`:
```
        "stonks": {
            "tickers": [
                "DOGE-USD","MMM","TSLA", "BTC-USD", "AAPL", "AMD", "DIS"
            ],
            "rotation_rate": 6,
            "chart_enabled": true,
            "logo_enabled": false
        },
```
When you add the `"stonks"` section to the config file, make sure you have that last comma!

Now you can add the `stonks` board to any of the game states in your config!

### tickers
A list of stock symbols, using the Yahoo Finance symbology. Basically, look up the stocks you want to use on Yahoo Finance and then cut and paste the tickers here.

### rotation_rate
How long, in seconds, each stock stays on the display before switching to the next stock. The total display time for the stocks will be the number of stocks in `tickers` multiplied by the `rotation_rate`

### chart_enabled
A boolean value that determines whether a chart will be displayed. If this is `false`, then the data fetch for chart data will not occur.

### logo_enabled (Not Implemented)
A boolean value that determines whether to display the ticker (i.e. company) logo.

### Other Configuration Options
The display assumes you are using a 64x32 LED matrix. You can tweak this (untested!) by adjusting the `LED_WIDTH` and `LED_HEIGHT` values in the source file. 

## Requirements
The [nhl-led-scoreboard](https://github.com/riffnshred/nhl-led-scoreboard) project has been synced to your pi.

The [yfinance](https://github.com/ranaroussi/yfinance) python package must be installed. This can be achieved by running `pip3 install yfinance`. Since `yfinance` depends on 
`numpy` and `pandas`, you may need to ensure they are up to date as well. This can be achieved by running `pip3 install yfinance --upgrade`. You may need to run this command with `sudo` if it does not work.

Check out the [yfinance](https://github.com/ranaroussi/yfinance) for more information on installing, etc.
