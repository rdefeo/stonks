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
            
            tickerData = yf.Ticker(ticker).info
            last_price = tickerData["regularMarketPrice"]
            prev_close = tickerData["regularMarketPreviousClose"]
            percent_chg = 100.0*((last_price/prev_close)-1.0)

            self.matrix.clear()
            
            # get intraday chart data, if enabled
            if self.data.config.stonks_chart_enabled:
                CHART_Y = 14 # pixel row for the top of the chart
                cd = yf.download(tickers=ticker,interval="1m",period="1d",progress=False)
                prices = cd["Close"].tolist()
                minp, maxp = min(prices), max(prices)
                x_inc = len(prices) / LED_WIDTH # compute the X Axis increment
                prevcl_Y = CHART_Y + (maxp-prev_close)*((LED_HEIGHT-CHART_Y)/(maxp-minp)) # Prev Close Y Axis value
                for x in range(LED_WIDTH):
                    p = prices[int(x * x_inc)] # Get the subsampled price, based on our X Axis position
                    y = CHART_Y + (maxp-p)*((LED_HEIGHT-CHART_Y)/(maxp-minp)) # compute Y value
                    color = GREEN if p > prev_close else RED
                    step = -1 if y > prevcl_Y else 1 # compute up/down direction for chart area fill
                    for ys in range(int(y),int(prevcl_Y),step): # draw area fill
                        dim_y = y/ys if step == 1 else ys/y # dimmer color near prev close
                        self.matrix.draw_pixel((x,ys),tuple([int(i * 0.25 * dim_y) for i in color]))
                    self.matrix.draw_pixel((x,y),color) # finally, draw the price values

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