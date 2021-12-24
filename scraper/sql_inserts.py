import asyncio
import os
import traceback
import sys, subprocess
import aiofiles
import ujson
from models import s, hr, sconres, hjres, hres, hconres, sjres, sres
from init import initialize_db, db
from sqlalchemy.orm import sessionmaker
import time
from apscheduler.schedulers.blocking import BlockingScheduler
import xml.etree.ElementTree as ET
from dateutil import parser

tables = [s, hr, hconres, hjres, hres, sconres, sjres, sres]

## Full Scraper
Session = sessionmaker(bind=db)


async def billProcessor(billList, congressNumber, table, session):
    billType = table.__tablename__
    print(f'Processing: Congress: {congressNumber} Type: {billType}')
    for b in billList:
        try:
            # filePath = f'/congress/data/{congressNumber}/bills/{table.__tablename__}/{bill}/data.json'
            # if os.path.exists(filePath):
            # if False:
            #     async with aiofiles.open(filePath) as f:
            #         contents = await f.read()
            #         data = ujson.loads(contents)
            #         billnumber = data['number']
            #         billtype = data['bill_type']
            #         introduceddate = data['introduced_at']
            #         congress = data['congress']
            #
            #         ## committee code
            #         committees = data['committees']
            #         committeelist = []
            #         try:
            #             for com in committees:
            #                 committee = data['committee']
            #                 committeelist.append(
            #                     {'committee': committee})
            #         except:
            #             pass
            #
            #         try:
            #             title = data['short_title']
            #             if title is None:
            #                 title = data['official_title']
            #         except:
            #             pass
            #
            #         # ignore if no summary
            #         try:
            #             summary = data['summary']['text']
            #         except:
            #             continue
            #
            #         actions = data['actions']
            #         actionlist = []
            #         for a in actions:
            #             actionlist.append({'date': a['acted_at'], 'text': a['text'], 'type': a['type']})
            #         actionlist.reverse()
            #         ## sponsors code
            #         sponsorlist = []
            #         sponsor = data['sponsor']
            #         if sponsor is not None:
            #             if sponsor['title'] == 'sen':
            #                 sponsortitle = f"{sponsor['title']} {sponsor['name']} [{sponsor['state']}]"
            #             else:
            #                 sponsortitle = f"{sponsor['title']} {sponsor['name']} [{sponsor['state']}-{sponsor['district']}]"
            #         sponsorlist.append({'fullname': sponsortitle})
            #         cosponsorlist = []
            #         try:
            #             cosponsors = data['cosponsors']
            #             for sponsor in cosponsors:
            #                 if sponsor['title'] == 'sen':
            #                     sponsortitle = f"{sponsor['title']} {sponsor['name']} [{sponsor['state']}]"
            #                 else:
            #                     sponsortitle = f"{sponsor['title']} {sponsor['name']} [{sponsor['state']}-{sponsor['district']}]"
            #             cosponsorlist.append({'fullname': sponsortitle})
            #         except:
            #             traceback.format_exc()
            #         try:
            #             status_at = data['status_at']
            #         except:
            #             traceback.format_exc()
            #         sql = table(billnumber=billnumber, billtype=billtype, introduceddate=introduceddate,
            #                     congress=congress, committees=committeelist, actions=actionlist,
            #                     sponsors=sponsorlist, cosponsors=cosponsorlist,
            #                     title=title, summary=summary, status_at=status_at)
            #         session.merge(sql)
            if os.path.exists(f'/congress/data/{congressNumber}/bills/{table.__tablename__}/{b}/fdsys_billstatus.xml'):
                # print(f'processing {table.__tablename__}/{b}/')
                filename = f'/congress/data/{congressNumber}/bills/{table.__tablename__}/{b}/fdsys_billstatus.xml'
                try:
                    tree = ET.parse(filename)
                    root = tree.getroot()
                    bill = root.find('bill')
                    billNumber = bill.find('billNumber').text
                    billType = bill.find('billType').text
                    introducedDate = parser.parse(bill.find('introducedDate').text)
                    congress = bill.find('congress').text
                    committeeList = []
                    committees = bill.find('committees').find('billCommittees')
                    for com in committees:
                        committee = com.find('name').text
                        committeeChamber = com.find('chamber').text
                        committeeType = com.find('type').text
                        subcommittees = com.find('subcommittees')
                        subcommitteesList = []
                        for sb in subcommittees:
                            sbName = sb.find('name').text
                            sbActivitiesList = []
                            sbActivities = sb.find('activities')
                            for sba in sbActivities:
                                sbaName = sba.find('name').text
                                sbaDate = sba.find('date').text
                                sbActivitiesList.append({'name': sbaName, 'date': sbaDate})
                            subcommitteesList.append({'name': sbName, 'activities': sbActivitiesList})
                        committeeList.append(
                            {'committee': committee, 'comitteeChamber': committeeChamber,
                             'committeeType': committeeType,
                             'subcommittees': subcommitteesList})
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
                    status_at = actionsList[0]['date']
                    sql = table(billnumber=billNumber, billtype=billType, introduceddate=introducedDate,
                                congress=congress, committees=committeeList, actions=actionsList,
                                sponsors=sponsorList, cosponsors=cosponsorList,
                                title=title, summary=summary, status_at=status_at)
                    session.merge(sql)
                except:
                    traceback.print_exc()
                    continue
        except:
            traceback.print_exc()
            print(f'{congressNumber}/{table.__tablename__}-{b} does not exist')
            continue

    session.commit()
    print(f'Added: Congress: {congressNumber} Bill Type: {billType} # Rows Inserted: {len(billList)}')


async def main():
    await update_files()
    for table in tables:
        tasks = []
        congressNumbers = range(93, 118)
        with Session() as session:
            for congressNumber in congressNumbers:
                bills = os.listdir(f'/congress/data/{congressNumber}/bills/{table.__tablename__}')
                tasks.append(asyncio.ensure_future(billProcessor(bills, congressNumber, table, session)))
            await asyncio.gather(*tasks)
            print(f'Processed: {table.__tablename__}')

    # APScheduler used for updating
    # scheduler = BlockingScheduler()
    # scheduler.add_job(update_files, 'interval', kwargs={'update_only': True}, hours=6)
    # scheduler.start()

async def update_files(update_only=False):
    print(os.listdir('.'))
    os.chdir('/congress')

    os.system('/congress/run govinfo --bulkdata=BILLSTATUS')
    os.chdir('/')
    if update_only:
        await update()


async def update():
    with Session() as session:
        tasks = []
        for table in tables:
            bills = os.listdir(f'/congress/data/117/bills/{table.__tablename__}')
            tasks.append(asyncio.ensure_future(billProcessor(bills, 117, table, session)))
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    initialize_db()
    asyncio.run(main())

### Finished populating the database
print("SQL INSERTS COMPLETED")
