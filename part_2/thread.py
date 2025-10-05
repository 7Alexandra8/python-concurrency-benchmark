import json
import re
import threading
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from database import Trip, SessionLocal
import time
from datetime import datetime


def parse_and_save(url):
    start_time = time.time()

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string

    departure_location_element = soup.find("div", class_="tags")
    if departure_location_element:
        departure_location_element = departure_location_element.find("a", class_="tag has-icon-location")
    departure_location = departure_location_element.text.strip() if departure_location_element else "Unknown"

    date_option = soup.select_one("option[selected='selected']")
    if date_option:
        date_text = date_option.text.strip()
        if " — " in date_text and " " in date_text:
            start_day, end_month_year = date_text.split(" — ", maxsplit=1)
            end_day, month_year = end_month_year.split(" ", maxsplit=1)
            month_name, year = month_year.rsplit(maxsplit=1)
            months = {
                "января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6,
                "июля": 7, "августа": 8, "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
            }
            month = months.get(month_name, None)
            if month:
                start_date_str = f"{start_day} — {month} {year}"
                end_date_str = f"{end_day} {month} {year}"
                start_date = datetime.strptime(start_date_str, "%d — %m %Y")
                end_date = datetime.strptime(end_date_str, "%d %m %Y")
            else:
                print("Invalid month name:", month_name)
                start_date, end_date = None, None
        else:
            print("Date format not as expected.")
            start_date, end_date = None, None
    else:
        start_date, end_date = None, None

    duration_element = soup.select_one("p.heading:-soup-contains('Длительность') + p.title i.icon-duration")
    duration_text = duration_element.find_next_sibling(text=True).strip() if duration_element else None
    duration = int(duration_text) if duration_text and duration_text.isdigit() else None

    details_block = soup.find("div", class_="block mt-6")
    details = details_block.find("div").text.strip() if details_block else None

    print(f"Title of {url}: {title}")

    # Word count parsing
    word_count = {}
    if details:
        words = re.findall(r'\w+', details.lower())
        for word in words:
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1
        print("Word count:", word_count)

    db = SessionLocal()
    db.add(Trip(title=title, departure_location=departure_location,
                start_date=start_date, end_date=end_date,
                duration=duration, details=json.dumps(word_count)))
    db.commit()
    db.close()

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time for {url}: {execution_time} seconds")


urls = ["https://turclub-pik.ru/pohod/yaponiya-v-sezon-cveteniya-sakury/",
        "https://www.trip.com/travel-guide/attraction/tokyo/warner-bros-studio-tour-tokyo-the-making-of-harry-potter-136452473/?locale=en-XX&curr=USD",
        "https://turclub-pik.ru/pohod/elbrus-s-yuga-s-komfortom-s-otelem/#trip-4253",
        "https://www.tsarvisit.com/ru/visit/zimnie-katanija-na-sobach-ih-uprjazhkah-s-posescheniem-fermy-i-tradicionnym-obedom-671"
   ]

start_time = time.time()

threads = []

for url in urls:
    thread = threading.Thread(target=parse_and_save, args=(url,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

end_time = time.time()
total_execution_time = end_time - start_time
print(f"Total execution time for all threads: {total_execution_time} seconds")
