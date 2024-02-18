# fast_tradier_client in Python
Tradier client in python for trading stocks and options through Tradier API

#### Dependencies:
- jsonpickle
- httpx
- arrow
- autoscraper
- pandas
- python-interface

#### Dependencies for unit tests:
- pytest
- pytest_httpx
- pytest-asyncio

#### Examples below:
1. Test Account:
```python

from fast_tradier.models.account.Position import Position
from fast_tradier.models.market_data.Quote import Quote

account_position = {
    "cost_basis": 207.01,
    "date_acquired": "2018-08-08T14:41:11.405Z",
    "id": 130089,
    "quantity": 1.00000000,
    "symbol": "AAPL"
}

position = Position(account_position)
print(position.to_json())
print(position.symbol)
print(position.date_acquired)
print('-------' * 10)

quote1 = {
        "symbol": "VXX190517P00016000",
        "description": "VXX May 17 2019 $16.00 Put",
        "exch": "Z",
        "type": "option",
        "last": None,
        "change": None,
        "volume": 0,
        "open": None,
        "high": None,
        "low": None,
        "close": None,
        "bid": 0.0,
        "ask": 0.01,
        "underlying": "VXX",
        "strike": 16.0,
        "change_percentage": None,
        "average_volume": 0,
        "last_volume": 0,
        "trade_date": 0,
        "prevclose": None,
        "week_52_high": 0.0,
        "week_52_low": 0.0,
        "bidsize": 0,
        "bidexch": "I",
        "bid_date": 1557167321000,
        "asksize": 618,
        "askexch": "Z",
        "ask_date": 1557168367000,
        "open_interest": 10,
        "contract_size": 100,
        "expiration_date": "2019-05-17",
        "expiration_type": "standard",
        "option_type": "put",
        "root_symbol": "VXX"
      }

my_q = Quote(quote1)
print(my_q.symbol)
print(my_q.ask_date_datetime)
```

2. Test Client:
```python

from fast_tradier.FastTradierAsyncClient import FastTradierAsyncClient
from fast_tradier.FastTradierClient import FastTradierClient
from fast_tradier.models.market_data.Quote import Quote
from fast_tradier.models.trading.OptionOrder import OptionLeg, OptionOrder
from fast_tradier.models.trading.EquityOrder import EquityOrder
from fast_tradier.models.trading.Sides import OptionOrderSide, EquityOrderSide
from fast_tradier.models.trading.PriceTypes import OptionPriceType, EquityPriceType
from fast_tradier.models.trading.Duration import Duration

import asyncio

#TODO: replace the client_id and sandbox access token with yours
sandbox_client_id = 'VA123456789'
sandbox_at = 'abcdefghijklmnopqrstuvwxyzzzz'

def mock_order() -> OptionOrder:
    ticker = 'SPX'
    order_status = 'pending'
    option_symbols = ['SPXW_080823C4510', 'SPXW_080823C4520'] #TODO: replace option symbols
    sides = [OptionOrderSide.SellToOpen, OptionOrderSide.BuyToOpen]
    option_legs = []

    for i in range(len(sides)):
        opt_symbol = option_symbols[i]
        side = sides[i]
        option_legs.append(OptionLeg(underlying_symbol=ticker, option_symbol=opt_symbol, side=side, quantity=1))

    option_order = OptionOrder(ticker=ticker,
                            price=1.2,
                            price_type=OptionPriceType.Credit,
                            duration=Duration.Day,
                            option_legs=option_legs)
    return option_order

def mock_equity_order() -> EquityOrder:
    symbol = 'SPY'
    price = 379.0
    quantity = 1.0
    return EquityOrder(ticker=symbol, quantity=quantity, price=price, side=EquityOrderSide.Buy, price_type=EquityPriceType.Limit, duration=Duration.Gtc)

async def async_test():
    tasks = []
    count = 4
    tradier_client = FastTradierAsyncClient(sandbox_at, sandbox_client_id, is_prod=False)
    
    quote1 = await tradier_client.get_quotes_async(['MSFT'])
    print('quote1 last price: ', quote1[0].last)

    for i in range(count):
        tasks.append(asyncio.ensure_future(tradier_client.place_option_order_async(mock_order())))

    order_ids = await asyncio.gather(*tasks)
    cancel_tasks = []
    for order_id in order_ids:
        print('order_id: ', order_id)
        cancel_tasks.append(asyncio.ensure_future(tradier_client.cancel_order_async(order_id)))
    
    is_canceled = await asyncio.gather(*cancel_tasks)
    for canceled in is_canceled:
        print('canceled? ', canceled)
    
    ### test equity order:
    equity_order = mock_equity_order()
    order_id = await tradier_client.place_equity_order_async(equity_order)
    print('equity order id: ', order_id)
    equity_order_canceled = await tradier_client.cancel_order_async(order_id)
    print('equity order canceld? ', equity_order_canceled)

    ### get option chain for spx
    ticker = 'spx'
    expiration = '2023-08-31' #TODO: replace the expiration date
    opt_chain_result = await tradier_client.get_option_chain_async(symbol=ticker, expiration=expiration)
    print('result of option chain: ', opt_chain_result)
    positions = await tradier_client.get_positions_async()
    print('positions: ', positions)

    print('------' * 10)
    balances = await tradier_client.get_account_balance_async()
    print('balances: ', balances.total_cash)
    if hasattr(balances, 'pdt') and balances.pdt is not None:
        print('balances.pdt.to_json(): ', balances.pdt.to_json())
    elif hasattr(balances, 'margin') and balances.margin is not None:
        print('balances.margin.to_json: ', balances.margin.to_json())
    elif hasattr(balances, 'cash') and balances.cash is not None:
        print('balances.cash.to_json: ', balances.cash.to_json())

def sync_test():
    count = 4
    tradier_client = FastTradierClient(sandbox_at, sandbox_client_id, is_prod=False)
    quote1 = tradier_client.get_quotes(['MSFT'])
    print('quote1 last price: ', quote1[0].last)

    order_id = tradier_client.place_option_order(mock_order())
    print('option order id: ', order_id)
    canceled_order = tradier_client.cancel_order(order_id)
    print('canceled order? ', canceled_order)

    ### test equity order:
    equity_order = mock_equity_order()
    order_id = tradier_client.place_equity_order(equity_order)
    print('equity order id: ', order_id)
    equity_order_canceled = tradier_client.cancel_order(order_id)
    print('equity order canceld? ', equity_order_canceled)

    ### get option chain for spx
    ticker = 'spx'
    expiration = '2023-08-31' #TODO: replace the expiration date
    opt_chain_result = tradier_client.get_option_chain(symbol=ticker, expiration=expiration)
    print('result of option chain: ', opt_chain_result)
    positions = tradier_client.get_positions()
    print('positions: ', positions)

    print('------' * 10)
    balances = tradier_client.get_account_balance()
    print('balances: ', balances.total_cash)
    if hasattr(balances, 'dt') and balances.pdt is not None:
        print('balances.pdt.to_json(): ', balances.pdt.to_json())
    elif hasattr(balances, 'margin') and balances.margin is not None:
        print('balances.margin.to_json: ', balances.margin.to_json())
    elif hasattr(balances, 'cash') and balances.cash is not None:
        print('balances.cash.to_json: ', balances.cash.to_json())

asyncio.run(async_test())
print('-------finished async tests--------')
sync_test()
print('-------finished sync tests-------')
```

