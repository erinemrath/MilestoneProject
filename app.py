from flask import Flask,jsonify, render_template, request, redirect
import pandas as pd
import bokeh
import requests
import os
import datetime
from pandas import DataFrame, Series
from bokeh.plotting import figure
from bokeh.embed import components

app = Flask(__name__)

####################
# Helper Functions
# Load API key for accessing data

def load_api_key(key_file, key_name):
  with open(key_file) as f_:
    info = {}
    for line in f_:
      line = line.split()
      if len(line) == 3:
        info[line[0]] = line[2]
  f_.close()
  api_key = info[key_name]
  return api_key

# Get Quandl Data
def get_quandl(ticker, api_key):
  ticker = ticker.upper()
  now = datetime.date(2018, 3, 27)
  start = now - datetime.timedelta(days = 31)
  start = "&start_date=" + start.strftime("%Y-%m-%d")
  now = "&end_date=" + now.strftime("%Y-%m-%d")
  data_url = 'https://www.quandl.com/api/v3/datasets/WIKI/' + ticker + '.json?api_key=' + api_key + now + start
  req = requests.get(data_url)
  if req.status_code > 400:
    print "Stock ticker is invalid"
    df = None
    name = None
  else:
    # find company name
    company_name = req.json()['dataset']['name']
    company_name = company_name.split('(')[0]
    # get the data
    header = (req.json())['dataset']['column_names']
    data = (req.json())['dataset']['data']
    stockdata = pd.DataFrame(data, columns=header)
    stockdata = stockdata.set_index(pd.DatetimeIndex(stockdata['Date']))
  return stockdata, company_name

# Show a figure
def show_figure(df, price, ticker):
  print "price: ", price, type(price)
  p = figure(x_axis_type="datetime", width=800, height=600)
  if type(price) == list:
    for p in price:
      p.line(df.index, df[price[p]], legend = p, line_width = 3)
  else:
    p.line(df.index, df[price], legend = price, line_width = 3)
  p.grid.grid_line_alpha=0.3
  p.xaxis.axis_label = 'Date'
  p.yaxis.axis_label = 'Price'
  script, div = components(p)
  return script, div

# App functions

#to hold variables
app.vars = {}
#name of key_file and key  with quandl api_key
key_file = 'API_KEYS'
key_name = 'quandl'
app.vars['api_key'] = load_api_key(key_file, key_name)

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index', methods=['GET', 'POST'])
def index():
  return render_template('index.html')

@app.route('/plot', methods = ['POST'])
def plot_():
  ticker = request.form['ticker_text']
  prices = request.form['price_check']
  app.vars['ticker'] = ticker.upper()
  app.vars['prices'] = prices
  df, name = get_quandl(app.vars['ticker'], app.vars['api_key'])
  if type(df) != DataFrame:
    message = "Receied an invalid ticker, try again."
    return render_template('index.html', message=message)
  else:
    script, div = show_figure(df, app.vars['prices'], app.vars['ticker'])
    return render_template("plot.html", script=script, div=div, ticker=name)

if __name__ == '__main__':
  port = int(os.environ.get("PORT", 5000))
  app.run(host = '0.0.0.0', port = port)

## @app.route('/about')
## def about():
##  return render_template('about.html')

if __name__ == '__main__':
  app.run(port=33507)
