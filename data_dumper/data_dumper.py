import robin_stocks as r
import pandas as pd
import time

ETH_ID = "76637d50-c702-4ed1-bcb5-5b0732a81f48"

def getHistorical() -> dict:
    url = r.urls.crypto_historical(ETH_ID)
    payload = {'interval': "15second",
                'span': "hour",
                'bounds': "24_7"}
    data = r.helper.request_get(url, 'regular', payload)
    if (not data) or (not type(data) is dict) or (data.get('data_points') == None):
      print("Invalid response, trying again in 60 seconds.")
      time.sleep(60)
      return getHistorical()
    return data['data_points']

if __name__ == "__main__":
    # execute only if run as a script
    print("---------------------------------- Dumping RobinHood Api Data ----------------------------------")
    
    # Load and read username and password env files
    usernameFile = open("D:/Documents/Projects/night-trader/env/username", "r")
    username = usernameFile.read()
    passwordFile = open("D:/Documents/Projects/night-trader/env/password", "r")
    password = passwordFile.read()

    print("Logging in...", end='')
    login = r.login(username, password)
    if not login["access_token"]:
        print("FAILURE")
        print("system exiting.")
        r.authentication.logout()
        exit()
    print("Making Api call")
    
    # raw_data = r.crypto.get_crypto_historicals("ETH", interval='15second', span='hour', bounds='24_7', info=None)
    raw_data = getHistorical()
    df = pd.DataFrame(raw_data)[["begins_at", "open_price"]]
    df = df.rename(columns={"begins_at":"time", "open_price":"price"})
    
    print("Dumping...")
    df.to_csv("D:/Documents/Projects/night-trader/data/dump.csv", header=False, index=False, mode='a')
    print("Dump complete")

    print("Dumping full data...")
    full_df = pd.DataFrame(raw_data)[["begins_at", "open_price", "close_price", "high_price", "low_price", "volume"]]
    full_df.to_csv("D:/Documents/Projects/night-trader/data/ETH.csv", header=False, index=False, mode='a')
    print("Dump complete")