from PIL import ImageFont
from utils import get_file
#import re
import debug
from time import sleep
import yfinance as yf
#import json

WHITE = (255,255,255)
GREEN = (  0,255,  0)
RED   = (255,  0,  0)

LED_WIDTH = 64
LED_HEIGHT = 32

FULL_DAY_TICKS = 150   # not really true, but maybe
CHART_Y = 14           # pixel row for the top of the chart

class Stonks:
    def __init__(self, data, matrix, sleepEvent):
        self.data = data
        self.matrix = matrix
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        self.font = ImageFont.truetype(get_file("assets/fonts/BMmini.TTF"), 8)
        self.render()

    def render(self):
        # debug.info("displaying sToNkS!")
        for ticker in self.data.config.stonks_tickers:
            # debug.info("sToNkS: {}".format(ticker))
            
            if self.sleepEvent.is_set():
                self.matrix.clear()
                return

            try:
                tickerData = yf.Ticker(ticker).info
            except:
                debug.error(f"Unable to fetch data for {ticker}")
                continue

            last_price = tickerData["regularMarketPrice"]
            prev_close = tickerData["regularMarketPreviousClose"]
            percent_chg = 100.0*((last_price/prev_close)-1.0)

            self.matrix.clear()
            
            # get intraday chart data, if enabled
            if self.data.config.stonks_chart_enabled:

                try:
                    cd = yf.download(tickers=ticker,interval="1m",period="1d",progress=False)
                except:
                    debug.error(f"Unable to fetch intraday tick data for {ticker}")
                    continue
                
                prices = cd["Close"].tolist()
                minp, maxp = min(prices), max(prices)
                lenp = len(prices)
                x_inc = lenp / LED_WIDTH # compute the X Axis increment
                # Prev Close Y Axis value
                if prev_close < minp:
                    prevcl_Y = LED_HEIGHT-1
                elif prev_close > maxp:
                    prevcl_Y = CHART_Y
                elif maxp == minp:
                    prevcl_Y = CHART_Y
                else:
                    prevcl_Y = int(CHART_Y + (maxp-prev_close)*((LED_HEIGHT-CHART_Y)/(maxp-minp)))
                # debug.info(f"{ticker} prev close {prevcl_Y}")
                for x in range(LED_WIDTH):
                    p = prices[int(x * x_inc)] # Get the subsampled price, based on our X Axis position
                    if maxp == minp:
                        y = CHART_Y
                    else:
                        y = int(CHART_Y + (maxp-p)*((LED_HEIGHT-CHART_Y)/(maxp-minp))) # compute Y value
                    color = GREEN if p > prev_close else RED
                    step = -1 if y > prevcl_Y else 1 # compute up/down direction for chart area fill
                    for ys in range(y,prevcl_Y+step,step): # draw area fill
                        dim_y = y/ys if step == 1 else ys/y # dimmer color near prev close
                        self.matrix.draw_pixel((x,ys-1),tuple([int(i * 0.25 * dim_y) for i in color]))
                    self.matrix.draw_pixel((x,y-1),color) # finally, draw the price values

            # Compute the up/down color        
            color = WHITE
            if percent_chg > 0:
                color = GREEN
            elif percent_chg < 0:
                color = RED
            
            # Render the first line: Ticker / $Chg
            ticker = ticker.split('-')[0][0:5] # trim the ticker to the first 5 characters, excluding dashes
            self.matrix.draw_text([0,0],ticker,self.font)
            self.matrix.draw_text(["100%",0],"{:.2f}".format(last_price-prev_close),self.font,fill=color,align="right")

            # Render the second line: Last Price / %Chg
            fstr = "{:.2f}"       # limit precision for Last Price
            if last_price < 1:
                fstr = "{:.5f}"   # for cheap stocks, increase precision
            self.matrix.draw_text([0,8],fstr.format(last_price),self.font)
            self.matrix.draw_text(["100%",8],"{:.2f}".format(percent_chg)+"%",self.font,fill=color,align="right")

            self.matrix.render()
            self.sleepEvent.wait(self.data.config.stonks_rotation_rate)
        self.matrix.clear()
        # debug.info("done wit sToNkS!")
