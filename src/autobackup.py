import os
import time
import datetime
import logging

from conf import (
    POSTGRES_HOST,
    POSTGRES_NAME,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
    BACKUP_HOUR,
    BACKUP_EVERY_MINUTES,
    LOG_DIR,
    BACKUP_FIN_DIR,
)

# Logging configuration
logging.basicConfig(
    filename=LOG_DIR / "backup.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(message)s",
    level=logging.INFO,
    encoding="utf-8",
)


def backup_database():
    # Filename
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = f"{POSTGRES_NAME}_{timestamp}.sql"
    logging.info(f"Backup started: {backup_file}")

    # for exec command
    os.environ["PGPASSWORD"] = POSTGRES_PASSWORD

    # making pg_dump command
    dump_command = f"docker exec -t postgres-1 pg_dump --host {POSTGRES_HOST} --port {POSTGRES_PORT} --username {POSTGRES_USER} {POSTGRES_NAME} > {BACKUP_FIN_DIR / backup_file}"

    # executing command
    os.system(dump_command)

    logging.info(f"Backup file created successfully: {backup_file}")


if __name__ == "__main__":
    logging.info(f"Backup script started")

    # Infinite cycle to watch the timer
    while True:
        if (
            BACKUP_EVERY_MINUTES != "None"
            and datetime.datetime.now().minute % int(BACKUP_EVERY_MINUTES) == 0
        ):
            logging.info(f"Arming backup script, with interval {BACKUP_EVERY_MINUTES}")
            backup_database()
            time.sleep(60 * int(BACKUP_EVERY_MINUTES))
        elif BACKUP_HOUR == datetime.datetime.now().hour:
            logging.info(f"Arming backup script, timer set to {BACKUP_HOUR}")
            backup_database()
            time.sleep(86400)
