from sqlalchemy_utils import database_exists, create_database, drop_database
from models import Base, s, hr, sconres, hjres, hres, hconres, sjres, sres
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
import os
import asyncio

db = create_async_engine(f"postgresql+asyncpg://postgres:postgres@db:5432/csearch")


def get_db_session():
    # Connect the database
    Session = sessionmaker(
        db, expire_on_commit=False, class_=AsyncSession
    )
    db.connect()
    return Session


def initialize_db():
    Session = sessionmaker(
        db, expire_on_commit=False, class_=AsyncSession
    )
    # Try creating the tables and indices, if fails, then db likely already bootstrapped.
    try:
        Base.metadata.create_all(db)

        db.connect()
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
                    print(f"CREATE INDEX ON {table.__tablename__} (status_at);")
                    conn.execute(f"CREATE INDEX ON {table.__tablename__} (status_at);")

                    ## Build tsvectors and indices for full-text search
                    billType = table.__tablename__
                    print(f"Generating full text search column and index")
                    print(
                        f"ALTER TABLE {billType} ADD COLUMN {billType}_ts tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(title,'') || ' ' || coalesce(summary,''))) STORED;")
                    conn.execute(
                        f"ALTER TABLE {billType} ADD COLUMN {billType}_ts tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(title,'') || ' ' || coalesce(summary,''))) STORED;")
                    print(f"CREATE INDEX {billType}_ts_idx ON {billType} USING GIN ({billType}_ts);")
                    conn.execute(f"CREATE INDEX {billType}_ts_idx ON {billType} USING GIN ({billType}_ts);")
    except:
        pass
