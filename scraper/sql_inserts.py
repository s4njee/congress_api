import asyncio
import os
import traceback

import aiofiles
import ujson
from models import s, hr, sconres, hjres, hres, hconres, sjres, sres
from init import initialize_db, get_db_session
tables = [s, hr, hconres, hjres, hres, sconres, sjres, sres]
from concurrent.futures import ThreadPoolExecutor

## Full Scraper
Session = get_db_session()


async def billProcessor(billList, congressNumber, table, session):
    billType = table.__tablename__
    print(f'Processing: Congress: {congressNumber} Type: {billType}')
    for bill in billList:
        filePath = f'data/{congressNumber}/bills/{table.__tablename__}/{bill}/data.json'
        if os.path.exists(filePath):
            async with aiofiles.open(filePath) as f:
                contents = await f.read()
                data = ujson.loads(contents)
                billnumber = data['number']
                billtype = data['bill_type']
                introduceddate = data['introduced_at']
                congress = data['congress']

                ## committee code
                committees = data['committees']
                committeelist = []
                try:
                    for com in committees:
                        committee = data['committee']
                        committeelist.append(
                            {'committee': committee})
                except:
                    pass

                try:
                    title = data['short_title']
                    if title is None:
                        title = data['official_title']
                except:
                    pass

                # ignore if no summary
                try:
                    summary = data['summary']['text']
                except:
                    continue

                actions = data['actions']
                actionlist = []
                for a in actions:
                    actionlist.append({'date': a['acted_at'], 'text': a['text'], 'type': a['type']})

                ## sponsors code
                sponsorlist = []
                sponsor = data['sponsor']
                if sponsor is not None:
                    if sponsor['title'] == 'sen':
                        sponsortitle = f"{sponsor['title']} {sponsor['name']} [{sponsor['state']}]"
                    else:
                        sponsortitle = f"{sponsor['title']} {sponsor['name']} [{sponsor['state']}-{sponsor['district']}]"
                sponsorlist.append({'fullname': sponsortitle})
                sponsorlist
                cosponsorlist = []
                try:
                    cosponsors = data['cosponsors']
                    for sponsor in cosponsors:
                        if sponsor['title'] == 'sen':
                            sponsortitle = f"{sponsor['title']} {sponsor['name']} [{sponsor['state']}]"
                        else:
                            sponsortitle = f"{sponsor['title']} {sponsor['name']} [{sponsor['state']}-{sponsor['district']}]"
                    cosponsorlist.append({'fullname': sponsortitle})
                except:
                    traceback.format_exc()
                try:
                    status_at = data['status_at']
                except:
                    traceback.format_exc()
                sql = table(billnumber=billnumber, billtype=billtype, introduceddate=introduceddate,
                            congress=congress, committees=committeelist, actions=actionlist,
                            sponsors=sponsorlist, cosponsors=cosponsorlist,
                            title=title, summary=summary, status_at=status_at)
                session.add(sql)
        else:
            print(f'{filePath} does not exist')
        # print(f'Added: Congress: {congressNumber} Bill Type: {billType} # Rows Inserted: {len(billList)}')

async def main():
    print(os.getcwd())
    for table in tables:
        tasks = []
        congressNumbers = range(93, 118)
        with Session() as session:
            for congressNumber in congressNumbers:
                bills = os.listdir(f'data/{congressNumber}/bills/{table.__tablename__}')
                tasks.append(asyncio.ensure_future(billProcessor(bills, congressNumber, table, session)))
            await asyncio.gather(*tasks)
            session.commit()
            print(f'Processed: {table.__tablename__}')

if __name__ == "__main__":
    initialize_db()
    asyncio.run(main())
### Finished populating the database
print("SQL INSERTS COMPLETED")
#
#