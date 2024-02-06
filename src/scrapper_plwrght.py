import asyncio
from playwright.async_api import async_playwright
import logging
import re

from conf import session as db_session
from models import Cars_used
from conf import WORK_DIR

# url = 'https://auto.ria.com/car/used/'
url = "https://auto.ria.com/uk/car/used/?page=29744"

# Настройка логгирования
logging.basicConfig(
    filename=WORK_DIR / "logs" / "app.log",
    filemode="a",
    format="%(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    encoding="utf-8",
)


async def fetch_car(page, url: str) -> dict:
    logging.info(f"START FETCHING CAR LINK: {url}")
    await page.goto(url)
    title = await page.query_selector(".head")
    title = await title.text_content()
    title = title.strip()
    price_usd = await page.query_selector(".price_value strong")
    price_usd = await price_usd.text_content()
    price_usd = int(re.sub(r"\D", "", price_usd))
    odometer = await page.query_selector(".base-information.bold span.size18")
    odometer = await odometer.text_content()
    odometer = int(odometer) * 1000
    username = await page.query_selector(".seller_info_name.bold")
    username = await username.text_content()
    phone_number = await page.query_selector(".mhide span")
    phone_number = await phone_number.text_content()
    image_url = await page.evaluate(
        '(document.querySelector("img.outline.m-auto")).src'
    )
    images_count = await page.query_selector(".count span:last-child")
    images_count = await images_count.text_content()
    images_count = int(images_count.replace("з", "").strip())
    car_number = await page.query_selector(".state-num.ua")
    car_number = await car_number.text_content()
    if car_number:
        car_number = car_number[:10]
    else:
        car_number = "Не вказано"
    vin_number = await page.query_selector(".label-vin")
    vin_number = await vin_number.text_content()
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


async def fetch_page(page, url: str) -> list:
    logging.info(f"START FETCHING: {url}")
    await page.goto(url)
    cars = await page.query_selector_all(".ticket-item")
    if not cars:
        cars = await page.query_selector_all(".span3 item unlink")
    cars_data = []

    for car in cars:
        car_text = await car.text_content()
        car_url = await car.query_selector("a")
        car_url = await car_url.get_attribute("href")
        logging.info(f"FETCHED A CAR: {car_text}")
        logging.info(f"FETCHED THIS HREF: {car_url}")
        cars_data.append(await fetch_car(page, url=car_url))

    logging.info(f"GOT CARS: {cars_data}")
    return cars_data


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
    async with async_playwright() as p:
        logging.info(f"PAGINATION INIT")
        browser = await p.chromium.launch()
        page = await browser.new_page()
        while True:
            logging.info(f"START PAGE FETCH: ", url)
            cars = await fetch_page(page, url)
            if cars:
                await save_data(cars, db_session)

            await page.goto(url)
            next_page = await page.query_selector("span.page-item.next.text-r")
            logging.info(f"LOOKING FOR NEXT PAGE: {next_page}")
            if not next_page:
                logging.info("NEXT PAGE NOT FOUND!")
                break

            next_url = await next_page.get_attribute("href")
            url = f"{next_url}"
            logging.info(f"TAKING NEW URL: {url}")
        await browser.close()


if __name__ == "__main__":
    logging.info(f"BEGIN!")
    asyncio.run(main(url=url))
    logging.info(f"FINISHED!")
