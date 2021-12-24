#!/usr/bin/python3

import asyncio
import os
from models import s, hr, sconres, hjres, hres, hconres, sjres, sres
from sql_inserts import billProcessor

from init import get_db_session
tables = [s, hr, hconres, hjres, hres, sconres, sjres, sres]


## Updater Scraper

async def main():
    Session = get_db_session()
    with Session() as session:
        for table in tables:
            tasks = []
            bills = os.listdir(f'congress/data/117/bills/{table.__tablename__}')
            tasks.append(asyncio.ensure_future(billProcessor(bills, 117, table, session)))
            await asyncio.gather(*tasks)


asyncio.run(main())
