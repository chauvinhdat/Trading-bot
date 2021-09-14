from requests.api import request

import os
import time
import requests
import json
import csv
from datetime import date, datetime

url = ''
month_url = ''
r = None
data = None
month_r = None
month_data = None

today = datetime.now()
today = today.strftime("%Y-%m-%d %H:%M:%S")

absolute_path = os.path.dirname(os.path.abspath(__file__))
# Or: file_path = os.path.join(absolute_path, 'folder', 'my_file.py')
balance_file_path = absolute_path + '\\balance.json'

def set_url(functionInterval,timeInterval, symbol):
    try:
        global url
        t_url = "https://www.alphavantage.co/query?function=" + str(functionInterval) + "&symbol=" + str(symbol) + "&interval=" + str(timeInterval) + "&apikey=SU6OH7HAUS5X1OSU"
        if(t_url != url):
            url = t_url
        global month_url
        t_month_url = "https://www.alphavantage.co/query?function=" + str(functionInterval) + "&symbol=" + str(symbol) + "&interval=" + str(timeInterval) + "&outputsize=full&apikey=SU6OH7HAUS5X1OSU"    
        if(t_month_url != month_url):
            month_url = t_month_url
        global r
        r = requests.get(url)
        global data
        data = r.json()
        global month_r
        month_r = requests.get(month_url)
        global month_data
        month_data = month_r.json()
        print(month_data)
    except:
        quit()

# print(data['Time Series (5min)']['2021-08-24 19:55:00'])
# retrive stock info from timestamp (today, every 5 minutes)
log = []
timestamp_storage = []

series = ""
#value are 5 minutes behind to yahoo finance (NOTE)
def set_timestamp():
    i = 0
    for timestamp in data[series]:
        print(timestamp+": ")
        print(data[series][timestamp]['4. close'])
        timestamp_storage.append(timestamp)
        i += 1

def reset_timestamp():
    if len(timestamp_storage) == 0:
        return 0
    for i in range(len(timestamp_storage)):
        timestamp_storage.pop(0)

def store_timestamp(database, onlydate):
    arr = []
    if(onlydate == False):    
        for timestamp in database[series]:
            arr.append(timestamp)
    else:
        for timestamp in database[series]:
            arr.append(timestamp[:-9])
    return arr

def get_price(date_time):
    return float(month_data[series][date_time]['4. close'][-10:])

def saveLog(toSave):
    log.append(toSave)
    
purchased_stocks = []
def buy(date_time):
    #most recent
    price = get_price(date_time)
    balance = get_balance()
    print(balance)
    balance = updateBalance(balance, price, False)
    buy_price = ""
    buy_price = "Date&Time: " + date_time + " | Price: " + str(get_price(date_time))
    purchased_stocks.append(price)
    saveLog("Bought: " + buy_price)
    print("bought: "+buy_price, balance)

sold_stocks = []
def sell(date_time):
    if len(purchased_stocks) == 0:
        print(date_time + ": Got no stonk left son")
        return 0
    price = get_price(date_time)
    balance = get_balance()
    print(balance)
    balance = updateBalance(balance, price, True)
    sold_price = ""
    sold_price = "Date&Time: " + date_time + " | Price: " + str(get_price(date_time))
    sold_stocks.append(sold_price)
    if len(purchased_stocks) != 0:
        save_grid(purchased_stocks[0], price)
        saveLog("Sold: " + sold_price)
        purchased_stocks.pop(0)
    print("sold: "+sold_price, balance)

grid_stocks = []
def save_grid(buy_price, sell_price):
    store = []
    store.append(buy_price)
    store.append(sell_price)
    grid_stocks.append(store)

def cost_check(date_time):
    balance = get_balance()
    price = get_price(date_time)
    if (float(balance['USD']) - price) >= 0:
        return True
    else:
        return False

def get_balance():
    with open(balance_file_path) as f:
        try:
            return json.load(f)
        except:
            return {'USD': '1000'}

def updateBalance(amount, price, sell):
    balance = get_balance()
    if sell:
        balance['USD'] = str((float(amount['USD'])) + price)
    else:
        balance['USD'] = str((float(amount['USD'])) - price)
    with open(balance_file_path, 'w') as f:
        json.dump(balance,  f, indent=2)
    return balance

def updateBalance_manual(amount):
    balance = get_balance()
    balance['USD'] = str(amount)
    with open(balance_file_path, 'w') as f:
        json.dump(balance,  f, indent=2)

def convert_date(today_year, today_month, today_day, hour):
    if(today_month>=10):
        d = (str(today_year)+"-"+str(today_month)+"-"+str(today_day)+" "+hour)
    else:
        d = (str(today_year)+"-0"+str(today_month)+"-"+str(today_day)+" "+hour)
    return d

def data_check(date_time, d):
    for n in d:
        if(n == date_time):
            return True
    return False

def avg_trend(hour, m_data):
    t = datetime.now()
    t = t.strftime("%Y")
    today_year = int(t)
    t = datetime.now()
    t = t.strftime("%m")
    today_month = int(t)
    t = datetime.now()
    t = t.strftime("%d")
    today_day = int(t)
    check = False
    arr = []
    for i in range(28):
        if today_day >= 1:
            today_day -= 1
        else:
            today_month -= 1
            #even month
            if today_month == 7 or (today_month % 2) == 0:
                today_day = 31
            else:
                today_day = 30
        dt = convert_date(today_year, today_month, today_day, hour)
        if data_check(dt, m_data) == True:
            arr.append(get_price(dt))
    avg = 0
    for i in arr:
        avg += i
    return float(avg/28)

