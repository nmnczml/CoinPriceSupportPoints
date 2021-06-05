import pandas as pd
import numpy as np
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
from binance.client import Client
from datetime import datetime

class ApiKeyPair:
    ApiKey=""
    Secret=""
    
class AvailableCoins:
  
    Pair=""    
 

 
import base64
from Crypto.Cipher import AES

BS = 16
pad = lambda s: bytes(s + (BS - len(s) % BS) * chr(BS - len(s) % BS), 'utf-8')
unpad = lambda s : s[0:-ord(s[-1:])]
class AESCipher:

    def __init__( self, key ):
        self.key = bytes(key, 'utf-8')

    def encrypt( self, raw ):
        raw = pad(raw)
        iv = "9/\~V).A,lY&=t2b".encode('utf-8')
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return base64.b64encode(cipher.encrypt( raw ) )
    
    def decrypt( self, enc ):
        iv = "9/\~V).A,lY&=t2b".encode('utf-8')
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc )).decode('utf8')
    
    
class BinanceConnection:
    def __init__(self, apiKey, secret):
        try:
            self.connect(apiKey, secret)
        except BaseException as error:
            logMeError('An exception occurred: {}'+format(error))

    """ Creates Binance client """

    def connect(self, apiKey, secret):        
        try:
            self.client = Client(apiKey, secret)
        except BaseException as error:
            logMeError('An exception occurred: {}'+format(error))



def logMeError(msg):
    
    print(msg)
    
def isSupport(df,i):
    support = df['Low'][i] < df['Low'][i-1]  and df['Low'][i] < df['Low'][i+1] \
    and df['Low'][i+1] < df['Low'][i+2] and df['Low'][i-1] < df['Low'][i-2]

    return support

def isResistance(df,i):
    resistance = df['High'][i] > df['High'][i-1]  and df['High'][i] > df['High'][i+1] \
    and df['High'][i+1] > df['High'][i+2] and df['High'][i-1] > df['High'][i-2] 

    return resistance




def plot_all(coinName,df,levels):
    fig, ax = plt.subplots()

    candlestick_ohlc(ax,df.values,width=0.6, \
                    colorup='green', colordown='red', alpha=0.8)

    date_format = mpl_dates.DateFormatter('%d %b %Y')
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()

    fig.tight_layout()

    try:
        
        for level in levels:
            plt.hlines(level[1],xmin=df['Date'][level[0]],\
                    xmax=max(df['Date']),colors='blue',label=str(level[1]))
        
        # fig.show()
        plt.legend()
        plt.savefig('./SupportImages/'+coinName+'.pdf')
        plt.close()
    except BaseException as error:
        logMeError('An exception occurred: '+format(error))   
         
     
    
 
def isFarFromLevel(l,s,levels):
    return np.sum([abs(l-x) < s  for x in levels]) == 0

def getApiKey():
    try:
        cipher = AESCipher("qwr{@^h`h&_`50/ja9!'dcmh3!uw<&=?")
         
        with open('config.txt', 'r') as config:
            config_values = config.readlines()

        apiKey, secret = read_config(config_values)

        inApiKey= ApiKeyPair() 
        inApiKey.ApiKey =  cipher.decrypt(apiKey)
        inApiKey.Secret =  cipher.decrypt(secret)
        
        return inApiKey
    except BaseException as error:
        logMeError('An exception occurred: {}'+format(error))   
    
def parse_line(line):
    delim_loc = line.find(':')
    return line[delim_loc+1:].strip()

def read_config(config_string):
    apiKey = parse_line(config_string[0])
    secret = parse_line(config_string[1])
    return  apiKey, secret 
 
 
def getAvailablePairs():
    try:
          
        with open('coins.txt', 'r') as coinList:
            coins = coinList.readlines()
        
        
        marketPairs = []
        for row in coins:
            inPair= AvailableCoins()  
 
            inPair.Pair = row.strip()
            marketPairs.append(inPair)
        return marketPairs
           
    except BaseException as error:
        logMeError('An exception occurred:'+format(error))   
 
      
 

def jobDef():
    try:
        plt.rcParams['figure.figsize'] = [12, 7]

        plt.rc('font', size=14)

        apiKey = getApiKey()
        connection = BinanceConnection(apiKey.ApiKey, apiKey.Secret)

        marketPairs = getAvailablePairs()
        
        for coin in marketPairs:
            try:
                klines = connection.client.get_klines(symbol=coin.Pair, interval="1d", limit=50)
                column_names = ['Date',   'Open', 'High', 'Low', 'Close']

                df = pd.DataFrame(columns = column_names)
            
                open_time = [int(entry[0]) for entry in klines]

                open = [float(entry[1]) for entry in klines]
                high = [float(entry[2]) for entry in klines]
                low = [float(entry[3]) for entry in klines]
                close = [float(entry[4]) for entry in klines]
                
                last_closing_price = close[-1]

            
                df['Date'] =   pd.to_datetime(open_time, unit='ms')
                df['Open'] = open
                df['High'] = high
                df['Low'] = low
                df['Close'] = close
            
                df['Date'] = df['Date'].apply(mpl_dates.date2num)
            
                df = df.loc[:,['Date', 'Open', 'High', 'Low', 'Close']]
            
                s =  np.mean(df['High'] - df['Low'])


                levels = []
                for i in range(2,df.shape[0]-2):
                    if isSupport(df,i):
                        l = df['Low'][i]

                        if isFarFromLevel(l,s,levels):
                            levels.append((i,l))

                    elif isResistance(df,i):
                        l = df['High'][i]

                        if isFarFromLevel(l,s,levels):
                            levels.append((i,l))
            
                
                
        
                    
                print('#'+coin.Pair,', lastClosingPrice:'+str(last_closing_price)
                    +', levels:'+str(levels))
                plot_all(coin.Pair,df,levels)
            except BaseException as error:
                logMeError('An exception occurred: '+format(error))  
        
        
                
    except BaseException as error:
        logMeError('An exception occurred: '+format(error))  
        
#run setup and copy/paste values inside quotes to config.txt
def setup():
        
    cipher = AESCipher("qwr{@^h`h&_`50/ja9!'dcmh3!uw<&=?")
    apiKey = 'yourApiKey'
    secret = 'yourSecret'
    print(cipher.encrypt(apiKey))
    print(cipher.encrypt(secret))
 
if __name__ == '__main__':
    
    jobDef()
  
