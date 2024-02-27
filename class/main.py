import random
from keys import api, secret, accountType
from helper import Bybit
from time import sleep
import ta
from threading import Thread

session = Bybit(api, secret, accountType)

tp = 0.012
sl = 0.009
mode = 1
leverage = 10
timeframe = 60
qty = 10
max_positions = 1


def rsi_signal(session, symbol):
    kl = session.klines(symbol, timeframe)
    rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
    if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
        return 'up'
    if rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
        return 'down'
    else:
        return 'none'


def signal2(symbol):
    kl = session.klines(symbol, timeframe)
    ema200 = ta.trend.ema_indicator(kl.Close, window=200)
    if kl.Close.iloc[-1] > kl.Open.iloc[-1]:
        if abs(kl.High.iloc[-1]-kl.Close.iloc[-1]) > abs(kl.Close.iloc[-1] - kl.Open.iloc[-1]) and kl.Close.iloc[-1] < ema200.iloc[-1]:
            return 'sell'
        if abs(kl.Open.iloc[-1] - kl.Low.iloc[-1]) > abs(kl.Close.iloc[-1] - kl.Open.iloc[-1]) and kl.Close.iloc[-1] > ema200.iloc[-1]:
            return 'buy'
    if kl.Close.iloc[-1] < kl.Open.iloc[-1]:
        if abs(kl.High.iloc[-1]-kl.Open.iloc[-1]) > abs(kl.Open.iloc[-1] - kl.Close.iloc[-1]) and kl.Close.iloc[-1] < ema200.iloc[-1]:
            return 'sell'
        if abs(kl.Close.iloc[-1] - kl.Low.iloc[-1]) > abs(kl.Open.iloc[-1] - kl.Open.iloc[-1]) and kl.Close.iloc[-1] > ema200.iloc[-1]:
            return 'buy'


qty = 10
symbols = session.get_tickers()
while True:
    balance = session.get_balance()
    if balance is None or symbols is None:
        print('Cant connect')
        sleep(120)
    if balance is not None and symbols is not None:
        print(f'Account balance: {balance} USDT')
        try:
            positions = session.get_positions()
            print(f'Opened positions: {len(positions)}')
            last_pnl = session.get_last_pnl(10)
            print(f'Last 10 PnL: {last_pnl} USDT')
            current_pnl = session.get_current_pnl()
            print(f'Current PnL: {current_pnl} USDT')
            for elem in symbols:
                positions = session.get_positions()
                if len(positions) >= max_positions:
                    break
                signal = signal2(elem)
                if signal == 'up' and not elem in positions:
                    print(f'Found BUY signal for {elem}')
                    session.place_order_market(elem, 'buy', mode, leverage, qty, tp, sl)
                    sleep(1)
                if signal == 'down' and not elem in positions:
                    print(f'Found SELL signal for {elem}')
                    session.place_order_market(elem, 'sell', mode, leverage, qty, tp, sl)
                    sleep(1)

        except Exception as err:
            print(err)
            print('No connection')
            sleep(120)
    print('Wait 60 sec')
    sleep(60)



