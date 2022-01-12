import asyncio
import os
import traceback
import aiofiles
from models import s, hr, sconres, hjres, hres, hconres, sjres, sres
from init import initialize_db, db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from lxml import etree as ET
from dateutil import parser
import ujson as json
from tqdm import tqdm
tables = [s, hr, hconres, hjres, hres, sconres, sjres, sres]
# from apscheduler.schedulers.blocking import BlockingScheduler

## Full Scraper
Session = sessionmaker(
    db, expire_on_commit=False, class_=AsyncSession
)


async def billProcessor(billList, congressNumber, table):
    billType = table.__tablename__
    print(f'Processing: Congress: {congressNumber} Type: {billType}')
    tasks = []
    for b in billList:
        try:
            task = asyncio.create_task(process(b, congressNumber, table))
            tasks.append(task)
        except:
            traceback.print_exc()
            print(f'Failed processing {congressNumber}/{billType}-{b}')
    return tasks


async def process(bill, congressNumber, table):
    path = f'/congress/data/{congressNumber}/bills/{table.__tablename__}/{bill}'
    if os.path.exists(f'{path}/fdsys_billstatus.xml'):
        try:
            tree = ET.parse(f'{path}/fdsys_billstatus.xml')
            root = tree.getroot()
            bill = root.find('bill')
            billNumber = int(bill.find('billNumber').text)
            billType = bill.find('billType').text
            introducedDate = parser.parse(bill.find('introducedDate').text)
            congress = int(bill.find('congress').text)
            committeeList = []
            committees = bill.find('committees').find('billCommittees')
            try:
                for com in committees:
                    committee = com.find('name').text
                    committeeChamber = com.find('chamber').text
                    committeeType = com.find('type').text
                    subcommittees = com.find('subcommittees')
                    subcommitteesList = []
                    try:
                        for sb in subcommittees:
                            sbName = sb.find('name').text
                            sbActivitiesList = []
                            sbActivities = sb.find('activities')
                            for sba in sbActivities:
                                sbaName = sba.find('name').text
                                sbaDate = sba.find('date').text
                                sbActivitiesList.append({'name': sbaName, 'date': sbaDate})
                            subcommitteesList.append({'name': sbName, 'activities': sbActivitiesList})
                    except:
                        print(f'No subcommittees for {billType}-{billNumber} {congressNumber}')
                    committeeList.append(
                        {'committee': committee, 'comitteeChamber': committeeChamber,
                         'committeeType': committeeType,
                         'subcommittees': subcommitteesList})
            except:
                print(f'No committees for {billType}-{billNumber} {congressNumber}')
            actions = bill.find('actions')
            actionsList = []
            status_at = ''
            try:
                for a in actions:
                    try:
                        actionDate = a.find('actionDate').text
                        actionText = a.find('text').text
                        actionsList.append({'date': actionDate, 'text': actionText})
                    # Not all actions have these fields
                    except:
                        pass
                actionsList.reverse()
            except BaseException as err:
                print(f'No actions for bill {congressNumber}-{billType}{billNumber}')
            try:
                sponsors = bill.find('sponsors')
                sponsorList = []
                for s in sponsors:
                    fullName = s.find('fullName').text
                    party = s.find('party').text
                    state = s.find('state').text
                    sponsorList.append({'fullName': fullName, 'party': party, 'state': state})
            except:
                print(f'No sponsors for bill {congressNumber}-{billType}{billNumber}')
            try:
                cosponsorList = []
                cosponsors = bill.find('cosponsors')
                for s in cosponsors:
                    fullName = s.find('fullName').text
                    party = s.find('party').text
                    state = s.find('state').text
                    cosponsorList.append({'fullName': fullName, 'party': party, 'state': state})
            except:
                print(f'No cosponsors for bill {congressNumber}-{billType}{billNumber}')
            try:
                summary = bill.find('summaries').find('billSummaries')[0].find('text').text
            except:
                summary = ''
                print(f'No summary for bill {congressNumber}-{billType}{billNumber}')
            title = bill.find('title').text
            try:
                status_at = parser.parse(actionsList[0]['date'])
            except:
                print(f'No date for bill {congressNumber}-{billType}{billNumber}')


            sql = table(billnumber=billNumber, billtype=billType, introduceddate=introducedDate,
                        congress=congress, committees=committeeList, actions=actionsList,
                        sponsors=sponsorList, cosponsors=cosponsorList,
                        title=title, summary=summary, status_at=status_at)
        except:
            traceback.print_exc()
    elif os.path.exists(f'{path}/data.json'):
        try:
           async with aiofiles.open(f'{path}/data.json') as contents:
                contents = await contents.read()
                data = json.loads(contents)
                billNumber = int(data['number'])
                billtype = data['bill_type']
                introduceddate = parser.parse(data['introduced_at'])
                congress = int(data['congress'])

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
                    summary = ''
                try:
                    actions = data['actions']
                    actionlist = []
                    for a in actions:
                        actionlist.insert(0,{'date': a['acted_at'], 'text': a['text'], 'type': a['type']})
                except:
                   print(f'No actions for {billtype}-{billNumber}')
                ## sponsors code
                sponsorlist = []
                sponsor = data['sponsor']
                if sponsor is not None:
                    if sponsor['title'] == 'sen':
                        sponsortitle = f"{sponsor['title']} {sponsor['name']} [{sponsor['state']}]"
                    else:
                        sponsortitle = f"{sponsor['title']} {sponsor['name']} [{sponsor['state']}-{sponsor['district']}]"
                    sponsorlist.append({'fullName': sponsortitle})
                cosponsorlist = []
                try:
                    cosponsors = data['cosponsors']
                    for sponsor in cosponsors:
                        if sponsor['title'] == 'sen':
                            sponsortitle = f"{sponsor['title']} {sponsor['name']} [{sponsor['state']}]"
                        else:
                            sponsortitle = f"{sponsor['title']} {sponsor['name']} [{sponsor['state']}-{sponsor['district']}]"
                    cosponsorlist.append({'fullName': sponsortitle})
                except:
                    pass
                try:
                    status_at = parser.parse(data['status_at'])
                except:
                    traceback.format_exc()

                sql = table(billnumber=billNumber, billtype=billtype, introduceddate=introduceddate,
                            congress=congress, committees=committeelist, actions=actionlist,
                            sponsors=sponsorlist, cosponsors=cosponsorlist,
                            title=title, summary=summary, status_at=status_at)
        except:
            traceback.print_exc()
            print(f'{congressNumber}/{table.__tablename__}-{billNumber} failed')
    try:
        return sql
    except:
        pass



