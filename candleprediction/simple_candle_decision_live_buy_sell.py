import json
import requests
from pprint import pprint
import time
from time import gmtime, strftime
from quadriga import QuadrigaClient
from exchange import Exchange

# simple function to see if there is a direct match with 1D array you are looking for
def is_slice_in_list(s,l):
    len_s = len(s) #so we don't recompute length of s on every iteration
    return any(s == l[i:len_s+i] for i in range(len(l) - len_s+1))

#variables for setting up base time intervals for polling the exchange

query_every_sec = 60 #how often exchange is polled for data in seconds
max_arr_len = 5 #number of queries that exist in the array
candle_time = 0 #total time before a decision block occurs
decision_time = 0 #can use this to change the decision time from every time a candle is created to every time 3 candles are created
bids = [] 
asks = []
spreads = []
bidCandles = [0,0,0] #change this if you change the number of 5 minute intervals to be included in your matching
spreadCandles = [0,0,0]
last_buy = False

debug = True

exc_file_path = 'exchanges.json'
exc = json.load(open(exc_file_path))
coin_list = exc['coins']
e = 'quadriga'
exchange = Exchange(e, exc[e]['can_buy'], exc[e]['can_sell'], exc[e]['account'], debug)

#enter your own quadriga ethereum address here
eth_quadriga_address = '' 

coin = 'ether'
amount = 0.0

#TESTING CODE#
#Comment all below out if you do not want printed in your console#
print('Initializing Test Values')
currentEther = exchange.getBalance('ether')[0]
print(currentEther)

currentCAD = exchange.getBalance('cad')[0]
print(currentCAD)

currentCAD = exchange.getBalance('cad')[0]
bidEther, askEther = exchange.getLatestPrice('ether')
# if bidEther == -1 or askEther == -1:
#     continue
print(currentCAD, bidEther)  
coinToBuy = float(currentCAD) / float(bidEther)
coinToBuyRound = round(coinToBuy, 5)
print(currentCAD, bidEther, coinToBuy)

currentEther = exchange.getBalance('ether')[0]
currentEtherFloat = float(currentEther)
print(currentEther)

print('lastest script - v0.1205')
###############

# print("raw data every 60 seconds")
# print("w,h,m,bid,ask,spread,volume")

#Below is main continuous loop that polls quadrigacx on your defined query interval
#This script is meant to be run in your console for testing purposes; have tested running for >8 hours without error

