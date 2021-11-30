from sqlalchemy import Text, Date, Column, Integer, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_mixin
from sqlalchemy_utils import database_exists, create_database, drop_database

db = create_engine('postgresql://postgres:postgres@db/congress')
Base = declarative_base()

if not database_exists(db.url):
    create_database(db.url)
else:
    drop_database(db.url)
    create_database(db.url)
    # Connect the database if exists.
    db.connect()

Session = sessionmaker(bind=db)


@declarative_mixin
class BillMixin:
    __tablename__ = 'base'
    __table_args__ = {'postgresql_partition_by': 'range(congress)'}
    billnumber = Column(Integer, primary_key=True)
    originchamber = Column(Text)
    billtype = Column(Text, primary_key=True)
    introduceddate = Column(Date)
    congress = Column(Integer, primary_key=True)
    committees = Column(JSONB)
    actions = Column(JSONB)
    sponsors = Column(JSONB)
    cosponsors = Column(JSONB)
    policyarea = Column(Text)
    summary = Column(Text)
    title = Column(Text)


class s(BillMixin, Base):
    __tablename__ = 's'


class sconres(BillMixin, Base):
    __tablename__ = 'sconres'


class sjres(BillMixin, Base):
    __tablename__ = 'sjres'


class sres(BillMixin, Base):
    __tablename__ = 'sres'


class hr(BillMixin, Base):
    __tablename__ = 'hr'


class hconres(BillMixin, Base):
    __tablename__ = 'hconres'


class hjres(BillMixin, Base):
    __tablename__ = 'hjres'


class hres(BillMixin, Base):
    __tablename__ = 'hres'


Base.metadata.create_all(db)

tables = [s, hr, hconres, hjres, hres, sconres, sjres, sres]
with Session() as session:
    with session.bind.begin() as conn:
        for table in tables:
            for i in range(93, 120):
                conn.execute(
                    f"CREATE TABLE {table.__tablename__}_PARTITION_{i} PARTITION OF {table.__tablename__} FOR VALUES FROM ({i}) TO ({i + 1});")
                print(
                    f"CREATE TABLE {table.__tablename__}_PARTITION_{i} PARTITION OF {table.__tablename__} FOR VALUES FROM ({i}) TO ({i + 1});")
                conn.execute(f"CREATE INDEX ON {table.__tablename__}_partition_{i} (congress);")
            print(f"CREATE INDEX ON {table.__tablename__} (introduceddate);")
            conn.execute(f"CREATE INDEX ON {table.__tablename__} (introduceddate);")
