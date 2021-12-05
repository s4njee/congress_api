from sqlalchemy import Text, Date, Column, Integer, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_mixin

db = create_engine('postgresql://postgres:postgres@localhost/congress')
Base = declarative_base()


# Connect the database
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




