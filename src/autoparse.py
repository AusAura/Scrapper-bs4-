import time
import datetime
import logging

from conf import PARSING_HOUR, PARSING_EVERY_MINUTES, LOG_DIR
from scrapper_bs4 import run_script

# Logging configuration
logging.basicConfig(
    filename=LOG_DIR / "backup.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(message)s",
    level=logging.INFO,
    encoding="utf-8",
)


if __name__ == "__main__":
    logging.info(f"Parsing script started")
    # Infinite cycle to watch the timer
    while True:
        if (
            PARSING_EVERY_MINUTES != "None"
            and datetime.datetime.now().minute % int(PARSING_EVERY_MINUTES) == 0
        ):
            logging.info(
                f"Arming parsing script, with interval {PARSING_EVERY_MINUTES}"
            )
            run_script()
            time.sleep(60 * int(PARSING_EVERY_MINUTES))
        elif PARSING_HOUR == datetime.datetime.now().hour:
            logging.info(f"Arming parsing script, timer set to {PARSING_HOUR}")
            run_script()
            time.sleep(86400)