while True:
    time.sleep(query_every_sec)
    
    candle_time += query_every_sec
    
    try:
        bid, ask = exchange.getLatestPrice('ether')
        volume = exchange.getLatestVolume('ether')
    except Exception as e:
        print(str(e))

    #data structure for arrays to save, bid, ask, spread and time values
    if bid == -1 or ask == -1:
        continue
    bids.append(bid)
    asks.append(ask)

    spread = ask - bid
    spreads.append(spread)

    if len(bids) > max_arr_len:
        bids.pop(0)
    if len(asks) > max_arr_len:
        asks.pop(0)
    if len(spreads) > max_arr_len:
        spreads.pop(0)

    
    currentTimeHour = strftime("%H", gmtime())
    currentTimeMin = strftime("%M", gmtime())
    currentTimeDayWeek = strftime("%w", gmtime()) #0-6 sunday is 0
    
    #raw data
    # print(currentTimeDayWeek,",",currentTimeHour,",",currentTimeMin,",",bid,",",ask,",",spread,",",volume)

    #save the raw data to a text file
    with open("ethcad", "a") as f:
        currentData = str(currentTimeDayWeek) + "," + str(currentTimeHour) + "," + str(currentTimeMin) + "," + str(bid) + "," + str(ask) + "," + str(spread) + "," + str(volume) + "\n"
        try:
            f.write(currentData)
        except Exception as e:
            print(str(e))

    if len(bids) < max_arr_len:
        continue
    
    #time for 1st decision to be made for a candle value
    if (candle_time < 300):
        continue
    
    decision_time += candle_time
    
    candle_time = 0
    
    firstMinVal = float(bids[0])
    lastMinVal = float(bids[4])

    firstSpreadVal = float(spreads[0])
    lastSpreadVal = float(spreads[4])

    bidDelta = lastMinVal - firstMinVal
    print('Latest difference in currency value CAD')
    print(bidDelta)

    spreadDelta = lastSpreadVal - firstSpreadVal
    print('Latest spread difference in currency value CAD')
    print(spreadDelta)

    #save prices array to database
    #reset prices array after delta

    if bidDelta > 0.5: 
        bidCandles.append(1)
    elif bidDelta < -0.5:
        bidCandles.append(-1)
    else:
        bidCandles.append(0)
        
    bidCandles.pop(0)
    print("bid candles: ", bidCandles)

    if spreadDelta > 0.5: 
        spreadCandles.append(1)
    elif spreadDelta < -0.5:
        spreadCandles.append(-1)
    else:
        spreadCandles.append(0)
        
    spreadCandles.pop(0)
    print("spread candles: ", spreadCandles)
    
    if last_buy == True:
        print('Decision: SELL transaction')
        print(bids)
        print(asks)
        last_buy = False
        currentEther = exchange.getBalance('ether')[0]
        currentEtherFloat = float(currentEther)
        print(currentEther)
        print(asks[4])
        # exchange.sell(coin, currentEtherFloat)
        exchange.sell_limit(coin, currentEtherFloat, asks[4])
    

    # create decision check here if you want decision window to be greater than candle interval check here
    # if (decision_time < 900):
    #     continue
    
    # decision_time = 0

    # BUY DECISION
    # hour candles:  [0, 0, -1]
    # spread candles:  [0, 0, 1]
    # +3, +10, 0, +10, 

    BUY1 = [0,0,-1]
    SPREADBUY = [0,0,1]
    decision_1 = is_slice_in_list(BUY1,bidCandles)
    decision_spread_1 = is_slice_in_list(SPREADBUY,spreadCandles)
    #print('Buy 1 decision: ' + str(decision_1))
    if decision_1 == True and decision_spread_1 == True:
        #print / save data to database
        print('Decision: BUY [0,0,-1]') 
        print(bids)
        print(asks)
        print(spreads)

        # # COMMENT/UNCOMMENT BELOW 
        # # LIVE TRADING
        # currentCAD = exchange.getBalance('cad')[0]
        # bidEther, askEther = exchange.getLatestPrice('ether')
        # #if bidEther == -1 or askEther == -1:
        # #    continue
        # print(currentCAD, bidEther)  
        # coinToBuy = float(currentCAD) / float(bidEther)
        # coinToBuyPercent = coinToBuy * 0.80
        # coinToBuyRound = round(coinToBuyPercent, 5)
        # print(currentCAD, bidEther, coinToBuyRound)
        # exchange.buy(coin, coinToBuyRound)
        # last_buy = True
        # # LIVE TRADING

    
    # hour candles:  [0, -1, 0]
    # spread candles:  [0, 1, 0]
    # +1.4, +0.6, +9
    # 1/1

    BUY2 = [0,-1,0]
    SPREADBUY2 = [0,1,0]
    decision_2 = is_slice_in_list(BUY2,bidCandles)
    decision_spread_2 = is_slice_in_list(SPREADBUY2,spreadCandles)
    #print('Buy 1 decision: ' + str(decision_1))
    if decision_2 == True and decision_spread_2 == True:
        #print / save data to database
        print('Decision: BUY [0,-1,0]') 
        print(bids)
        print(asks)
        print(spreads)

        # # COMMENT/UNCOMMENT BELOW 
        # # LIVE TRADING
        # currentCAD = exchange.getBalance('cad')[0]
        # bidEther, askEther = exchange.getLatestPrice('ether')
        # #if bidEther == -1 or askEther == -1:
        # #    continue
        # print(currentCAD, bidEther)  
        # coinToBuy = float(currentCAD) / float(bidEther)
        # coinToBuyPercent = coinToBuy * 0.80
        # coinToBuyRound = round(coinToBuyPercent, 5)
        # print(currentCAD, bidEther, coinToBuyRound)
        # exchange.buy(coin, coinToBuyRound)
        # last_buy = True
        # # LIVE TRADING


    # hour candles:  [-1, 1, -1]
    # spread candles:  [0, 1, -1]
    # followed by +4.89
    # 2/3

    BUY3 = [-1,1,-1]
    SPREADBUY3 = [0,1,-1]
    decision_3 = is_slice_in_list(BUY3,bidCandles)
    decision_spread_3 = is_slice_in_list(SPREADBUY3,spreadCandles)
    #print('Buy 1 decision: ' + str(decision_1))
    if decision_3 == True and decision_spread_3 == True:
        #print / save data to database
        print('Decision: BUY [-1,1,-1]') 
        print(bids)
        print(asks)
        print(spreads)

        # # COMMENT/UNCOMMENT BELOW 
        # # LIVE TRADING
        # currentCAD = exchange.getBalance('cad')[0]
        # bidEther, askEther = exchange.getLatestPrice('ether')
        # #if bidEther == -1 or askEther == -1:
        # #    continue
        # print(currentCAD, bidEther)  
        # coinToBuy = float(currentCAD) / float(bidEther)
        # coinToBuyPercent = coinToBuy * 0.80
        # coinToBuyRound = round(coinToBuyPercent, 5)
        # print(currentCAD, bidEther, coinToBuyRound)
        # exchange.buy(coin, coinToBuyRound)
        # last_buy = True
        # # LIVE TRADING

    # hour candles:  [-1, -1, -1]
    # spread candles:  [1, 1, -1]
    # followed by +15.99
    # 1/1

    BUY4 = [-1,-1,-1]
    SPREADBUY4 = [1,1,-1]
    decision_4 = is_slice_in_list(BUY4,bidCandles)
    decision_spread_4 = is_slice_in_list(SPREADBUY4,spreadCandles)
    #print('Buy 1 decision: ' + str(decision_1))
    if decision_4 == True and decision_spread_4 == True:
        #print / save data to database
        print('Decision: BUY [-1,-1,-1]') 
        print(bids)
        print(asks)
        print(spreads)

        # # COMMENT/UNCOMMENT BELOW 
        # # LIVE TRADING
        # currentCAD = exchange.getBalance('cad')[0]
        # bidEther, askEther = exchange.getLatestPrice('ether')
        # #if bidEther == -1 or askEther == -1:
        # #    continue
        # print(currentCAD, bidEther)  
        # coinToBuy = float(currentCAD) / float(bidEther)
        # coinToBuyPercent = coinToBuy * 0.80
        # coinToBuyRound = round(coinToBuyPercent, 5)
        # print(currentCAD, bidEther, coinToBuyRound)
        # exchange.buy(coin, coinToBuyRound)
        # last_buy = True
        # # LIVE TRADING


    #if -1,1,1 then buy
    BUY2PASS = [-1,1,1]
    decision_2 = is_slice_in_list(BUY2PASS,bidCandles)
    #print('Buy 2 decision: ' + str(decision_2))
    if decision_2 == True:
        #print / save data to database
        print('Decision: PASS2 [-1,1,1]') 
        print(bids)
    
    #if 1,1,1 then pass
    BUY3 = [1,1,1]
    decision_3 = is_slice_in_list(BUY3,bidCandles)
    #print('Sell 1 decision: ' + str(decision_3))
    if decision_3 == True:
        #print / save data to database
        print('Decision: PASS3 [1,1,1]') 
        print(bids)


    #if -1,-1,1 then sell
    SKIP2 = [-1,-1,1]
    decision_4 = is_slice_in_list(SKIP2,bidCandles)
    #print('Sell 2 decision: ' + str(decision_4))
    if decision_4 == True:
        
        #print / save data to database
        print('Decision: SKIP2') 
        print(bids)

    #if -1,-1,0 then sell
    SKIP3 = [-1,-1,0]
    decision_5 = is_slice_in_list(SKIP3,bidCandles)
    #print('Sell 3 decision: ' + str(decision_5))
    if decision_5 == True:
        
        #print / save data to database
        print('Decision: SKIP3') 
        print(bids)


    # #if -1,-1,-1 do nothing
    # PASS1 = [-1,-1,-1]
    # decision_6 = is_slice_in_list(PASS1,bidCandles)
    # #print('Pass 1 decision: ' + str(decision_6))
    # if decision_6 == True:
    #     #print / save data to database
    #     print('Decision: PASS1') 
    #     print(bids)

    #if 1,1,0 do nothing
    PASS2 = [1,1,0]
    decision_7 = is_slice_in_list(PASS2,bidCandles)
    #print('Pass 2 decision: ' + str(decision_7))
    if decision_7 == True:
        #print / save data to database
        print('Decision: PASS2') 
        print(bids)

    #if -1,0,-1 do nothing
    PASS3 = [-1,0,-1]
    decision_8 = is_slice_in_list(PASS3,bidCandles)
    #print('Pass 3 decision: ' + str(decision_8))
    if decision_8 == True:
        #print / save data to database
        print('Decision: PASS3') 
        print(bids)

    #if 1,0,1 do nothing
    PASS4 = [1,0,1]
    decision_9 = is_slice_in_list(PASS4,bidCandles)
    #print('Pass 4 decision: ' + str(decision_9))
    if decision_9 == True:
        #print / save data to database
        print('Decision: PASS4') 
        print(bids)

    #if -1,0,1 do nothing
    PASS5 = [-1,0,1]
    decision_10 = is_slice_in_list(PASS5,bidCandles)
    #print('Pass 5 decision: ' + str(decision_10))
    if decision_10 == True:
        #print / save data to database
        print('Decision: PASS5') 
        print(bids)

    #if 1,-1,0 do nothing
    PASS6 = [1,-1,0]
    decision_11 = is_slice_in_list(PASS6,bidCandles)
    #print('Pass 6 decision: ' + str(decision_11))
    if decision_11 == True:
        #print / save data to database
        print('Decision: PASS6') 
        print(bids)

    #if 0,0,1 do nothing
    PASS7 = [0,0,1]
    decision_12 = is_slice_in_list(PASS7,bidCandles)
    #print('Pass 7 decision: ' + str(decision_12))
    if decision_12 == True:
        #print / save data to database
        print('Decision: PASS7') 
        print(bids)

    #if 0,-1,1 do nothing
    PASS8 = [0,-1,1]
    decision_13 = is_slice_in_list(PASS8,bidCandles)
    #print('Pass 8 decision: ' + str(decision_13))
    if decision_13 == True:
        #print / save data to database
        print('Decision: PASS8') 
        print(bids)

    #if 0,1,-1 do nothing
    PASS9 = [0,1,-1]
    decision_14 = is_slice_in_list(PASS9,bidCandles)
    #print('Pass 9 decision: ' + str(decision_14))
    if decision_14 == True:
        #run buy function
        
        #print / save data to database
        print('Decision: PASS9') 
        print(bids)
        
    # #if 0,0,-1 do nothing
    # PASS10 = [0,0,-1]
    # decision_15 = is_slice_in_list(PASS10,bidCandles)
    # #print('Pass 10 decision: ' + str(decision_14))
    # if decision_15 == True:
    #     #print / save data to database
    #     print('Decision: PASS10') 
    #     print(bids)
        
    # #if -1,1,-1 do nothing
    # PASS11 = [-1,1,-1]
    # decision_16 = is_slice_in_list(PASS11,bidCandles)
    # #print('Pass 10 decision: ' + str(decision_14))
    # if decision_16 == True:
    #     #print / save data to database
    #     print('Decision: PASS11') 
    #     print(bids)
        
    #if -1,0,0 do nothing
    PASS12 = [-1,0,0]
    decision_17 = is_slice_in_list(PASS12,bidCandles)
    #print('Pass 10 decision: ' + str(decision_14))
    if decision_17 == True:
        #print / save data to database
        print('Decision: PASS12') 
        print(bids)
        
    #if 0,-1,0 do nothing
    PASS13 = [0,-1,0]
    decision_18 = is_slice_in_list(PASS13,bidCandles)
    #print('Pass 10 decision: ' + str(decision_14))
    if decision_18 == True:
        #print / save data to database
        print('Decision: PASS13') 
        print(bids)