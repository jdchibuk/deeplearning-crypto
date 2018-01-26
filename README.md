# Deeplearning Crypto

Attention this is not investment advice and no guarantee in results. The included repository and anything written does not represent investment advice. All data used and prediction results are experimental results and do no constitute as investment advice. Experiment with at your own risk.


This repository using Ethereum and Canadian dollar to buy and sell.


Three avenues are explored in this repository:


1. /candleprediction - Using differences in bid and ask prices to predict when to buy so that the next time period you sell at a profit
2. /ml-notebooks - A simple random forest classification which predicts on a 1 minute interval if the next minute will be a buy or pass state as defined by an increase in price
3. /ml-notebooks - A simple feedforward neural network; same as the random forest classifier but using hidden features



To setup: 
- In quadriga.key replace the key, secret and client_id with your own from QuadrigaCX
- LN 33 in simple_candle_decision_live_buy_sell.py, enter in your QuadrigaCX Ethereum address
- Current setup is set to poll bid, ask prices, volumes at 1 minute intervals (change LN 14 query_every_sec to any amount you like)
- Decisions on deltas are based on 5 minute intervals or LN 15 max_arr_len = 5 (change as you like)
- If you change array length be sure to change LN 110 to to represent the new time a decision has be made current is 300 sec or 5 minutes


Within (1) run: 

	python simple_candle_decision_live_buy_sell.py

Within (2) run - dev environment python 3.2 attached is Conda 

	jupyter notebook

	run through cells to generate new prediction results