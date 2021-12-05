import asyncio
import os
from models import s, hr, sconres, hjres, hres, hconres, sjres, sres
from sql_inserts import billProcessor
tables = [s, hr, hconres, hjres, hres, sconres, sjres, sres]


## Updater Scraper

async def main():
    for table in tables:
        tasks = []
        bills = os.listdir(f'data/117/bills/{table.__tablename__}')
        tasks.append(asyncio.ensure_future(billProcessor(bills, 117, table)))
        await asyncio.gather(*tasks)


asyncio.run(main())