3. Test model like `TradierQuote`:

```python
import json
from fast_tradier.models.market_data.TradierQuote import TradierQuote
from fast_tradier.models.trading.OptionOrder import OptionOrder, OptionLeg
from fast_tradier.models.trading.Sides import OptionOrderSide
from fast_tradier.models.trading.PriceTypes import OptionPriceType
from fast_tradier.models.trading.Duration import Duration

quote1 = TradierQuote(symbol='spx', type='stock', open=1000.0, high=2012.1, low=1999.0, close=4910.1, volume=30000, bid=1.2, ask=2.3, last_price=4.3)
json_obj = quote1.serialize()
print('serialize: ', json_obj)

quote2 = TradierQuote.deserialize_from_json(json_obj)
print('quote2.ask: ', quote2.ask)

print('--------' * 10)
ticker = 'SPX'
order_status = 'pending'
option_symbols = ['SPXW_052223C4225', 'SPXW_052223C4235']
sides = ['sell_to_open', 'buy_to_open']
option_legs = []

for i in range(len(sides)):
    opt_symbol = option_symbols[i]
    side = sides[i]
    option_legs.append(OptionLeg(underlying_symbol=ticker, option_symbol=opt_symbol, side=side, quantity=1))

option_order = OptionOrder(ticker=ticker,
                           price=100.0,
                           price_type=OptionPriceType.Market,
                           duration=Duration.Day,
                           option_legs=option_legs)

order_json = option_order.to_json()
print('option_order json: ', order_json)
parsable_json = option_order.serialize()
print('parsable order json: ', parsable_json)
option_order2 = OptionOrder.deserialize_from_json(parsable_json)
print('option_order2.price: ', option_order2.price)

```

4. Get history quotes

```
from fast_tradier.utils.TimeUtils import TimeUtils
from fast_tradier.models.trading.Interval import Interval
from fast_tradier.FastTradierAsyncClient import FastTradierAsyncClient

import pandas as pd

ticker = 'AAPL'
start_date = TimeUtils.past_date(days_ago = 100)
end_date = TimeUtils.today_date()

tradier_client = FastTradierAsyncClient(sandbox_at, sandbox_client_id, is_prod=False)

history_quotes = await tradier_client.get_history_async(symbol=ticker, start_date=start_date, end_date=end_date, interval=Interval.Daily)
print(history_quotes)
if history_quotes is not None:
    print(history_quotes.head())

```

5. Real time quote

As of 8/6/2023, Tradier does not provide real time quote for index like SPX, instead its quote has 15 minute delay. To help solve this problem, the constructor of `FastTradierAsyncClient` and `FastTradierClient` takes an optional object for getting real time quote.

To implement the interface `IRealTimeQuoteProvider`, reference to `YFinanceQuoteProvider` that uses web scraping to get real time quote from Yahoo Finance.

```python
from fast_tradier.utils.YFinanceQuoteProvider import YFinanceQuoteProvider
from fast_tradier.FastTradierAsyncClient import FastTradierAsyncClient

yfin_real_quote_provider = YFinanceQuoteProvider()
tradier_client = FastTradierAsyncClient(sandbox_at, sandbox_client_id, is_prod=False real_time_quote_provider=yfin_real_quote_provider)

```
