# CSearch API
## Congress Data Notebook/Scripts

The goal of this repo is to create notebooks/scripts to parse the xml that is scraped by the [congress github](https://github.com/unitedstates/congress)
and store it in a postgresql database.

The notebook used for exploratory data analysis can be found [here](https://github.com/s4njee/congress_api/blob/main/scraper/data.ipynb).

The script sql_inserts in the scraper folder is configured to use sqlalchemy with postgres, and will scrape all the data in the data folder.  Please note
that the uncompressed .json and .xml files take up ~6gb of disk space.

The sqlalchemy models are defined in models.py, with db initialization code in init.py.  


## CSearch API



The api is a simple express server to connect to the postgresql database housing all the files. The scraper folder provides
the json parsing to insert the data from [unitedstates/congress](https://github.com/unitedstates/congress) into postgresql.

Alternatively a dump of the postgres database can be found on [dropbox](https://www.dropbox.com/s/twwno6q2m7ulcci/congress.dump?dl=0)

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

## k8s

There is a deployment.yaml file in the scraper subfolder. It is designed to work with
[crunchydata's postgres operator](https://access.crunchydata.com/documentation/postgres-operator/v5/quickstart/), though
there needs to be some work done on the init.py file to bootstrap the database correctly.

I have been developing using minikube, which to get the proper volume mount for the unitedstates/congress data folder in the
right spot requires this command

```bash
minikube start --driver=docker --mount-string="/home/sanjee/IdeaProjects/congress_api/congress/:/congress" --mount
```
where the congress folder is the unitedstates/congress github folder.

---

After the crunchydata postgres operator is installed, then
```bash
kubectl apply -f deployment.yaml 
```
will start the scraper and will update every 6 hours