def calculate_trend(average):
    prev = 0
    trend = []
    avg = 0
    time_m = store_timestamp(month_data, False)
    for time in reversed(timestamp_storage):
        date = time[:-9]
        hour = time[-8:]
        #print(date, hour)
        if average == True:    
            curr_value = float(avg_trend(hour, time_m))
        if average == False:
            curr_value = get_price(time)
        if prev == 0:
            prev = curr_value
        #uptrend
        elif (curr_value/prev) > 1:
            prev = curr_value
            trend.append('up')
        #downtrend
        elif (curr_value/prev) < 1:
            prev = curr_value
            trend.append('down')
        #hueh
        else:
            trend.append('NA')
            prev = curr_value
    #time_m[-8:] = hour
    #print(today_day, today_month)
    #print(trend)
    return trend

def check_oppertunity(trend, current_time, c_price, prev_price, count):
    if prev_price == 0 or len(trend) == 0:
        prev_price = c_price
        return prev_price
    #buy high or sell high
    elif ((trend[0] == 'up') and ((c_price/prev_price) >= 1)):
        sell(current_time)
        #if len(count) == 0:
        #    count.append(0)
        #elif len(count) > 0:     
        #    count.append(count[0] + 1)
        #if len(count) > 1:    
        #    count.pop(0)
    #elif ((trend[0] == 'down') and ((c_price/prev_price) < 1) and (cost_check(current_time) == True)):
    #    buy(current_time)
    elif ((trend[0] == 'down') and ((c_price/prev_price) < 1) and (cost_check(current_time) == True)):
        buy(current_time)
        #count.append(0)
        #count.pop(0)
    #print(str(c_price) + " | " + str(prev_price) + " | " +  str(c_price/prev_price) + " | " + trend[0])
    prev_price = c_price
    trend.pop(0)
    return prev_price

def resetLog():
    if len(log) == 0:
        return 0
    for i in range(len(log)):
        log.pop(0)
    return 0

def resetgrid():
    if len(grid_stocks) == 0:
        return 0
    for i in range(len(grid_stocks)):
        grid_stocks.pop(0)

def reset_purchase_stocks():
    if len(purchased_stocks) == 0:
        return 0
    for i in range(len(purchased_stocks)):
        purchased_stocks.pop(0)
    return 0

def reset_sold_stocks():
    if len(sold_stocks) == 0:
        return 0
    for i in range(len(sold_stocks)):
        sold_stocks.pop(0)
    return 0

def begin(interval):
    global series
    series = 'Time Series (' + str(interval)+ ')'
    set_timestamp()
    avg_trending = calculate_trend(True)
    p_price = 0
    c = []
    print(avg_trending)
    #print(purchased_stocks)
    for time in reversed(timestamp_storage):
        p_price = check_oppertunity(avg_trending, time, get_price(time), p_price, c)
    print("owned stocks left: ")
    for stonks in purchased_stocks:
        print(stonks)
    bal = get_balance()
    round = "{:.3f}".format(((len(purchased_stocks))*p_price + float(bal['USD'])))
    tt = ("Total balance: " + str(round))
    #print(tt)
    updateBalance_manual(0)
    reset_purchase_stocks()
    reset_sold_stocks()
    #print(purchased_stocks)
    #print(series)
    return tt

#main
price_daily = []
def set_pricedaily():
    for time in timestamp_storage:
        price_daily.append(get_price(time))

def reset_pricedaily():
    if len(price_daily) == 0:
        return 0
    for i in range(len(price_daily)):
        price_daily.pop(0)

def getLog():
    return log

def get_grid():
    return grid_stocks

def get_grid_count():
    counter=[]
    for count in range(len(grid_stocks)):
        counter.append(count) 
    return counter

from flask import Blueprint, render_template, request, flash, jsonify


bot_trading = Blueprint('bot_trading', __name__)
  

@bot_trading.route('/', methods=['POST', 'GET', 'RESET'])
def bruh():
    text = ""
    if request.method == 'POST':
        text = request.form["balance"]
        symbol = request.form["symbol"]
        interval = request.form["Interval"]
        try:
            float(symbol)
            #if symbol contain number then return default
            return render_template("index.html")
        except:
            if ((text == None or text == "") or (symbol == None or symbol == "") or (interval == None or interval == "empty")):
                return render_template("index.html")
        if (len(getLog()) > 1) or (len(timestamp_storage) > 1) or (len(price_daily) > 1) or (len(get_grid()) > 1):
            reset_pricedaily()
            reset_timestamp()
            resetLog()
            resetgrid()
        try:
            float(text)
        except:
            resetLog()
            resetgrid()
            reset_timestamp()
            reset_pricedaily()
            return render_template("index.html")  
        set_url("TIME_SERIES_INTRADAY", interval, symbol)  
        updateBalance_manual(float(text))
        total_balance = begin(interval)
        set_pricedaily()
        labels = timestamp_storage
        values = price_daily
        grid_v = get_grid()
        grid_l = get_grid_count()
        loggy = getLog()
        balance = "Budget: "+ str(text)
        stonk = "Stonk: "+ str(symbol)
        return render_template("index.html", labels=labels, values=values, grid_v=grid_v,grid_l=grid_l,total_balance=total_balance,loggy=loggy, balance=balance, stonk=stonk) 
    return render_template("index.html")

@bot_trading.route('/')
def home():
    return render_template("index.html")

