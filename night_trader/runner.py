import robin_stocks as r
from data_sourcer import DataSourcer

class NightTrader():

    login: dict
    data_source: DataSourcer

    def __init__(self):
        print("---------------------------------- Night Trader ----------------------------------")
        # Load and read username and password env files
        usernameFile = open("env/username", "r")
        username = usernameFile.read()
        passwordFile = open("env/password", "r")
        password = passwordFile.read()

        print("Logging in...", end='')
        self.login = r.login(username, password)
        if not self.login["access_token"]:
            print("FAILURE")
            print("system exiting.")
            r.authentication.logout()
            exit()
        print("done")

        # Create data source object which pulls history on init
        self.data_source = DataSourcer(r)
        self.data_source.getCurrentQuote(r)

    def logout(self):
        # print(r.crypto.get_crypto_positions())
        # log out of robinhood at the end of the session
        r.authentication.logout()

if __name__ == "__main__":
    # execute only if run as a script
    nt = NightTrader()