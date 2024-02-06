from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os, pathlib
from dotenv import load_dotenv

# loading .env
load_dotenv()

# Reading ENV variables
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_NAME = os.getenv("POSTGRES_NAME")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
BACKUP_DIR = os.getenv("BACKUP_DIR")
BACKUP_HOUR = os.getenv("BACKUP_HOUR")
BACKUP_EVERY_MINUTES = os.getenv("BACKUP_EVERY_MINUTES")
PARSING_HOUR = os.getenv("PARSING_HOUR")
PARSING_EVERY_MINUTES = os.getenv("PARSING_EVERY_MINUTES")

# dirs
WORK_DIR = pathlib.Path(__file__).parent.parent
LOG_DIR = WORK_DIR / "logs"
BACKUP_FIN_DIR = WORK_DIR / BACKUP_DIR.replace("/", "")

if not LOG_DIR.exists():
    # Creating if does not exist
    LOG_DIR.mkdir(parents=True, exist_ok=True)

if not BACKUP_FIN_DIR.exists():
    # Creating if does not exist
    BACKUP_FIN_DIR.mkdir(parents=True, exist_ok=True)

# Database engine/session
engine = create_engine(
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}"
)
DBsession = sessionmaker(bind=engine)
session = DBsession()
