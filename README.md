# Scrapper Auto.RIA

This Python application is made to parse auto.ria website with BeautifulSoup4 and store result in PostgreSQL DB (psycopg2).
Additionally, the application and DB are run in a Docker containers that being orchestrated with Docker Compose.

Structure:
- scrapper_bs4.py -> main module which do all the scrapping, based on BeautifulSoup4 + Aiohttp for Async client requests
- scrapper_plwrght.py -> test version of the same module that is based on Playwright. It is not intended to work completely correct.
- conf.py -> sets up database, env variables and other configurations
- autobackup.py -> script for automatic backup dumps
- autoparse.py -> script for automatic parsing

Folders:

- /dumps (by default) -> stores DB dump files
- /logs -> stores logs
- /src -> stores modules

Instructions:
1) Clone the repository.
2) Adapt settings in .env file and docker-compose.yml to your needs.

The database will be created based on these parameters + BACKUP_DIR could be changed to any other name.
You can set either a specific hour for scripts to perform (BACKUP_HOUR for backups, PARSING_HOUR for parsing) or interval in minutes (BACKUP_EVERY_MINUTES, PARSING_EVERY_MINUTES). Be notified that intervals ALWAYS count from 00, means that if set to 5 minutes, script will be executed at 00, 05, 10, 15... minutes.

3) Run Docker Engine.
4) Run 'docker-compose up' in CLI in the application directory.
5) Wait until containers will be ready to work.

6) In some cases, app container tries to connect to DB when PostgreSQL container is not compeltely up yet. So check and re-run app container if it had any connection errors.