import os
import sys
from pathlib import Path
import time
# Add the project directory to the sys.path
project_dir = str(Path(__file__).resolve().parents[2])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from dotenv import load_dotenv
load_dotenv()
import aiohttp
import pandas as pd
from pytz import timezone
from .webull_helpers import calculate_countdown, calculate_setup

from .trade_models.capital_flow import CapitalFlow
from .trade_models.cost_distribution import CostDistribution
from .trade_models.etf_holdings import ETFHoldings
from .trade_models.institutional_holdings import InstitutionHolding, InstitutionStat
from .trade_models.financials import BalanceSheet, FinancialStatement, CashFlow
from .trade_models.news import NewsItem
from .trade_models.forecast_evaluator import ForecastEvaluator
from .trade_models.short_interest import ShortInterest
from .trade_models.volume_analysis import WebullVolAnalysis
from .trade_models.ticker_query import WebullStockData, MultiQuote
from .trade_models.analyst_ratings import Analysis

import asyncio

from datetime import datetime, timedelta

class WebullTrading:
    def __init__(self):
        self.most_active_tickers= ['SNOW', 'IBM', 'DKNG', 'SLV', 'NWL', 'SPXS', 'DIA', 'QCOM', 'CMG', 'WYNN', 'PENN', 'HLF', 'CCJ', 'WW', 'NEM', 'MOS', 'SRPT', 'MS', 'DPST', 'AG', 'PAA', 'PANW', 'XPEV', 'BHC', 'KSS', 'XLP', 'LLY', 'MDB', 'AZN', 'NVO', 'BOIL', 'ZM', 'HUT', 'VIX', 'PDD', 'SLB', 'PCG', 'DIS', 'TFC', 'SIRI', 'TDOC', 'CRSP', 'BSX', 'BITF', 'AAL', 'EOSE', 'RIVN', 'X', 'CCL', 'SOXS', 'NOVA', 'TMUS', 'HES', 'LI', 'NVAX', 'TSM', 'CNC', 'IAU', 'GDDY', 'CVX', 'TGT', 'MCD', 'GDXJ', 'AAPL', 'NKLA', 'EDR', 'NOK', 'SPWR', 'NKE', 'HYG', 'FSLR', 'SGEN', 'DNN', 'BAX', 'CRWD', 'OSTK', 'XLC', 'RIG', 'SEDG', 'SNDL', 'RSP', 'M', 'CD', 'UNG', 'LQD', 'TTD', 'AMGN', 'EQT', 'YINN', 'MULN', 'FTNT', 'WBD', 'MRNA', 'PTON', 'SCHW', 'ABNB', 'EW', 'PM', 'UCO', 'TXN', 'DLR', 'KHC', 'MMAT', 'QQQ', 'GOOGL', 'AEM', 'RTX', 'AVGO', 'RBLX', 'PAAS', 'UUP', 'OXY', 'SQ', 'PLUG', 'CLF', 'GOEV', 'BKLN', 'ALB', 'BALL', 'SMH', 'CVE', 'F', 'KRE', 'TWLO', 'ARCC', 'ARM', 'U', 'SOFI', 'SBUX', 'FXI', 'BMY', 'HSBC', 'EFA', 'SVXY', 'VALE', 'GOLD', 'MSFT', 'OIH', 'ARKK', 'AMD', 'AA', 'DXCM', 'ABT', 'WOLF', 'FDX', 'SOXL', 'MA', 'KWEB', 'BP', 'SNAP', 'NLY', 'KGC', 'URA', 'UVIX', 'KMI', 'ACB', 'NET', 'W', 'GRAB', 'LMT', 'EPD', 'FCX', 'STNE', 'NIO', 'SU', 'ET', 'CVS', 'ADBE', 'MXL', 'HOOD', 'FUBO', 'RIOT', 'CRM', 'TNA', 'DISH', 'XBI', 'VFS', 'GPS', 'NVDA', 'MGM', 'MRK', 'ABBV', 'LABU', 'BEKE', 'VRT', 'LVS', 'CPNG', 'BA', 'MTCH', 'PEP', 'EBAY', 'GDX', 'XLV', 'UBER', 'GOOG', 'COF', 'XLU', 'BILI', 'XLK', 'VXX', 'DVN', 'MSOS', 'KOLD', 'XOM', 'BKNG', 'SPY', 'RUT', 'CMCSA', 'STLA', 'NCLH', 'GRPN', 'ZION', 'UAL', 'GM', 'NDX', 'TQQQ', 'COIN', 'WBA', 'CLSK', 'NFLX', 'FREY', 'AFRM', 'NAT', 'EEM', 'IYR', 'KEY', 'OPEN', 'DM', 'TSLA', 'BXMT', 'T', 'TZA', 'BAC', 'MARA', 'UVXY', 'LOW', 'COST', 'HL', 'CHTR', 'TMF', 'ROKU', 'DOCU', 'PSEC', 'XHB', 'VMW', 'SABR', 'USB', 'DDOG', 'DB', 'V', 'NOW', 'XRT', 'SMCI', 'PFE', 'NYCB', 'BIDU', 'C', 'SPX', 'ETSY', 'EMB', 'SQQQ', 'CHPT', 'DASH', 'VZ', 'DNA', 'CL', 'ANET', 'WMT', 'MRO', 'WFC', 'MO', 'USO', 'ENVX', 'INTC', 'GEO', 'VFC', 'WE', 'MET', 'CHWY', 'PBR', 'KO', 'TH', 'QS', 'BTU', 'GLD', 'JD', 'XLY', 'KR', 'ASTS', 'WDC', 'HTZ', 'XLF', 'COP', 'PATH', 'SHEL', 'MXEF', 'SE', 'SPCE', 'UPS', 'RUN', 'DOW', 'ASHR', 'ONON', 'DAL', 'SPXL', 'SAVE', 'LUV', 'HD', 'JNJ', 'LYFT', 'UNH', 'BBY', 'CZR', 'NEE', 'STNG', 'SPXU', 'MMM', 'VNQ', 'IMGN', 'MSTR', 'AXP', 'TMO', 'XPO', 'FEZ', 'ENPH', 'AX', 'NVCR', 'GS', 'MRVL', 'ADM', 'GILD', 'IBB', 'FTCH', 'PARA', 'PINS', 'JBLU', 'SNY', 'BITO', 'PYPL', 'FAS', 'GME', 'LAZR', 'URNM', 'BX', 'MPW', 'UPRO', 'HPQ', 'AMZN', 'SAVA', 'TLT', 'ON', 'CAT', 'VLO', 'AR', 'IDXX', 'SWN', 'META', 'BABA', 'ZS', 'EWZ', 'ORCL', 'XOP', 'TJX', 'XP', 'EL', 'HAL', 'IEF', 'XLI', 'UPST', 'Z', 'TELL', 'LRCX', 'DLTR', 'BYND', 'PACW', 'CVNA', 'GSAT', 'CSCO', 'NU', 'KVUE', 'JPM', 'LCID', 'TLRY', 'AGNC', 'CGC', 'XLE', 'VOD', 'TEVA', 'JETS', 'UEC', 'FSR', 'ZIM', 'ABR', 'IQ', 'AMC', 'ALLY', 'HE', 'OKTA', 'ACN', 'MU', 'FLEX', 'SHOP', 'PLTR', 'CLX', 'LUMN', 'WHR', 'PAGP', 'IWM', 'WPM', 'TTWO', 'AI', 'ALGN', 'SPOT', 'BTG', 'IONQ', 'GE', 'DG', 'AMAT', 'XSP', 'PG', 'LULU', 'DE', 'MDT', 'RCL']
        self.scalar_tickers = ['SPX', 'VIX', 'OSTK', 'XSP', 'NDX', 'MXEF']
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        self.tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        self.thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        self.thirty_days_from_now = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        self.fifteen_days_ago = (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')
        self.fifteen_days_from_now = (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')
        self.eight_days_from_now = (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d')
        self.eight_days_ago = (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d')
        self.timeframes = ['m1','m5', 'm10', 'm15', 'm20', 'm30', 'm60', 'm120', 'm240', 'd1']

        self.headers = {
        "Access_token": os.environ.get('ACCESS_TOKEN'),
        "App": "global",
        "App-Group": "broker",
        "Appid": "wb_web_app",
        "Content-Type": "application/json",
        "Device-Type": "Web",
        "Did": os.environ.get('DID'),
        "Hl": "en",
        "Locale": "eng",
        "Os": "web",
        "Osv": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Ph": "Windows Chrome",
        "Platform": "web",
        "Referer": "https://app.webull.com/",
    }
    async def fetch_endpoint(self, endpoint):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(endpoint) as resp:
                return await resp.json()

    async def get_ticker_id(self, symbol):
        """Converts ticker name to ticker ID to be passed to other API endpoints from Webull."""
        endpoint =f"https://quotes-gw.webullfintech.com/api/search/pc/tickers?keyword={symbol}&pageIndex=1&pageSize=1"

        
        data =  await self.fetch_endpoint(endpoint)
        datas = data['data'] if 'data' in data else None
        if datas is not None:
            tickerID = datas[0]['tickerId']
            return tickerID
    

    async def get_bars(self, symbol, timeframe:str='m1'):
        """
        Timeframes:
        
        >>> m1: 1 minute
        >>> m5: 5 minute
        >>> m10: 10 minute
        >>> m15: 15 minute
        >>> m20: 20 minute
        >>> m30: 30 minute
        >>> m60: 1 hour
        >>> m120: 2 hour
        >>> m240: 4 hour
        
        """
        tickerid = await self.get_ticker_id(symbol)
        endpoint = f"https://quotes-gw.webullfintech.com/api/quote/charts/query?tickerIds={tickerid}&type={timeframe}&count=800&extendTrading=0"
        datas =  await self.fetch_endpoint(endpoint)
        if datas is not None:
            data = datas[0]['data']
            # Create empty lists for each column
            timestamps = []
            column2 = []
            column3 = []
            column4 = []
            column5 = []
            column6 = []

            # Split each line and append values to respective lists
            for line in data:
                parts = line.split(',')
                timestamps.append(parts[0])
                column2.append(parts[1])
                column3.append(parts[2])
                column4.append(parts[3])
                column5.append(parts[4])
                column6.append(parts[5])

  

            df = pd.DataFrame({
                'Timestamp': timestamps,
                'Open': column2,
                'Low': column3,
                'High': column4,
                'Close': column5,
                'Vwap': column6
            })

            # Convert the 'Timestamp' column to integers before converting to datetime
            df['Timestamp'] = df['Timestamp'].astype(int)

            # Then convert to datetime
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')


            # Convert to Eastern Time
            eastern = timezone('US/Eastern')
            df['Timestamp'] = df['Timestamp'].dt.tz_localize('UTC').dt.tz_convert(eastern)

            # Remove the timezone information
            df['Timestamp'] = df['Timestamp'].dt.tz_localize(None)
            df['Timeframe'] = timeframe
            df['Ticker'] = symbol
  
            return df
        


    async def get_stock_quote(self, symbol:str):
        if symbol == 'SPX':
            symbol == 'SPXW'
        ticker_id = await self.get_ticker_id(symbol)

        endpoint = f"https://quotes-gw.webullfintech.com/api/stock/tickerRealTime/getQuote?tickerId={ticker_id}&includeSecu=1&includeQuote=1&more=1"
        print(endpoint)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint) as resp:
                    r = await resp.json()

                    #data = WebullStockData(r)
                    try:

                        df = pd.DataFrame(r)
                        df = df.drop(columns=['secType', 'exchangeId', 'regionId', 'regionCode'])
                        return df
                    except Exception as e:
                        print(f"{e} | Attempting to use an index of 0...")
                        try:
                            df = pd.DataFrame(r, index=[0])
                            
                        except Exception as e:
                            print(f"Second attempt failed for {symbol}: {e}")
                        try:
                            df = df.drop(columns=['secType', 'exchangeId', 'regionId', 'regionCode'])
                            
                            return df
                        except Exception as e:
                            print(f'Giving up...{symbol}: {e}')
        except Exception as e:
            return f"Failed for {e}"


    async def get_analyst_ratings(self, symbol:str):
        ticker_id = await self.get_ticker_id(symbol)
        endpoint=f"https://quotes-gw.webullfintech.com/api/information/securities/analysis?tickerId={ticker_id}"
        datas = await self.fetch_endpoint(endpoint)
        data = Analysis(datas)
        return data
    

    async def get_short_interest(self, symbol:str):
        ticker_id = await self.get_ticker_id(symbol)
        endpoint = f"https://quotes-gw.webullfintech.com/api/information/brief/shortInterest?tickerId={ticker_id}"
        datas = await self.fetch_endpoint(endpoint)
        data = ShortInterest(datas)
        return data
    
    async def institutional_holding(self, symbol:str):
        ticker_id = await self.get_ticker_id(symbol)
        endpoint = f"https://quotes-gw.webullfintech.com/api/information/stock/getInstitutionalHolding?tickerId={ticker_id}"
        datas = await self.fetch_endpoint(endpoint)
        data = InstitutionStat(datas)

        return data
    

    async def volume_analysis(self, symbol:str):
        ticker_id = await self.get_ticker_id(symbol)
        endpoint = f"https://quotes-gw.webullfintech.com/api/stock/capitalflow/stat?count=10&tickerId={ticker_id}&type=0"
        datas = await self.fetch_endpoint(endpoint)
        data = WebullVolAnalysis(datas)
        return data
    

    async def cost_distribution(self, symbol:str, start_date:str=None, end_date:str=None):

        if start_date is None:
            start_date = self.yesterday
            

        if end_date is None:
            end_date = self.today

        ticker_id = await self.get_ticker_id(symbol)
        endpoint = f"https://quotes-gw.webullfintech.com/api/quotes/chip/query?tickerId={ticker_id}&startDate={start_date}&endDate={end_date}"
 
        datas = await self.fetch_endpoint(endpoint)
        data = CostDistribution(datas)
        return data
    

    async def stock_quote(self, symbol:str):
        ticker_id = await self.get_ticker_id(symbol)
        endpoint = f"https://quotes-gw.webullfintech.com/api/bgw/quote/realtime?ids={ticker_id}&includeSecu=1&delay=0&more=1"
        datas = await self.fetch_endpoint(endpoint)
        data = WebullStockData(datas)
        return data
    

    async def news(self, symbol:str, pageSize:str='100'):
        ticker_id = await self.get_ticker_id(symbol)
        endpoint = f"https://nacomm.webullfintech.com/api/information/news/tickerNews?tickerId={ticker_id}&currentNewsId=0&pageSize={pageSize}"
        datas = await self.fetch_endpoint(endpoint)
        data = NewsItem(datas)
        return data
    

    async def balance_sheet(self, symbol:str, limit:str='11'):
        ticker_id = await self.get_ticker_id(symbol)
        endpoint = f"https://quotes-gw.webullfintech.com/api/information/financial/balancesheet?tickerId={ticker_id}&type=101&fiscalPeriod=0&limit={limit}"
        datas = await self.fetch_endpoint(endpoint)
        data = BalanceSheet(datas)
        return data
    
    async def cash_flow(self, symbol:str, limit:str='12'):
        ticker_id = await self.get_ticker_id(symbol)
        endpoint = f"https://quotes-gw.webullfintech.com/api/information/financial/cashflow?tickerId={ticker_id}&type=102&fiscalPeriod=1,2,3,4&limit={limit}"
        datas = await self.fetch_endpoint(endpoint)
        data = CashFlow(datas)
        return data
    
    async def income_statement(self, symbol:str, limit:str='12'):
        ticker_id = await self.get_ticker_id(symbol)
        endpoint = f"https://quotes-gw.webullfintech.com/api/information/financial/incomestatement?tickerId={ticker_id}&type=102&fiscalPeriod=1,2,3,4&limit={limit}"
        datas = await self.fetch_endpoint(endpoint)
        data = FinancialStatement(datas)
        return data
    



    async def capital_flow(self, symbol:str):
        ticker_id = await self.get_ticker_id(symbol)
        endpoint = f"https://quotes-gw.webullfintech.com/api/stock/capitalflow/ticker?tickerId={ticker_id}&showHis=true"
        datas = await self.fetch_endpoint(endpoint)
        data = CapitalFlow(datas)
        return data
    

    async def etf_holdings(self, symbol:str, pageSize:str='200'):
        ticker_id = await self.get_ticker_id(symbol)
        endpoint = f"https://quotes-gw.webullfintech.com/api/information/company/queryEtfList?tickerId={ticker_id}&pageIndex=1&pageSize={pageSize}"
        datas = await self.fetch_endpoint(endpoint)
        data = ETFHoldings(datas)
        return data
    

    async def multi_quote(self, symbols:str):
        counter = 0
        while True:
            counter = counter + 1
           
            ticker_ids = [await self.get_ticker_id(i) for i in symbols]
            ticker_ids = str(ticker_ids)
            ticker_ids = ','.join([ticker_ids]).replace(']', '').replace('[', '').replace(' ', '')
            endpoint = f"https://quotes-gw.webullfintech.com/api/bgw/quote/realtime?ids={ticker_ids}&includeSecu=1&delay=0&more=1"

            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(endpoint) as resp:
                    datas = await resp.json()
                    all_data = MultiQuote(datas)

                    for sym,price, vol, vr in zip(all_data.symbol, all_data.close, all_data.volume, all_data.vibrateRatio):
                        yield(f'SYM(1): | {sym} | PRICE(3): | {price} | VOL:(5): | {vol} | VIBRATION:(7): | {vr}')

                        if counter == 250:
                            print(f"Stream ending...")
                        
                            break


    async def async_get_td9(self, ticker, interval):
        timeStamp = None
        if ticker == 'I:SPX':
            ticker = 'SPXW'
        elif ticker =='I:NDX':
            ticker = 'NDX'
        elif ticker =='I:VIX':
            ticker = 'VIX'
        
        tickerid = await self.get_ticker_id(ticker)




        if timeStamp is None:
            # if not set, default to current time
            timeStamp = int(time.time())

        base_fintech_gw_url = f'https://quotes-gw.webullfintech.com/api/quote/charts/query?tickerIds={tickerid}&type={interval}&count=300&timestamp={timeStamp}&extendTrading=1'



        if interval == 'm1':
            timespan = 'minute'
        elif interval == 'm60':
            timespan = 'hour'
        elif interval == 'm20':
            timespan = 'hour'
        elif interval == 'm5':
            timespan = 'hour'
        elif interval == 'm15':
            timespan = 'hour'
        elif interval == 'm30':
            timespan = 'hour'
        elif interval == 'm120':
            timespan = 'day'
        elif interval == 'm240':
            timespan = 'day'
        elif interval == 'd1':
            timespan = 'day'
        elif interval == 'w':
            timespan = 'week'
        elif interval == 'm':
            timespan = 'month'
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(base_fintech_gw_url) as resp:
                r = await resp.json()
                try:
                    # Check if the data is present and the expected structure is correct
                    if r and isinstance(r, list) and 'data' in r[0]:
                        data = r[0]['data']

                        data = r[0]['data']
                        if data is not None:
                            parsed_data = []
                            for entry in data:
                                values = entry.split(',')
                                if values[-1] == 'NULL':
                                    values = values[:-1]
                                elif values[-1] == 'NULL':
                                    values = values[:-1]  # remove the last element if it's 'NULL'
                                parsed_data.append([float(value) if value != 'null' else 0.0 for value in values])
                            try:
                                sorted_data = sorted(parsed_data, key=lambda x: x[0], reverse=True)
                                
                                # Dynamically assign columns based on the length of the first entry
                                columns = ['Timestamp', 'Open', 'Close', 'High', 'Low', 'N', 'Volume', 'Vwap'][:len(sorted_data[0])]
                                
                                df = pd.DataFrame(sorted_data, columns=columns)
                                # Convert the Unix timestamps to datetime objects in UTC first
                                df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s', utc=True)

                                # Convert UTC to Eastern Time (ET)
                                df['Timestamp'] = df['Timestamp'].dt.tz_convert('US/Eastern')
                                df['Timestamp'] = df['Timestamp'].dt.tz_localize(None)
                                df['Ticker'] = ticker
                                df['timespan'] = interval


                                df['ticker'] = ticker

                                
                                td9_df = df.head(13)

                                setup_phase = calculate_setup(td9_df)
                                countdown_phase = calculate_countdown(td9_df)

                                df = df.head(13)
                                df = df.iloc[::-1].reset_index(drop=True)
                                td9_state = "Setup Complete" if setup_phase else "Countdown Complete" if countdown_phase else "Not in TD9 State"  

                                if td9_state in ['Setup Complete', 'Countdown Complete']:
                                    return ticker, td9_state, timespan
                                else:
                                    return None
                            except Exception as e:
                                print(f'error - finished scan?')

                                                
                                        
                    else:
                        # Handle the case where the data is not in the expected format
                        print(f"No data available for {ticker} or unexpected response format.")
                        return None
                except KeyError as e:
                    # Log the error
                    print(f"KeyError encountered while processing {ticker}: {e}")
                    return None


    async def async_scan_td9(self, symbol, interval):
        try:
            td9_state = await self.async_get_td9(symbol, interval=interval)
            return symbol, td9_state
        except Exception as e:
            # Handle exceptions, you might want to log this
            print(f"Error processing {symbol}: {e}")
            return symbol, None
        
    async def async_get_all_td9_for_timespan(self, interval):
        tickers = self.most_active_tickers  # Ensure this is a list of ticker symbols
        results = []

        async def get_td9_for_symbol(symbol):
            try:
                _, td9_state = await self.async_scan_td9(symbol, interval)
                if td9_state is not None:
                    return (symbol, td9_state, interval)
            except Exception as e:
                print(f"Error retrieving result for {symbol}: {e}")
            return None

        tasks = [get_td9_for_symbol(symbol) for symbol in tickers]
        completed_tasks = await asyncio.gather(*tasks)

        for task_result in completed_tasks:
            if task_result is not None:
                results.append(task_result)

        return results