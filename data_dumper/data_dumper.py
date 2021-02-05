import robin_stocks as r
import pandas as pd
import time
import sys

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


def appendToFile(filePath: str, crypto_symbol: str):
    crypto_id = SYMBOLS[crypto_symbol]
    print("------ Beginning {crypto_symbol} dump ------")
    print("Making API call...", end="")
    raw_data = getHistorical(crypto_id)
    print("done")
    
    print(f"Reading data and removing dupes...", end="")
    
    full_df = pd.DataFrame(raw_data)[
        ["begins_at", "open_price", "close_price", "high_price", "low_price", "volume"]
    ]
    full_df.index = pd.DatetimeIndex(pd.to_datetime(full_df["begins_at"].values, utc=True))

    from_file = pd.read_csv(filePath)

    from_file.index = pd.DatetimeIndex(pd.to_datetime(from_file["begins_at"].values, utc=True))
    
    full_df = full_df[~full_df.index.isin(from_file.index)].dropna()
    print("done")

    print(f"Writing ({len(full_df)}) new values to {filePath}...", end="")
    full_df.to_csv(
        filePath,
        header=False,
        index=False,
        mode="a",
    )
    print("done")


if __name__ == "__main__":
    # execute only if run as a script
    print(
        "---------------------------------- Dumping RobinHood Api Data ----------------------------------"
    )

    cred_dir = str(sys.argv[1])
    output_dir = str(sys.argv[2])
    # Load and read username and password env files
    usernameFile = open(f"{cred_dir}/username", "r")
    username = usernameFile.read()
    passwordFile = open(f"{cred_dir}/password", "r")
    password = passwordFile.read()

    print("Logging in...", end="")
    login = r.login(username, password)
    if not login["access_token"]:
        print("FAILURE")
        print("system exiting.")
        r.authentication.logout()
        exit()
    print("done")

    # raw_data = r.crypto.get_crypto_historicals("ETH", interval='15second', span='hour', bounds='24_7', info=None)
    print("Beginning call and appends...")
    appendToFile(f"{output_dir}/ETH.csv", "ETH")
    appendToFile(f"{output_dir}/LTC.csv", "LTC")
    appendToFile(f"{output_dir}/BCH.csv", "BCH")
    appendToFile(f"{output_dir}/ETC.csv", "ETC")
    appendToFile(f"{output_dir}/BTC.csv", "BTC")
