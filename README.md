# CSearch API
## Congress Data Notebook/Scripts

The goal of this repo is to create notebooks/scripts to parse the xml that is scraped by the [congress github](https://github.com/unitedstates/congress)
and store it in a postgresql database.

The notebook used for exploratory data analysis can be found [here](https://github.com/s4njee/congress_data/blob/main/data.ipynb).

The script sql_inserts in the scraper folder is configured to use sqlalchemy with postgres, and will scrape all the data in the data folder.
The contents of the data folder is compressed as **data.tar.zst** and requires **git lfs** due to its size. Please note
that the uncompressed .json and .xml files take up ~6gb of disk space when decompressed.

The sqlalchemy models are defined in models.py, and raw sql is executed at the end of the sql_inserts file to create 
full text search and indexes for them.


## CSearch API



The api is a simple express server to connect to the postgresql database housing all the files. The scraper folder provides
the json parsing to insert the data from [unitedstates/congress](https://github.com/unitedstates/congress) into postgresql.

Alternatively a dump of the postgres database can be found on [dropbox](https://dropbox.com/s/13lpfbwvigrcudr/congress.dump?dl=0)

Initialize and restore the database with these commands. The default password for postgres is postgres.
```bash
docker-compose up -d db
createdb -h localhost -U postgres congress
pg_restore -Fc -v -h localhost -U postgres congress.dump
```

The api can be run with the command, which will spawn a nodejs server on port 3001:
```bash
docker-compose up -d db node
```
