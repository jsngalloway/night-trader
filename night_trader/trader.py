import time
import numpy as np
from datetime import datetime

def buyAndWait(r):
    price_info = r.crypto.get_crypto_quote("ETH", info=None)
    # will_pay = round((float(price_info["ask_price"]) + float(price_info["mark_price"])) / 2, 2)
    will_pay = round(float(price_info["ask_price"]), 2)
    buy_info = r.orders.order_buy_crypto_limit("ETH", 0.05, will_pay)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Buying (Limit: ${round(will_pay, 2)})...", end="")
    cleared = False
    id = buy_info["id"]
    tries = 0
    while not cleared:
        order_info = r.orders.get_crypto_order_info(id)
        if order_info['state'] == 'filled':
            print(f"bought [{datetime.now().strftime('%H:%M:%S')}] (Exec: ${round(float(order_info['average_price']), 2)})")
            cleared = True
            return (True, float(order_info['average_price']))

        tries = tries + 1
        if tries > 50:
            # cancel order
            print(f"[{datetime.now().strftime('%H:%M:%S')}] cancelling...", end="")
            r.orders.cancel_crypto_order(id)
            order_info = r.orders.get_crypto_order_info(id)
            while(order_info['state'] != 'canceled'):
                order_info = r.orders.get_crypto_order_info(id)
                if order_info['state'] == 'filled':
                    print(f"cancel failed: bought [{datetime.now().strftime('%H:%M:%S')}] (Exec: ${round(float(order_info['average_price']), 2)})")
                    cleared = True
                    return (True, float(order_info['average_price']))

                time.sleep(50/1000) #wait until the order is confirmed canceled
            print(f"canceled [{datetime.now().strftime('%H:%M:%S')}]")
            return (False, 0)

        time.sleep(50/1000) # sleep 50ms

def sellAndWait(r):
    price_info = r.crypto.get_crypto_quote("ETH", info=None)
    will_get = round(float(price_info["bid_price"]), 2)
    # will_pay = round((float(price_info["bid_price"]) + float(price_info["mark_price"])) / 2, 2)
    sell_info = r.orders.order_sell_crypto_limit("ETH", 0.05, will_get)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Selling (Limit: ${round(will_get, 2)})...", end="")
    cleared = False
    if 'id' not in sell_info:
        print("NOT SURE WHAT IS GOING ON HERE, NO ID???")
        print(sell_info)
    id = sell_info["id"]
    tries = 0
    while not cleared:
        order_info = r.orders.get_crypto_order_info(id)
        if order_info['state'] == 'filled':
            print(f"[{datetime.now().strftime('%H:%M:%S')}] sold (Exec: ${round(float(order_info['average_price']), 2)})")
            cleared = True
            return (True, float(order_info["average_price"]))

        tries = tries + 1
        if tries > 50:
            # cancel order
            print(f"[{datetime.now().strftime('%H:%M:%S')}] cancelling...", end="")
            r.orders.cancel_crypto_order(id)
            order_info = r.orders.get_crypto_order_info(id)
            while(order_info['state'] != 'canceled'):
                order_info = r.orders.get_crypto_order_info(id)
                if order_info['state'] == 'filled':
                    print(f"cancel failed: sold [{datetime.now().strftime('%H:%M:%S')}] (Exec: ${round(float(order_info['average_price']), 2)})")
                    cleared = True
                    return (True, float(order_info['average_price']))
                time.sleep(50/1000) #wait until the order is confirmed canceled
            print(f"canceled [{datetime.now().strftime('%H:%M:%S')}].")
            return (False, 0)

        time.sleep(50/1000) # sleep 50ms