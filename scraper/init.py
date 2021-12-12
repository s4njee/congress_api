from sqlalchemy_utils import database_exists, create_database, drop_database
from models import Base, s, hr, sconres, hjres, hres, hconres, sjres, sres
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

db = create_engine(
    f"{os.environ['DB_URI']}")


def get_db_session():
    # Connect the database
    Session = sessionmaker(bind=db)
    db.connect()
    return Session


def initialize_db():
    Session = sessionmaker(bind=db)

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
