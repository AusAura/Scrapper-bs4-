import aiohttp
import logging
import asyncio
from bs4 import BeautifulSoup
from aiohttp import ClientSession
import re

from conf import session as db_session
from conf import LOG_DIR
from models import Cars_used

url = "https://auto.ria.com/car/used/"
# url = 'https://auto.ria.com/uk/car/used/?page=29744'
start_url = url

# Настройка логгирования
logging.basicConfig(
    filename=LOG_DIR / "app.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    encoding="utf-8",
)


async def fetch_car(session: ClientSession, url: str) -> dict:
    logging.info(f"START FETCHING CAR LINK: {url}")
    if url == "javascript:void(0)":
        return {}
    async with session.get(url) as response:
        if response.status == 200:
            soup = BeautifulSoup(await response.text(), "lxml")
            try:
                title = soup.find("h1", class_="head").text.strip()
                price_usd = (
                    soup.find("div", class_="price_value")
                    .select_one("strong")
                    .text.replace("$", "")
                    .replace(" ", "")
                )
                price_usd = int(re.sub(r"\D", "", price_usd))
                odometer = soup.find("div", class_="base-information bold")
                odometer = int(odometer.select_one("span", class_="size18").text) * 1000
                username = soup.find("div", class_="seller_info_name bold")
                if username:
                    username = username.text.strip()
                else:
                    username = "Не вказано"
                phone_number = soup.find("span", class_="mhide").text
                image_url = soup.find("img", class_="outline m-auto")["src"]
                images_count = int(
                    soup.find("span", class_="count")
                    .select("span")[1]
                    .text.replace("з", "")
                    .strip()
                )
                car_number = soup.find("span", class_="state-num ua")
                if car_number:
                    car_number = car_number.text[:10]
                else:
                    car_number = "Не вказано"
                vin_number = soup.find("span", class_="label-vin")
                if vin_number:
                    vin_number = vin_number.text
                else:
                    vin_number = "Не вказано"

            except AttributeError as e:
                logging.error(f"Error parsing data from HTML: {e}")
                return {}

            except ValueError as e:
                logging.error(f"Error with the data, probably disabled car: {e}")
                return {}

            data = {
                "url_uq": url,
                "title": title,
                "price_usd": price_usd,
                "odometer": odometer,
                "username": username,
                "phone_number": phone_number,
                "image_url": image_url,
                "images_count": images_count,
                "car_number": car_number,
                "car_vin": vin_number,
            }

            logging.info(f"FETCHED A CAR: {data}")
            return data


async def fetch_page(session: ClientSession, url: str) -> tuple[list, list]:
    logging.info(f"START FETCHING: {url}")
    async with session.get(url) as response:
        logging.info(f"RESPONSE STATUS: {response.status}")
        if response.status == 200:
            soup = BeautifulSoup(await response.text(), "lxml")
            # logging.info(f"GOT SOUP: {soup}")
            cars = soup.find_all("section", class_="ticket-item")
            if not cars:
                logging.info(f"Seems like protection is working now: {soup}")
                cars = soup.find_all("a", class_="span3 item unlink")
            cars_data = []

            for i in range(0, len(cars)):
                car = cars[i].text
                car_url = cars[i].find("a").get("href")
                logging.info(f"FETCHED A CAR: {car}")
                logging.info(f"FETCHED THIS HREF: {car_url}")
                cars_data.append(await fetch_car(session, url=car_url))

            logging.info(f"GOT CARS: {cars_data}")
            return tuple(cars_data)


async def save_data(cars_data: list, db_session) -> None:
    for car in cars_data:
        if not car:
            continue
        car = Cars_used(**car)

        checked_car = (
            db_session.query(Cars_used).filter(Cars_used.url_uq == car.url_uq).first()
        )
        if not checked_car:
            db_session.add(car)
            db_session.commit()
            logging.info(f"ADDED A CAR: {car.url_uq}")
        else:
            logging.info(
                f"ALREADY EXISTS IN DB: {car.url_uq} with ID: {checked_car.id_pk}"
            )


async def main(url: str) -> None:
    async with aiohttp.ClientSession() as session:
        logging.info(f"PAGINATION INIT")

        while True:
            logging.info(f"START PAGE FETCH: {url}")
            cars = await fetch_page(session, url)
            if cars:
                await save_data(cars, db_session)

            response = await session.get(url)
            soup = BeautifulSoup(await response.text(), "html.parser")
            next_page = soup.find("span", class_="page-item next text-r")
            logging.info(f"LOOKING FOR NEXT PAGE: {next_page}")
            if not next_page:
                logging.info("NEXT PAGE NOT FOUND!")
                break

            next_url = next_page.a["href"]
            url = f"{next_url}"
            logging.info(f"TAKING NEW URL: {url}")


def run_script():
    logging.info(f"BEGIN!")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(url=url))
    logging.info(f"FINISHED!")


if __name__ == "__main__":
    run_script()
