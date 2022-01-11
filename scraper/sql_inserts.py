import asyncio
import os
import traceback
import aiofiles
import ujson
from models import s, hr, sconres, hjres, hres, hconres, sjres, sres
from init import initialize_db, db
from sqlalchemy.orm import sessionmaker
from lxml import etree as ET
from dateutil import parser
from tqdm import tqdm

tables = [s, hr, hconres, hjres, hres, sconres, sjres, sres]

## Full Scraper
Session = sessionmaker(bind=db)


async def billProcessor(billList, congressNumber, table, session):
    billType = table.__tablename__
    print(f'Processing: Congress: {congressNumber} Type: {billType}')
    tasks = []
    for b in billList:
        try:
            task = asyncio.to_thread(process, b, congressNumber, table, session)
            tasks.append(task)
        except:
            traceback.print_exc()
            print(f'Failed processing {congressNumber}/{billType}-{b}')
    return tasks



async def process(bill, congressNumber, table, session):
    path = f'/congress/data/{congressNumber}/bills/{table.__tablename__}/{bill}'
    if os.exists(f'{path}/fdsys_billstatus.xml'):
        try:
            tree = ET.parse(f'{path}/fdsys_billstatus.xml')
            root = tree.getroot()
            bill = root.find('bill')
            billNumber = bill.find('billNumber').text
            billType = bill.find('billType').text
            introducedDate = parser.parse(bill.find('introducedDate').text)
            congress = bill.find('congress').text
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
                print(f"Unexpected {err=}, {type(err)=}")
                print(f'No actions for bill {congressNumber}-{billType}{billNumber}')
            sponsors = bill.find('sponsors')
            sponsorList = []
            for s in sponsors:
                fullName = s.find('fullName').text
                party = s.find('party').text
                state = s.find('state').text
                sponsorList.append({'fullName': fullName, 'party': party, 'state': state})
            cosponsorList = []
            try:
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
                print(f'No summary for bill {congressNumber}-{billType}{billNumber}')
            title = bill.find('title').text
            status_at = parser.parse(actionsList[0]['date'])

            sql = table(billnumber=billNumber, billtype=billType, introduceddate=introducedDate,
                        congress=congress, committees=committeeList, actions=actionsList,
                        sponsors=sponsorList, cosponsors=cosponsorList,
                        title=title, summary=summary, status_at=status_at)
            session.merge(sql)
        except:
            traceback.print_exc()
    elif os.exists(f'{path}/data.json'):
        try:
            with aiofiles.open(f'{path}/data.json') as contents:
                contents = await contents.read()
                data = ujson.loads(contents)
                billNumber = data['number']
                billtype = data['bill_type']
                introduceddate = parser.parse(data['introduced_at'])
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
                    pass

                actions = data['actions']
                actionlist = []
                for a in actions:
                    actionlist.append({'date': a['acted_at'], 'text': a['text'], 'type': a['type']})
                actionlist.reverse()
                ## sponsors code
                sponsorlist = []
                sponsor = data['sponsor']
                if sponsor is not None:
                    if sponsor['title'] == 'sen':
                        sponsortitle = f"{sponsor['title']} {sponsor['name']} [{sponsor['state']}]"
                    else:
                        sponsortitle = f"{sponsor['title']} {sponsor['name']} [{sponsor['state']}-{sponsor['district']}]"
                sponsorlist.append({'fullname': sponsortitle})
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
                    pass
                try:
                    status_at = parser.parse(data['status_at'])
                except:
                    traceback.format_exc()

                sql = table(billnumber=billNumber, billtype=billtype, introduceddate=introduceddate,
                            congress=congress, committees=committeelist, actions=actionlist,
                            sponsors=sponsorlist, cosponsors=cosponsorlist,
                            title=title, summary=summary, status_at=status_at)
                session.merge(sql)
        except:
            traceback.print_exc()
            print(f'{congressNumber}/{table.__tablename__}-{billNumber} failed')
    session.commit()
    return f'processed {congressNumber}/{table.__tablename__}-{billNumber}'



async def main():
    # await update_files()
    congressNumbers = range(93, 118)
    for congressNumber in congressNumbers:
        tasks = []
        with Session() as session:
            for table in tables:
                bills = os.listdir(f'/congress/data/{congressNumber}/bills/{table.__tablename__}')
                tasks += await billProcessor(bills, congressNumber, table, session)
            for future in asyncio.as_completed(tasks):
                print(await future)
            print(f'Processed: {table.__tablename__}')

    # # APScheduler used for updating
    # scheduler = BlockingScheduler()
    # scheduler.add_job(update_files, 'interval', kwargs={'update_only': True}, hours=6)
    # scheduler.start()

async def update_files(update_only=False):
    print(os.listdir('/'))
    os.chdir('/congress')
    os.system('./run govinfo --bulkdata=BILLSTATUS')
    if update_only:
        await update()


async def update():
    with Session() as session:
        tasks = []
        for table in tables:
            bills = os.listdir(f'/congress/data/117/bills/{table.__tablename__}')
            tasks.append(billProcessor(bills, 117, table, session))

        for future in asyncio.as_completed(tasks):
            print(await future)


if __name__ == "__main__":
    initialize_db()
    asyncio.run(main())

### Finished populating the database
print("SQL INSERTS COMPLETED")