async def main():
    await update_files()
    congressNumbers = range(93, 118)
    print('Beginning Parsing')
    for congressNumber in congressNumbers:
        tasks = []
        for table in tables:
            bills = os.listdir(f'/congress/data/{congressNumber}/bills/{table.__tablename__}')
            tasks += await billProcessor(bills, congressNumber, table)
        t = await asyncio.gather(*tasks)
        for sql in tqdm(t):
            async with Session.begin() as session:
                try:
                   await session.merge(sql)
                except:
                    traceback.print_exc()

            #     except:
            #         traceback.print_exc()
            #         pass
        # count = 0
        # for future in asyncio.as_completed(tasks):
        #     count += 1
        #     if count % 100 == 0:
        #         print(f'{count} rows inserted')
        #     try:
        #         async with Session.begin() as session:
        #             await session.merge(await future)
        #     except:
        #         traceback.print_exc()
        #         continue
        print(f'Processed Congress: {congressNumber}')

        # # APScheduler used for updating
        # scheduler = BlockingScheduler()
        # scheduler.add_job(update_files, 'interval', kwargs={'update_only': True}, hours=6)
        # scheduler.start()

async def update_files():
    print(os.listdir('/'))
    os.chdir('congress')
    os.system('./run govinfo --bulkdata=BILLSTATUS')



if __name__ == "__main__":
    initialize_db()
    asyncio.run(main())

### Finished populating the database
print("SQL INSERTS COMPLETED")
