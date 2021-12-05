from sqlalchemy_utils import database_exists, create_database, drop_database
from models import Session, db, Base, s, hr, sconres, hjres, hres, hconres, sjres, sres


def initialize_db():
    if not database_exists(db.url):
        create_database(db.url)
    else:
        drop_database(db.url)
        create_database(db.url)
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
