import robin_stocks as r
import pandas as pd
import time

ETH_ID = "76637d50-c702-4ed1-bcb5-5b0732a81f48"

# see more at https://nummus.robinhood.com/currency_pairs/
SYMBOLS = {
    "BTC": "3d961844-d360-45fc-989b-f6fca761d511",
    "ETH": "76637d50-c702-4ed1-bcb5-5b0732a81f48",
    "LTC": "383280b1-ff53-43fc-9c84-f01afd0989cd",
    "BCH": "2f2b77c4-e426-4271-ae49-18d5cb296d3a",
    "DOGE": "1ef78e1b-049b-4f12-90e5-555dcf2fe204",
    "ETC": "7b577ce3-489d-4269-9408-796a0d1abb3a",
    "BSV": "086a8f9f-6c39-43fa-ac9f-57952f4a1ba6",
}


def getHistorical(crypto_id) -> dict:
    url = r.urls.crypto_historical(crypto_id)
    payload = {"interval": "15second", "span": "hour", "bounds": "24_7"}
    data = r.helper.request_get(url, "regular", payload)
    if (not data) or (not type(data) is dict) or (data.get("data_points") == None):
        print("Invalid response, trying again in 60 seconds.")
        time.sleep(60)
        return getHistorical()
    return data["data_points"]


def appendToFile(filePath: str, crypto_id: str):
    raw_data = getHistorical(crypto_id)
    print("Dumping full data...")
    
    full_df = pd.DataFrame(raw_data)[
        ["begins_at", "open_price", "close_price", "high_price", "low_price", "volume"]
    ]

    full_df.to_csv(
        filePath,
        header=False,
        index=False,
        mode="a",
    )
    print("Dump complete")


if __name__ == "__main__":
    # execute only if run as a script
    print(
        "---------------------------------- Dumping RobinHood Api Data ----------------------------------"
    )

    # Load and read username and password env files
    usernameFile = open("D:/Documents/Projects/night-trader/env/username", "r")
    username = usernameFile.read()
    passwordFile = open("D:/Documents/Projects/night-trader/env/password", "r")
    password = passwordFile.read()

    print("Logging in...", end="")
    login = r.login(username, password)
    if not login["access_token"]:
        print("FAILURE")
        print("system exiting.")
        r.authentication.logout()
        exit()
    print("Making Api call")

    # raw_data = r.crypto.get_crypto_historicals("ETH", interval='15second', span='hour', bounds='24_7', info=None)
    raw_data = getHistorical(ETH_ID)
    df = pd.DataFrame(raw_data)[["begins_at", "open_price"]]
    df = df.rename(columns={"begins_at": "time", "open_price": "price"})

    print("Dumping...")
    df.to_csv(
        "D:/Documents/Projects/night-trader/data/dump.csv",
        header=False,
        index=False,
        mode="a",
    )
    print("Dump complete")

    appendToFile("D:/Documents/Projects/night-trader/data/ETH.csv", SYMBOLS["ETH"])
    appendToFile("D:/Documents/Projects/night-trader/data/LTC.csv", SYMBOLS["LTC"])
    appendToFile("D:/Documents/Projects/night-trader/data/BCH.csv", SYMBOLS["BCH"])
    appendToFile("D:/Documents/Projects/night-trader/data/ETC.csv", SYMBOLS["ETC"])
