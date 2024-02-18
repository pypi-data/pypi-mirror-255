


import os
import pandas as pd
from asyncio import Lock
lock = Lock()
from dotenv import load_dotenv
load_dotenv()
# Assuming we have the array of ticker IDs as numpy arrays from the user's environment
import numpy as np
from aiohttp.client_exceptions import ContentTypeError
from .options import WebullOptionsData, VolumeAnalysis
from .webull_trading import WebullTrading
from . import batch_insert_dataframe
import aiohttp
import asyncio
import json
import asyncpg
from ..helpers import get_human_readable_string
GEX_KEY = os.environ.get('GEXBOT')
def convert_to_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        # Handle the error or return None if the string cannot be converted
        return 
print(GEX_KEY)


from .webull_trading import WebullTrading
from datetime import datetime, timedelta

trading = WebullTrading()

class WebullOptions:
    def __init__(self, host, port, user, database, password):
        self.pool = None
        self.most_active_tickers = ['NAT', 'MOS', 'XHB', 'FUBO', 'AI', 'U', 'CHWY', 'HD', 'SIRI', 'XSP', 'BYND', 'HUT', 'DPST', 'SVXY', 'T', 'SEDG', 'ARCC', 'EMB', 'IEF', 'NEM', 'IBM', 'DNN', 'XLU', 'EEM', 'BBY', 'SNY', 'LLY', 'WYNN', 'XLY', 'PG', 'CVNA', 'SPWR', 'NKLA', 'WDC', 'CRM', 'NCLH', 'ALB', 'SCHW', 'DAL', 'NFLX', 'BITF', 'ALLY', 'CRWD', 'DOCU', 'PAA', 'VFS', 'V', 'AFRM', 'CSCO', 'TZA', 'PACW', 'VMW', 'MMAT', 'JNJ', 'MA', 'STNG', 'PAAS', 'OXY', 'SMCI', 'FREY', 'ADM', 'HYG', 'XBI', 'TDOC', 'DIA', 'SOXL', 'DLR', 'TLRY', 'EOSE', 'SLV', 'DXCM', 'MU', 'TMF', 'PM', 'SNAP', 'IAU', 'ZIM', 'ROKU', 'ADBE', 'SOXS', 'NEE', 'GSAT', 'NVAX', 'WW', 'UVXY', 'DB', 'Z', 'JETS', 'WE', 'AMAT', 'XLV', 'DISH', 'CHTR', 'GRPN', 'TH', 'PATH', 'SBUX', 'GDXJ', 'XLF', 'NOK', 'FXI', 'AXP', 'NDX', 'SAVE', 'MDT', 'SRPT', 'CCJ', 'RIOT', 'QCOM', 'ABR', 'BITO', 'LOW', 'ARKK', 'MXL', 'HES', 'STNE', 'RCL', 'MDB', 'KVUE', 'ZION', 'TXN', 'BTU', 'HAL', 'WPM', 'TNA', 'AAL', 'WOLF', 'VIX', 'KOLD', 'KMI', 'SABR', 'UPS', 'GPS', 'EFA', 'AMZN', 'HTZ', 'TELL', 'XPEV', 'SPY', 'CAT', 'GDDY', 'TQQQ', 'SPCE', 'PDD', 'GME', 'W', 'GRAB', 'AMGN', 'TTWO', 'OSTK', 'BMY', 'DVN', 'MCD', 'HPQ', 'BKNG', 'UPRO', 'KR', 'TFC', 'NYCB', 'CHPT', 'QS', 'XLC', 'LUV', 'OIH', 'DKNG', 'SPXU', 'BALL', 'FTNT', 'MET', 'STLA', 'NIO', 'AA', 'RIVN', 'LQD', 'KEY', 'BILI', 'SU', 'SNOW', 'SPX', 'GDX', 'NKE', 'CD', 'CPNG', 'MXEF', 'LUMN', 'SLB', 'COIN', 'OPEN', 'IQ', 'UBER', 'VALE', 'ASHR', 'PAGP', 'BSX', 'KWEB', 'BX', 'TEVA', 'BKLN', 'COP', 'IYR', 'MO', 'SQQQ', 'ANET', 'BHC', 'EBAY', 'AMD', 'PANW', 'GOOG', 'ON', 'SOFI', 'RUN', 'XOM', 'QQQ', 'HL', 'ABNB', 'MSOS', 'YINN', 'OKTA', 'XLI', 'EL', 'USB', 'CCL', 'COST', 'CMCSA', 'JPM', 'CVS', 'ARM', 'TGT', 'UNG', 'LABU', 'FDX', 'CRSP', 'GOLD', 'CL', 'ABT', 'NVO', 'MRVL', 'SGEN', 'ET', 'ENVX', 'BXMT', 'ABBV', 'AR', 'KRE', 'JBLU', 'UAL', 'NOVA', 'NET', 'SHOP', 'CVE', 'NVDA', 'PINS', 'EPD', 'LRCX', 'UEC', 'NWL', 'GOEV', 'GS', 'CGC', 'FSR', 'PENN', 'GM', 'UPST', 'LVS', 'BA', 'EDR', 'MARA', 'VNQ', 'XLP', 'F', 'DM', 'XRT', 'CNC', 'FTCH', 'IDXX', 'MPW', 'ETSY', 'GOOGL', 'CLX', 'NOW', 'MRK', 'SE', 'SMH', 'CLF', 'MULN', 'MRO', 'HSBC', 'DG', 'HE', 'GLD', 'MRNA', 'USO', 'XLK', 'DNA', 'SHEL', 'SPXS', 'LAZR', 'CLSK', 'NVCR', 'IBB', 'META', 'PYPL', 'RIG', 'ALGN', 'AVGO', 'FEZ', 'AX', 'FLEX', 'VRT', 'WFC', 'BOIL', 'ZS', 'GILD', 'ASTS', 'KSS', 'TWLO', 'CVX', 'TMO', 'MSTR', 'XP', 'SPXL', 'DLTR', 'BEKE', 'C', 'DDOG', 'GE', 'WMT', 'WHR', 'TJX', 'M', 'BAC', 'TLT', 'FAS', 'SAVA', 'UUP', 'KGC', 'BIDU', 'URNM', 'MGM', 'FCX', 'X', 'RSP', 'PLTR', 'PLUG', 'LMT', 'ZM', 'PCG', 'PFE', 'DOW', 'LCID', 'EQT', 'WBA', 'NU', 'CMG', 'INTC', 'ENPH', 'PTON', 'BAX', 'AG', 'VXX', 'TSLA', 'AZN', 'UNH', 'BABA', 'MMM', 'UVIX', 'VLO', 'FSLR', 'EWZ', 'PBR', 'JD', 'KHC', 'RBLX', 'MS', 'LI', 'XLE', 'SNDL', 'AEM', 'VOD', 'HOOD', 'MTCH', 'SPOT', 'LYFT', 'KO', 'PEP', 'RUT', 'DIS', 'RTX', 'IMGN', 'AGNC', 'MSFT', 'ACN', 'XPO', 'ACB', 'SWN', 'ORCL', 'VZ', 'COF', 'PSEC', 'AAPL', 'NLY', 'GEO', 'CZR', 'IONQ', 'WBD', 'XOP', 'AMC', 'BP', 'DE', 'PARA', 'URA', 'LULU', 'EW', 'DASH', 'IWM', 'ONON', 'TTD', 'TSM', 'VFC', 'BTG', 'TMUS', 'SQ', 'HLF', 'UCO']
        self.most_active_tickers = set(self.most_active_tickers)
        self.host=host
        self.port=port
        self.database=database
        self.user=user
        self.password=password
        self.gex_tickers = ['SPY','SPX','QQQ','AAPL','TSLA','MSFT','AMZN','NVDA']
        self.as_dataframe = None
        self.api_key = os.environ.get('YOUR_POLYGON_KEY')
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        self.tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        self.thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        self.thirty_days_from_now = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        self.fifteen_days_ago = (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')
        self.fifteen_days_from_now = (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')
        self.eight_days_from_now = (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d')
        self.eight_days_ago = (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d')
        self.headers = {
        "Access_token": os.environ.get('ACCESS_TOKEN'),
        "Accept": "*/*",
        "App": "global",
        "App-Group": "broker",
        "Appid": "wb_web_app",
        "Content-Type": "application/json;charset=UTF-8",
        "Device-Type": "Web",
        "Did": os.environ.get('DID'),
        "Hl": "en",
        "Locale": "eng",
        "Os": "web",
        "Osv": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    }


    async def connect(self):
        self.pool = await asyncpg.create_pool(
            host=self.host,password=self.password,database=self.database,user=self.user,port=self.port, min_size=1, max_size=100
        )

    async def create_table(self, df, table_name):
        print("Connected to the database.")
        dtype_mapping = {
            'int64': 'BIGINT',
            'float64': 'DOUBLE PRECISION',
            'object': 'TEXT',
            'bool': 'BOOLEAN',
            'datetime.date': 'TIMESTAMP',
            'datetime.datetime': 'TIMESTAMP',
            'datetime64[ns]': 'timestamp',
            'datetime64[ms]': 'timestamp',
            'datetime64[ns, US/Eastern]': 'TIMESTAMP WITH TIME ZONE',
            'string': 'TEXT'
        }


        # Check for large integers and update dtype_mapping accordingly
        for col, dtype in zip(df.columns, df.dtypes):
            if dtype == 'int64':
                max_val = df[col].max()
                min_val = df[col].min()
                if max_val > 2**31 - 1 or min_val < -2**31:
                    dtype_mapping['int64'] = 'BIGINT'
        history_table_name = f"{table_name}_history"
        async with self.pool.acquire() as connection:

            table_exists = await connection.fetchval(f"SELECT to_regclass('{table_name}')")
            
            if table_exists is None:
                create_query = f"""
                CREATE TABLE {table_name} (
                    {', '.join(f'"{col}" {dtype_mapping[str(dtype)]}' for col, dtype in zip(df.columns, df.dtypes))}
                )
                """

                print(f"Creating table with query: {create_query}")

                # Create the history table
                history_create_query = f"""
                CREATE TABLE IF NOT EXISTS {history_table_name} (
                    id serial PRIMARY KEY,
                    operation CHAR(1) NOT NULL,
                    changed_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
                    {', '.join(f'"{col}" {dtype_mapping[str(dtype)]}' for col, dtype in zip(df.columns, df.dtypes))}
                );
                """
                print(f"Creating history table with query: {history_create_query}")
                await connection.execute(history_create_query)
                try:
                    await connection.execute(create_query)
                    print(f"Table {table_name} created successfully.")
                except asyncpg.UniqueViolationError as e:
                    print(f"Unique violation error: {e}")
            else:
                print(f"Table {table_name} already exists.")
            
            # Create the trigger function
            trigger_function_query = f"""
            CREATE OR REPLACE FUNCTION save_to_{history_table_name}()
            RETURNS TRIGGER AS $$
            BEGIN
                INSERT INTO {history_table_name} (operation, changed_at, {', '.join(f'"{col}"' for col in df.columns)})
                VALUES (
                    CASE
                        WHEN (TG_OP = 'DELETE') THEN 'D'
                        WHEN (TG_OP = 'UPDATE') THEN 'U'
                        ELSE 'I'
                    END,
                    current_timestamp,
                    {', '.join('OLD.' + f'"{col}"' for col in df.columns)}
                );
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """
            await connection.execute(trigger_function_query)

            # Create the trigger
            trigger_query = f"""
            DROP TRIGGER IF EXISTS tr_{history_table_name} ON {table_name};
            CREATE TRIGGER tr_{history_table_name}
            AFTER UPDATE OR DELETE ON {table_name}
            FOR EACH ROW EXECUTE FUNCTION save_to_{history_table_name}();
            """
            await connection.execute(trigger_query)


            # Alter existing table to add any missing columns
            for col, dtype in zip(df.columns, df.dtypes):
                alter_query = f"""
                DO $$
                BEGIN
                    BEGIN
                        ALTER TABLE {table_name} ADD COLUMN "{col}" {dtype_mapping[str(dtype)]};
                    EXCEPTION
                        WHEN duplicate_column THEN
                        NULL;
                    END;
                END $$;
                """
                await connection.execute(alter_query)

    async def fetch(self, query, *args):
        """
        Fetch data from the database using the provided SQL query.

        :param query: The SQL query to execute.
        :param args: The arguments to pass to the SQL query.
        :return: The result of the query as a list of records.
        """
        async with self.pool.acquire() as conn:  # Acquire a connection from the pool
            # Execute the query with the provided arguments
            return await conn.fetch(query, *args)


    async def batch_insert_options(self, pairs):
        try:
            await self.connect()
            async with self.pool.acquire() as conn:  # Acquire a connection from the pool

                async with conn.transaction():  # Start a transaction
                    # Prepare the statement to insert data
                    insert_query = 'INSERT INTO wb_opts (symbol, ticker_id, ticker) VALUES ($1, $2, $3)'
                    # Perform the batch insert
                    await conn.executemany(insert_query, pairs)
                    print("Batch insert completed.")
        except asyncpg.exceptions.UniqueViolationError:
            print(f'Duplicate found - skipping.')


    async def yield_batch_ids(self, ticker_symbol):
   
        async with self.pool.acquire() as conn:
            # We will fetch all derivative IDs associated with the ticker symbol
            derivative_ids = await conn.fetch(
                'SELECT ticker_id FROM wb_opts WHERE ticker = $1',
                ticker_symbol
            )
            
            # Convert the records to a list of IDs
            derivative_id_list = [str(record['ticker_id']) for record in derivative_ids]

            # Yield batches of 55 IDs at a time as a comma-separated string
            for i in range(0, len(derivative_id_list), 55):
                yield ','.join(derivative_id_list[i:i+55])

    async def get_option_ids(self, ticker):
        ticker_id = await trading.get_ticker_id(ticker)
        params = {
            "tickerId": f"{ticker_id}",
            "count": -1,
            "direction": "all",
            "expireCycle": [1,
                3,
                2,
                4
            ],
            "type": 0,
            "quoteMultiplier": 100,
            "unSymbol": f"{ticker}"
        }
        data = json.dumps(params)
        url="https://quotes-gw.webullfintech.com/api/quote/option/strategy/list"

        # Headers you may need to include, like authentication tokens, etc.
        headers = trading.headers
        # The body of your POST request as a Python dictionary
        import pandas as pd
        # Make the POST request
        # Make the POST request
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, data=data) as resp:
                response_json = await resp.json()
        
                # Extract the 'expireDateList' from the response
                expireDateList = response_json.get('expireDateList')

                # Flatten the nested 'data' from each item in 'expireDateList'
            try:
                data_flat = [item for sublist in expireDateList if sublist and sublist.get('data') for item in sublist['data']]



                # Create a DataFrame from the flattened data
                df_cleaned = pd.DataFrame(data_flat)

                # Drop the 'askList' and 'bidList' columns if they exist
                df_cleaned.drop(columns=['askList', 'bidList'], errors='ignore', inplace=True)
                # Existing DataFrame columns
                df_columns = df_cleaned.columns

                # Original list of columns you want to convert to numeric
                numeric_cols = ['open', 'high', 'low', 'strikePrice', 'isStdSettle', 'quoteMultiplier', 'quoteLotSize']

                # Filter the list to include only columns that exist in the DataFrame
                existing_numeric_cols = [col for col in numeric_cols if col in df_columns]

                # Now apply the to_numeric conversion only to the existing columns
                df_cleaned[existing_numeric_cols] = df_cleaned[existing_numeric_cols].apply(pd.to_numeric, errors='coerce')

      
            
                df_cleaned.to_csv('test.csv', index=False)


                # Load the data from the CSV file
                df = pd.read_csv('test.csv')

                # Extract 'tickerId' column values in batches of 55
                ticker_ids = df['tickerId'].unique()  # Assuming 'tickerId' is a column in your DataFrame
                symbol_list = df['symbol'].unique().tolist()
            # Pair up 'tickerId' and 'symbol'
                # Before you call batch_insert_options, make sure pairs contain the correct types
                pairs = [(str(symbol), int(ticker_id), str(ticker)) for ticker_id, symbol in zip(ticker_ids, symbol_list)]

                
                await self.batch_insert_options(pairs)
                return pairs
            except (ContentTypeError, TypeError):
                print(f'Error for {ticker}')
    async def get_option_id_for_symbol(self, ticker_symbol, table_name:str='webull_options'):
        async with self.pool.acquire() as conn:
            # Start a transaction
            async with conn.transaction():
                # Execute the query to get the option_id for a given ticker_symbol
                # This assumes 'symbol' column exists in 'options_data' table and 
                # is used to store the ticker symbol
                query = f'''
                    SELECT ticker_id FROM {table_name}
                    WHERE underlying_symbol = '{ticker_symbol}';
                '''
                # Fetch the result
                result = await conn.fetch(query)
                # Return a list of option_ids or an empty list if none were found
                return [record['ticker_id'] for record in result]


    async def get_option_symbols_by_ticker_id(self, ticker_id):
        async with self.pool.acquire() as conn:
            # Start a transaction
            async with conn.transaction():
                # Execute the query to get all option_symbols for a given ticker_id
                query = '''
                    SELECT option_symbol FROM options_data
                    WHERE ticker_id = $1;
                '''
                # Fetch the result
                records = await conn.fetch(query, ticker_id)
                # Extract option_symbols from the records
                return [record['option_symbol'] for record in records]
    async def get_ticker_symbol_pairs(self):
        # Assume 'pool' is an instance variable pointing to a connection pool
        async with self.pool.acquire() as conn:
            # Start a transaction
            async with conn.transaction():
                # Create a cursor for iteration using 'cursor()' instead of 'execute()'
                async for record in conn.cursor('SELECT ticker_id, symbol FROM wb_opts'):
                    yield (record['ticker_id'], record['symbol'])

    async def get_volume_analysis(self, ticker):
        ticker_id = await trading.get_ticker_id(ticker)
        params = {
            "tickerId": f"{ticker_id}",
            "count": -1,
            "direction": "all",
            "expireCycle": [1,
                3,
                2,
                4
            ],
            "type": 0,
            "quoteMultiplier": 100,
            "unSymbol": f"{ticker}"
        }
        data = json.dumps(params)
        url="https://quotes-gw.webullfintech.com/api/quote/option/strategy/list"

        # Headers you may need to include, like authentication tokens, etc.
        headers = trading.headers
        # The body of your POST request as a Python dictionary
        import pandas as pd
        # Make the POST request
        # Make the POST request
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, data=data) as resp:
                response_json = await resp.json()
          
                # Extract the 'expireDateList' from the response
                expireDateList = response_json.get('expireDateList')

                # Flatten the nested 'data' from each item in 'expireDateList'
            try:
                data_flat = [item for sublist in expireDateList if sublist and sublist.get('data') for item in sublist['data']]



                # Create a DataFrame from the flattened data
                df_cleaned = pd.DataFrame(data_flat)

                # Drop the 'askList' and 'bidList' columns if they exist
                df_cleaned.drop(columns=['askList', 'bidList'], errors='ignore', inplace=True)

                # Convert specified columns to numeric values, coercing errors to NaN
                numeric_cols = ['open', 'high', 'low', 'strikePrice', 'isStdSettle', 'quoteMultiplier', 'quoteLotSize']
                # Iterate through the list of numeric columns and check if they exist in df_cleaned
                existing_numeric_cols = [col for col in numeric_cols if col in df_cleaned.columns]

                # Now apply the conversion only on the columns that exist
                df_cleaned[existing_numeric_cols] = df_cleaned[existing_numeric_cols].apply(pd.to_numeric, errors='coerce')

                print(df_cleaned)
                df_cleaned.to_csv('test.csv', index=False)


                # Load the data from the CSV file
                df = pd.read_csv('test.csv')

                # Extract 'tickerId' column values in batches of 55
                ticker_ids = df['tickerId'].unique()  # Assuming 'tickerId' is a column in your DataFrame
                symbol_list = df['symbol'].unique().tolist()
            # Pair up 'tickerId' and 'symbol'
                pairs = list(zip(ticker_ids, symbol_list))

                
                # Split into batches of 55
                batches = [ticker_ids[i:i + 55] for i in range(0, len(ticker_ids), 55)]

                ticker_id_strings = [','.join(map(str, batch)) for batch in batches]







                for ticker_id_string in ticker_id_strings:
                    ticker_ids = ticker_id_string.split(',')
                    for deriv_id in ticker_ids:
                        all_data = []
                        volume_analysis_url = f"https://quotes-gw.webullfintech.com/api/statistic/option/queryVolumeAnalysis?count=200&tickerId={deriv_id}"
                        async with aiohttp.ClientSession(headers=headers) as session:
                            async with session.get(volume_analysis_url) as resp:
                                data = await resp.json()
                                all_data.append(data)


                   
                        return all_data
                        #df = pd.DataFrame(all_data)
                        #df.to_csv('all_options', index=False)
            except (ContentTypeError, TypeError):
                print(f'Error for {ticker}')

    async def get_option_ids_limited(self, sem, ticker):
        async with sem:
            # This will wait until the semaphore allows entry (i.e., under the limit)
            return await self.get_option_ids(ticker)

    async def harvest_options(self,most_active_tickers):
        # Set the maximum number of concurrent requests
        max_concurrent_requests = 5  # For example, limiting to 10 concurrent requests

        # Create a semaphore with your desired number of concurrent requests
        sem = asyncio.Semaphore(max_concurrent_requests)
        await self.connect()
        # Create tasks using the semaphore
        tasks = [self.get_option_ids_limited(sem, ticker) for ticker in most_active_tickers]

        # Run the tasks concurrently and wait for all to complete
        await asyncio.gather(*tasks)


    async def get_option_data_for_ticker(self, ticker):
        print(f"Starting processing for ticker: {ticker}")
        dataframes = []  # Initialize a list to collect DataFrames
  
        async for info in self.yield_batch_ids(ticker_symbol=ticker):
            print(f"Processing batch ID: {info} for ticker: {ticker}")
            url = f"https://quotes-gw.webullfintech.com/api/quote/option/quotes/queryBatch?derivativeIds={info}"
            async with aiohttp.ClientSession(headers=trading.headers) as session:
                async with session.get(url) as resp:
                    data = await resp.json()
                    if not data:  # If data is empty or None, break the loop
                        print(f"No more data for ticker: {ticker}. Moving to next.")
                        break
                    wb_data = WebullOptionsData(data)
                    if self.as_dataframe is not None:
                        df = wb_data.as_dataframe
                        df['ticker'] = ticker
                        df = df.rename(columns={'open_interest_change': 'oi_change'})
                        
                        await self.insert_dataframe_in_batches(df, 'options_data')
                        dataframes.append(df)
        return dataframes
            
        

  



    async def insert_dataframe_in_batches(self, df, table_name, batch_size=55):
        """
        Insert a pandas DataFrame into a SQL table in batches.

        :param df: The pandas DataFrame to insert.
        :param table_name: The name of the target SQL table.
        :param batch_size: The size of the batches to insert.
        """
        # Make sure we have a connection
        
        df['expiry_date'] = df['expiry_date'].apply(convert_to_date)
        df['close'] = df['close'].astype(float)
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['open_interest'] = df['open_interest'].replace({np.nan: None})
        async with self.pool.acquire() as conn:
            try:
                # Convert DataFrame to list of tuples
                records = df.to_records(index=False)
                columns = df.columns.tolist()
                values = [tuple(x) for x in records]

                # Create a prepared statement
                placeholders = ', '.join(f'${i+1}' for i in range(len(columns)))
                insert_query = f'INSERT INTO {table_name} ({", ".join(columns)}) VALUES ({placeholders})'

                # Insert data in batches
                for i in range(0, len(values), batch_size):
                    batch = values[i:i + batch_size]
                    await conn.executemany(insert_query, batch)

            except asyncpg.exceptions.UniqueViolationError:
                print(f'Duplicate found - skipping.')


        # Initialize an HTTP session
    async def associate_dates_with_data(self, dates, datas):
        if datas is not None and dates is not None:
        # This function remains for your specific data handling if needed
            return [{**data, 'date': date} for date, data in zip(dates, datas)]
    async def fetch_volume_analysis(self, option_symbol, id, underlying_ticker):
        url = f"https://quotes-gw.webullfintech.com/api/statistic/option/queryVolumeAnalysis?count=200&tickerId={id}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    vol_anal = await resp.json()
                    dates = vol_anal.get('dates')
                    datas = vol_anal.get('datas')
                    associated_data = await self.associate_dates_with_data(dates, datas)

                    df = pd.DataFrame(associated_data)
                    df['option_symbol'] = option_symbol
                    components = get_human_readable_string(option_symbol)
                    df['underlying_ticker'] = underlying_ticker
                    df['strike'] = components.get('strike_price')
                    df['call_put'] = components.get('call_put')
                    df['expiry'] = components.get('expiry_date')
                    return df
                else:
                    print(f"Failed to fetch data for ID {id}: HTTP Status {resp.status}")
                    return pd.DataFrame()
                    
    # Initialize an HTTP session
    async def test_vol_anal(self, ticker_id):
        volume_analysis_url = f"https://quotes-gw.webullfintech.com/api/statistic/option/queryVolumeAnalysis?count=500&tickerId={ticker_id}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(volume_analysis_url) as resp:
                data = await resp.json()
                if data is not None:
                    return VolumeAnalysis(data).trades_and_dates_dict
    async def insert_trades_and_dates(self, data):
        data['date'] = datetime.strptime(data['date'], '%Y-%m-%d')
        # Convert numeric strings to appropriate numeric types
        data['price'] = float(data['price']) if data['price'] else 0.0
        data['buy'] = int(data['buy']) if data['buy'] else 0
        data['sell'] = int(data['sell']) if data['sell'] else 0
        data['volume'] = int(data['volume']) if data['volume'] else 0
        data['strike_price'] = float(data['strike_price']) if data['strike_price'] else 0.0
        # Convert expiry_date string to date object
        data['expiry_date'] = datetime.strptime(data['expiry_date'], '%Y-%m-%d')

                

        # Assuming 'data' is a dictionary containing the keys that match your table's columns.
        async with self.pool.acquire() as connection:
            await connection.execute('''
                INSERT INTO trades_and_dates (
                    date, price, buy, sell, volume, ratio,
                    option_symbol, symbol, strike_price, call_put,
                    expiry_date
                ) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ''',
            data['date'], data['price'], data['buy'], data['sell'], data['volume'],
            data['ratio'], data['option_symbol'], data['symbol'], data['strike_price'],
            data['call_put'], data['expiry_date'])
    async def insert_volume_analysis_data(self, data: dict):
        # Assuming data contains the fields corresponding to your self.data_dict
        # You would extract these values and insert them into your volume_analysis table
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO volume_analysis (ticker_id, symbol, option_id, total_trades, total_volume, avg_price, buy_volume, sell_volume, neutral_volume, option_symbol, strike_price, call_put, expiry_date)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            """, data.get('ticker_id'), data.get('symbol', None), data.get('option_id', None), data.get('total_trades', None), data.get('total_volume', None), data.get('avg_price',None),data.get('buy_volume',None), data.get('sell_volume', None), data.get('neutral_volume', None), data.get('option_symbol', None), data.get('strike_price') , data.get('call_put'), data.get('expiry_date')        )
        
    async def run_all_tasks(self, tickers):

        async with aiohttp.ClientSession(headers=self.headers) as session:
            tasks = [self.get_option_data_for_ticker(ticker, session) for ticker in tickers]
            await asyncio.gather(*tasks)
    async def store_options_data(self):
        await self.connect()
        semaphore = asyncio.Semaphore(5)  # Adjust the number to limit concurrent tasks

        async def limited_get_option_data_for_ticker(ticker):
            async with semaphore:
                return await self.get_option_data_for_ticker(ticker)

        tasks = [limited_get_option_data_for_ticker(i) for i in self.most_active_tickers]
        await asyncio.gather(*tasks)

    async def get_vol1y(self, ticker):
        await self.connect()
        data = await self.get_option_id_for_symbol(ticker)
       
        for id in data:
            ticker_id = await WebullTrading().get_ticker_id(ticker)
            url = f"https://quotes-gw.webullfintech.com/api/quote/option/quotes/detail?derivativeIds={id}&tickerId={ticker_id}"
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as resp:
                    data = await resp.json()
                    
                    vol1y = data.get('vol1y')
                    return vol1y
    async def batch_insert_dataframe(self, df, table_name, unique_columns, batch_size=250):
        """
        WORKS - Creates table - inserts data based on DTYPES.
        
        """
    
        async with lock:
            if not await self.table_exists(table_name):
                await self.create_table(df, table_name)
            
            # Debug: Print DataFrame columns before modifications
            #print("Initial DataFrame columns:", df.columns.tolist())
            
            df = df.copy()
            df.dropna(inplace=True)

            # Debug: Print DataFrame columns after modifications
            #print("Modified DataFrame columns:", df.columns.tolist())
            
            records = df.to_records(index=False)
            data = list(records)


            async with self.pool.acquire() as connection:
                column_types = await connection.fetch(
                    f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
                )
                type_mapping = {col: next((item['data_type'] for item in column_types if item['column_name'] == col), None) for col in df.columns}

                async with connection.transaction():
                    insert_query = f"""
                    INSERT INTO {table_name} ({', '.join(f'"{col}"' for col in df.columns)}) 
                    VALUES ({', '.join('$' + str(i) for i in range(1, len(df.columns) + 1))})
                    ON CONFLICT ({unique_columns})
                    DO UPDATE SET {', '.join(f'"{col}" = excluded."{col}"' for col in df.columns)}
                    """
            
                    batch_data = []
                    for record in data:
                        new_record = []
                        for col, val in zip(df.columns, record):
                            pg_type = type_mapping[col]

                            if val is None:
                                new_record.append(None)
                            elif pg_type in ['timestamp', 'timestamp without time zone', 'timestamp with time zone']:
                                if isinstance(val, np.datetime64):
                                    # Convert numpy datetime64 to Python datetime, ensure UTC and remove tzinfo if needed
                                    new_record.append(pd.Timestamp(val).to_pydatetime().replace(tzinfo=None))
                                elif isinstance(val, datetime):
                                    # Directly use the Python datetime object
                                    new_record.append(val)
                            elif pg_type in ['double precision', 'real'] and not isinstance(val, str):
                                new_record.append(float(val))
                            elif isinstance(val, np.int64):
                                new_record.append(int(val))
                            elif pg_type == 'integer' and not isinstance(val, int):
                                new_record.append(int(val))
                            else:
                                new_record.append(val)
                    
                        batch_data.append(new_record)

                        if len(batch_data) == batch_size:
                            try:
                                
                            
                                await connection.executemany(insert_query, batch_data)
                                batch_data.clear()
                            except Exception as e:
                                print(f"An error occurred while inserting the record: {e}")
                                await connection.execute('ROLLBACK')
                                raise

                if batch_data:  # Don't forget the last batch
    
                    try:

                        await connection.executemany(insert_query, batch_data)
                    except Exception as e:
                        print(f"An error occurred while inserting the record: {e}")
                        await connection.execute('ROLLBACK')
                        raise
    async def save_to_history(self, df, main_table_name, history_table_name):
        # Assume the DataFrame `df` contains the records to be archived
        if not await self.table_exists(history_table_name):
            await self.create_table(df, history_table_name, None)

        df['archived_at'] = datetime.now()  # Add an 'archived_at' timestamp
        await self.batch_insert_dataframe(df, history_table_name, None)
    async def table_exists(self, table_name):
        query = f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}');"

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                exists = await conn.fetchval(query)
        return exists

    async def close_pool(self):
        await self.pool.close()
