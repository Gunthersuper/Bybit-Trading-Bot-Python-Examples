import random
from keys import api, secret, accountType
from helper import Bybit
from time import sleep
import ta
from threading import Thread

session = Bybit(api, secret, accountType)

tp = 0.02
sl = 0.015
mode = 1
leverage = 10
timeframe = 5
qty = 10
max_positions = 200


def rsi_signal(symbol):
    kl = session.klines(symbol, timeframe)
    rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
    if rsi.iloc[-2] < 25:
        return 'buy'
    if rsi.iloc[-2] > 75:
        return 'sell'

qty = 10
symbols = session.get_tickers()
while True:
    try:
        balance = session.get_balance()
        # qty = balance * 0.3
        print(f'Balance: {round(balance, 3)} USDT')
        positions = session.get_positions()
        print(f'{len(positions)} Positions: {positions}')

        for symbol in symbols:
            positions = session.get_positions()
            if len(positions) >= max_positions:
                break
            sign = rsi_signal(symbol)
            if sign is not None and not symbol in positions:
                print(symbol, sign)
                session.place_order_market(symbol, sign, mode, leverage, qty, tp, sl)
                sleep(1)

        wait = 100
        print(f'Waiting {wait} sec')
        sleep(wait)
    except Exception as err:
        print(err)
        sleep(30)


