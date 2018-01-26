import hmac
import hashlib
import base64
import time
import requests
import json
from quadriga import QuadrigaClient # using https://github.com/joowani/quadriga/
from pprint import pprint

class QuadrigaExchange:

  global url_buy_market_order
  url_buy_market_order = 'https://api.quadrigacx.com/v2/buy'

  global url_price_fetch
  url_price_fetch = 'https://api.quadrigacx.com/v2/ticker'

  global coin_map
  coin_map = {
    'bitcoin'  : 'btc_cad',
    'litecoin' : 'ltc_cad',
    'ether'    : 'eth_cad'
  }

  global coin_balance_map
  coin_balance_map = {
    'bitcoin'  : ['btc_balance', 'btc_available', 'btc_reserved'],
    'litecoin' : ['ltc_balance', 'ltc_available', 'ltc_reserved'],
    'ether'    : ['eth_balance', 'eth_available', 'eth_reserved'],
    'cad'      : ['cad_balance', 'cad_available', 'cad_reserved']
  }

  global coin_abbrev_map
  coin_abbrev_map = {
    'bitcoin'  : 'btc',
    'litecoin' : 'ltc',
    'ether'    : 'eth'
  }

  def __init__(self, exchange_name, can_buy, can_sell, account, debug):
    self.name     = exchange_name
    self.can_buy  = can_buy
    self.can_sell = can_sell
    self.account  = account
    self.bid = -1
    self.ask = -1
    self.volume = -1
    self.debug = debug
    self.load_key(self.account)

  def getLatestPrice(self, coin):
    if coin not in coin_map:
      print("coin: " + coin + " not in Quadriga coin_map")
      self.bid = -1
      self.ask = -1
      return -1, -1
    params = {'book': coin_map[coin]}
    response = requests.get(url_price_fetch, params=params)
    res = response.json()
    #print("\n\nquadriga json: " + str(data))
    try:
      self.bid = res['bid']
      self.ask = res['ask']
    except Exception as e:
      print("Error in getLatestPrice,", self.name, "- could not read ask/bid prices")
      print(str(e))

    return float(self.bid), float(self.ask)

  def getLatestVolume(self, coin):
    if coin not in coin_map:
      print("coin: " + coin + " not in Quadriga coin_map")
      self.volume = -1
      return -1
    params = {'book': coin_map[coin]}
    response = requests.get(url_price_fetch, params=params)
    res = response.json()
    #print("\n\nquadriga json: " + str(data))
    try:
      self.volume = res['volume']
    except Exception as e:
      print("Error in getLatestVolume,", self.name, "- could not read volume")
      print(str(e))

    return float(self.volume)

  def getBid(self):
    return self.bid


  def getAsk(self):
    return self.ask


  def canBuy(self):
    return self.can_buy


  def canSell(self):
    return self.can_sell


  def buy(self, coin, amount=0):
    if amount == 0:
      print("Error QuadrigaExchange.buy(): Enter a valid coin amount to buy")
      return False, ""

    if coin not in coin_map:
      print("Error QuadrigaExchange.buy(): Coin not in coin_map")
      return False, ""

    client = QuadrigaClient(api_key=self.key,
                              api_secret=self.secret,
                              client_id=self.client_id,
                              timeout=None,
                              session=None,
                              logger=None)

    pair = coin_map[coin]
    res = client.book(pair).buy_market_order(amount)

    return True, res


  def sell(self, coin, amount=0):
    if amount == 0:
      print("Error QuadrigaExchange.sell(): Enter a valid coin amount to sell")
      return False, ""

    if coin not in coin_map:
      print("Error QuadrigaExchange.sell(): Coin not in coin_map")
      return False, ""

    client = QuadrigaClient(api_key=self.key,
                              api_secret=self.secret,
                              client_id=self.client_id,
                              timeout=None,
                              session=None,
                              logger=None)

    pair = coin_map[coin]
    res = client.book(pair).sell_market_order(amount)

    return True, res


  def sell_limit(self, coin, amount=0, price=0):
    if amount == 0:
      print("Error QuadrigaExchange.sell(): Enter a valid coin amount to sell")
      return False, ""

    if coin not in coin_map:
      print("Error QuadrigaExchange.sell(): Coin not in coin_map")
      return False, ""

    client = QuadrigaClient(api_key=self.key,
                              api_secret=self.secret,
                              client_id=self.client_id,
                              timeout=None,
                              session=None,
                              logger=None)

    pair = coin_map[coin]
    res = client.book(pair).sell_limit_order(amount, price)

    return True, res


  def getBalance(self, coin):
    if coin not in coin_balance_map:
      print("Error QuadrigaExchange.getBalance(): Coin not in coin_balance_map")
      return False, ""

    client = QuadrigaClient(api_key=self.key,
                            api_secret=self.secret,
                            client_id=self.client_id,
                            timeout=None,
                            session=None,
                            logger=None)
    res = client.get_balance()
    return res[coin_balance_map[coin][0]], res[coin_balance_map[coin][1]], res[coin_balance_map[coin][2]]


  #TODO: not tested
  # Note: address passed must be setup in api settings to be accepted as a withdrawal address
  def withdraw(self, coin, amount, to_address):
    if coin not in coin_map:
        print("Error QuadrigaExchange.withdraw(): Coin not in coin_map")
        return False, ""

    client = QuadrigaClient(api_key=self.key,
                            api_secret=self.secret,
                            client_id=self.client_id,
                            timeout=None,
                            session=None,
                            logger=None)

    res = client.withdraw(coin_abbrev_map[coin], amount, to_address)
    print("withdraw response:", res)


  def load_key(self, path):
    with open(path, 'r') as f:
      self.key       = f.readline().split('=')[1].strip().strip('"')
      self.secret    = f.readline().split('=')[1].strip().strip('"')
      self.client_id = f.readline().split('=')[1].strip().strip('"')
    return


