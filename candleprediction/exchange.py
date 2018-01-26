from exchange_quadriga import QuadrigaExchange

class Exchange:

  def __init__(self, exchange_name, can_buy, can_sell, account, debug):
    self.name = exchange_name
    self.can_buy = can_buy
    self.can_sell = can_sell
    self.account = account

    if (exchange_name == "quadriga"):
      self.exc_object = QuadrigaExchange(exchange_name, can_buy, can_sell, account, debug)
    else:
      print("Error in Exchange init() - Invalid exchange name: " + exchange_name)
      exit(0)

  def canBuy(self):
    # template
    # return true or false
    return self.exc_object.canBuy()


  def canSell(self):
    # template
    # return true or false
    return self.exc_object.canSell()


  def getLatestPrice(self, coin):
    # template
    # param: coin (from exchanges.json)
    # save bid, ask in object
    # Assumptions:
    #   - Coin is mapped to a currency pair. It is assumed the pair's
    #      major is the coin and minor is the currency (USD or CAD, etc)
    #   - Proper conversion needs to be done when fetching and returning prices.
    # return: bid, ask
    return self.exc_object.getLatestPrice(coin)


  def getLatestVolume(self, coin):
    # template
    # param: coin (from exchanges.json)
    # save bid, ask in object
    # Assumptions:
    #   - Coin is mapped to a currency pair. It is assumed the pair's
    #      major is the coin and minor is the currency (USD or CAD, etc)
    #   - Proper conversion needs to be done when fetching and returning prices.
    # return: volume
    return self.exc_object.getLatestVolume(coin)

  def getBid(self):
    # template
    # return last queried coin bid price
    #        -1 if failed fetch occured or getLatestPrice never called
    return self.exc_object.getBid()


  def getAsk(self):
    # template
    # return last queried coin ask price
    #        -1 if failed fetch occured or getLatestPrice never called
    return self.exc_object.getAsk()


  def buy(self, coin, amount=0):
    return self.exc_object.buy(coin, amount)


  def sell(self, coin, amount=0):
    return self.exc_object.sell(coin, amount)

  def sell_limit(self, coin, amount=0, price=0):
    return self.exc_object.sell(coin, amount, price)

  def withdraw(self, amount, coin, to_address):
    return self.exc_object.withdraw(amount, coin, to_address)


  def getBalance(self, coin):
    return self.exc_object.getBalance(coin)
