
class DataSourcer:

    CRYPTO = 'ETH'

    eth_history = {}

    def __init__(self, r):
        print("Gathering historical data...", end='')
        self.eth_history = r.crypto.get_crypto_historicals(self.CRYPTO, interval='5minute', span='week', bounds='24_7', info=None) #TODO change to 15second
        if not self.eth_history:
            print("Error in loading history data, system exiting.")
            exit()
        else:
            print("done")
        return
    
    def getCurrentQuote(self, r):
        print(r.crypto.get_crypto_quote(self.CRYPTO, info=None))
        print("waiting now")


