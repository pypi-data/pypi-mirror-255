
import aiohttp
import asyncio
import pandas as pd

from typing import Optional

from .occ_models import StockLoans, VolumeTotals, DailyMarketShare
from datetime import datetime, timedelta
from .occ_models import flatten_json
from asyncpg import create_pool


class occSDK:
    def __init__(self, host, port, user, password, database):
        self.conn = None
        self.pool = None
        self.session = None

        self.host = host
        self.port = port
        self.user = user
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.today_mmddyyyy = datetime.now().strftime('%m/%d/%Y')
        self.yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        self.password = password
        self.database = database
        self.connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.base_url = f"https://marketdata.theocc.com/mdapi/"
        self.chat_memory = []  # In-memory list to store chat messages
    # Fetch all URLs
    async def convert_ms_timestamp(timestamp_ms):
        # Convert milliseconds to seconds
        timestamp_s = timestamp_ms / 1000.0
        return datetime.fromtimestamp(timestamp_s).strftime('%Y-%m-%d %H:%M:%S')
    async def fetch_url(session, url):
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                print(f"Error: {response.status}")
                return None
    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def connect(self):
        self.pool = await create_pool(
            host=self.host, pool=self.pool, password=self.password, database=self.database, port=self.port, min_size=1, max_size=40
        )

        return self.pool
        

    async def save_to_database(self, flattened_data):
        async with self.pool.acquire() as conn:
            # Flatten the data and prepare it for insertion

            
            # Prepare the SQL INSERT query
            columns = ', '.join(flattened_data.keys())
            placeholders = ', '.join([f'${i+1}' for i in range(len(flattened_data))])
            query = f'INSERT INTO occ_totals ({columns}) VALUES ({placeholders})'
            
            # Execute the query
            await conn.execute(query, *flattened_data.values())


    async def stock_loans(self, report_date: str = None, type: str = "daily") -> Optional[StockLoans]:
        """Retrieve stock loan data for a specific report date and type.

        Args:
            report_date (str): Report date in YYYY-MM-DD format. Defaults to today's date.
            type (str): Report type. Defaults to "daily".

        Returns:
            Optional[StockLoans]: Stock loan data for the specified report date and type, or None if data is not available.
        """
        if report_date is None:
            report_date = self.today
        url=f"https://marketdata.theocc.com/mdapi/stock-loan?report_date={report_date}&report_type={type}"
        session = await self.get_session()
        async with session.get(url) as data:
            r = await data.json()
            entity = r['entity']
            stockLoanResults = StockLoans(entity['stockLoanResults'] if entity.get('stockLoanResults') is not None else None)
            if stockLoanResults:
                return stockLoanResults
            else:
                return None


        

    async def stock_loans(self, report_date: str = None) -> Optional[StockLoans]:
        """Retrieve stock loan data for a specific report date and type.

        Args:
            report_date (str): Report date in YYYY-MM-DD format. Defaults to today's date.
            type (str): Report type. Defaults to "daily".

        Returns:
            Optional[StockLoans]: Stock loan data for the specified report date and type, or None if data is not available.
        """
        if report_date is None:
            report_date = self.today
        url=f"https://marketdata.theocc.com/mdapi/stock-loan?report_date={report_date}&report_type=daily"
        session = await self.get_session()
        async with session.get(url) as data:
            r = await data.json()
            entity = r['entity']
            stockLoanResults = StockLoans(entity['stockLoanResults'] if entity.get('stockLoanResults') is not None else None)
            if stockLoanResults:
                return stockLoanResults
            else:
                return None

    async def volume_totals(self) -> VolumeTotals:
        """Retrieve volume totals data.

        Returns:
            VolumeTotals: Volume totals data.
        """
        url = "https://marketdata.theocc.com/mdapi/volume-totals"
        session = await self.get_session()
        async with session.get(url) as data:
            r = await data.json()
            entity = r['entity']
            if entity is not None:

                return flatten_json(entity)
            

    async def open_interest(self):

        """
        
        DATE FORMAT = MM/DD/YYYY
        """
        url = f"https://marketdata.theocc.com/mdapi/open-interest?report_date={self.today_mmddyyyy}"
        session = await self.get_session()
        async with session.get(url) as data:
            r = await data.json()

            entity = r['entity']


            optionsOI = entity['optionsOI']
            all_data = []

            for i in optionsOI:
                activityDate = await self.convert_ms_timestamp(i.get('activityDate'))
                equityCalls = i.get('equityCalls')
                equityPuts = i.get('equityPuts')
                indexCalls = i.get('indexCalls')
                indexPuts = i.get('indexPuts')
                treasuryCalls = i.get('treasuryCalls')
                treasuryPuts = i.get('treasuryPuts')
                equityTotal = i.get('equityTotal')
                indexTotal = i.get('indexTotal')
                treasuryTotal = i.get('treasuryTotal')
                futuresTotal = i.get('futuresTotal')
                occTotal = i.get('occTotal')

                data_dict = { 

                    'activity_date': activityDate,
                    'equity_calls': equityCalls,
                    'equity_puts': equityPuts,
                    'equity_total': equityTotal,
                    'index_calls': indexCalls,
                    'index_puts': indexPuts,
                    'index_total': indexTotal,
                    'treasury_calls': treasuryCalls,
                    'treasury_puts': treasuryPuts,
                    'treasury_total': treasuryTotal,
                    'futures_total': futuresTotal,
                    'occTotal': occTotal
                }

                all_data.append(data_dict)


            df =pd.DataFrame(all_data)
            return df


    async def daily_market_share(self, date=None):
        today_str = pd.Timestamp.today().strftime('%Y-%m-%d')
        date = today_str if not date else date
        url = f"https://marketdata.theocc.com/mdapi/daily-volume-totals?report_date={date}"
        session = await self.get_session()
        async with session.get(url) as data:
            r = await data.json()

            entity = r['entity']
            if entity['total_volume'] == []:
                f"https://marketdata.theocc.com/mdapi/daily-volume-totals?report_date={self.yesterday}"
                entity = r['entity']
                

                total_volume = DailyMarketShare(entity)
                return total_volume.df


            

            else:
                total_volume = DailyMarketShare(entity)
                return total_volume.df