'''

buy response
  # buy response: 
  #   {'amount': '0.00000000', 
  #   'book': 'eth_cad', 
  #   'datetime': '2018-01-16 00:40:21', 
  #   'id': '',
  #   'price': '0.00', 
  #   'status': '0', 
  #   'type': '0'}

sell response
  # sell response: 
  #  {'amount': '0.00050000',
  #  'book': 'eth_cad', 
  #  'datetime': '2018-01-16 00:34:50', 
  #  'id': '', 
  #  'price': '0.00',
  #  'status': '0',
  #  'type': '1'}

getBalance() response
  {'btc_available': '0.00000000', 'btc_reserved': '0.00000000', 'btc_balance': '0.00000000', 'bch_available': '0.00000000', 'bch_reserved': '0.00000000', 'bch_balance': '0.00000000', 'btg_available': '0.00000000', 'btg_reserved': '0.00000000', 'btg_balance': '0.00000000', 'eth_available': '0.00250000', 'eth_reserved': '0.00000000', 'eth_balance': '0.00250000', 'ltc_available': '0.00000000', 'ltc_reserved': '0.00000000', 'ltc_balance': '0.00000000', 'etc_available': '0.00000000', 'etc_reserved': '0.00000000', 'etc_balance': '0.00000000', 'cad_available': '3.92', 'cad_reserved': '0.00', 'cad_balance': '3.92', 'usd_available': '0.00', 'usd_reserved': '0.00', 'usd_balance': '0.00', 'xau_available': '0.000000', 'xau_reserved': '0.000000', 'xau_balance': '0.000000', 'fee': '0.5000', 'fees': {'btc_cad': '0.5000', 'btc_usd': '0.5000', 'eth_cad': '0.5000', 'eth_btc': '0.2000', 'ltc_cad': '0.5000', 'ltc_btc': '0.2000', 'bch_cad': '0.5000', 'bch_btc': '0.2000', 'btg_cad': '0.5000', 'btg_btc': '0.2000'}}



'''