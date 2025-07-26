#!/usr/bin/env python3

import argparse
import calendar
import csv
from datetime import datetime, date
import logging
import os
import re
import sys
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from driver_factory import create_driver

MIN_DATE = date(2013, 1, 1)

results = []
opinions_url = "https://www.courts.wa.gov/opinions/" 

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
output_filename = os.path.join(OUTPUT_DIR, "opinions.tsv")

# Create a logs directory
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Create a log filename with timestamp
log_filename = datetime.now().strftime("opinion_scrape_%Y%m%d_%H%M%S.log")
log_path = os.path.join(LOG_DIR, log_filename)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path, mode='w', encoding='utf-8'),
        logging.StreamHandler() # want a console log too
    ]
)

def get_opinions_for_date_range(driver, begin_dt, end_dt):
    global results
    global opinions_url

    driver.get(opinions_url)

    court_level = Select(driver.find_element(By.NAME, "courtLevel"))
    court_level.select_by_visible_text("Court of Appeals Only")

    begin_date = driver.find_element(By.NAME, "beginDate")
    begin_date.send_keys(begin_dt)

    end_date = driver.find_element(By.NAME, "endDate")
    end_date.send_keys(end_dt)

    search_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    search_button.click()

    driver.implicitly_wait(1)

    group_header = "Court of Appeals Opinions"

    # Sadly, there are no ids or other elements that make it easy to grab the information
    # desired. Must use XPATH.
    h3_element = driver.find_element(By.XPATH, "//h3[contains(text(), 'Court of Appeals Opinions')]")

    # The webpage normally has 3 tables, in the following order: Opinions Published in Part,
    # Published Opinions, and Unpublished Opinions. There are no identifiers in the html to 
    # directly access those tables. However, they are all preceded by a table header in the format:
    # <p><strong>Table Name</strong></p>, where Table Name is "Opinions Published in Part", "Published
    # Opinions", or "Unpublished Opinions". Our XPATH uses the <p><strong></strong><p> elements
    # to find the tables
    p_elements = h3_element.find_elements(By.XPATH, "following-sibling::p[strong]")

    for p_element in p_elements:
        opinion_type = p_element.find_element(By.XPATH, ".//strong").text.strip()
    
        tables = p_element.find_elements(By.XPATH, "following-sibling::table[1]")

        # there are some p_elements that get captured by our xpath that are not the ones we want. We can tell
        # which they are because they are not followed by a table
        if len(tables) == 0:
            continue

        table = tables[0]

        #Extract all rows except the table header row
        rows = table.find_elements(By.XPATH, ".//tr[position() > 1]")

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 5: # Ensure the right number of columns exist
                filing_date = cells[0].text
                # If it is the header row, continue
                if filing_date == "File Date":
                    continue

                case_info = cells[1].text
                division = cells[2].text
                case_title = cells[3].text

                #print(f"{filing_date} {division} {case_title}")

                try:
                    # Parse the date string (handles "Jan. 25, 2025" format)
                    parsed_date = datetime.strptime(filing_date, "%b. %d, %Y")
                    
                    # Convert to desired format mm/dd/yyyy
                    file_date = parsed_date.strftime("%m/%d/%Y")
                except ValueError:
                    # Keep original date string if parsing fails
                    logging.info(f"Error parsing date for {filing_date}")
                    pass
                    
                if opinion_type == "Opinions Published in Part":
                    opinion_TLA = "PIP"
                elif opinion_type == "Published Opinions":
                    opinion_TLA = "PUB"
                elif opinion_type == "Unpublished Opinions":
                    opinion_TLA = "UPUB"

                case_num = re.sub(r"\D", "", case_info.rstrip())
                appellate_div = division.rstrip()
                results.append(
                        [
                         file_date.rstrip(),
                         case_num,
                         appellate_div,
                         opinion_TLA,
                         f"{case_title.rstrip()}"
                        ])

def write_opinions_to_file(data, filepath):
    data_sorted = sorted(data, key=lambda x: datetime.strptime(x[0], "%m/%d/%Y"))
    with open(filepath, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(data_sorted)

def generate_date_range_for_year(year: int) -> list[dict[str, str]]:
    """
        Input: a year 
        Output: a list with an entry for each month that contains the first day
                of the month and last day of the month in mm/dd/yyyy format
    """
    result = []
    for month in range(1, 13):
        _, last_day = calendar.monthrange(year, month)
        begin_str = f"{month:02d}/01/{year}"
        end_str = f"{month:02d}/{last_day:02d}/{year}"
        result.append({"begin": begin_str, "end": end_str})
    
    return result

def parse_year(arg_value: str) -> int:
    try:
        this_year = date.today().year
        year = int(arg_value)
        if year < 2012 or year > this_year:
            raise argparse.ArgumentTypeError(
                f"Year out of range: '{arg_value}'. Enter year between 2012 and {this_year}."
            )
        return year
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"Invalid year format: '{arg_value}'. Enter year between 2012 and {this_year}."
        )

def parse_args() -> str:
    parser = argparse.ArgumentParser(
        description="Scrape WA appellate opinion releases for a given year."
    )
    parser.add_argument(
        "--year",
        required=True,
        type=parse_year,
        help="Year for which to scrape opinion data (YYYY)"
    )

    args = parser.parse_args()
    return args.year

def main():
    global results

    year = parse_args()
    date_range = generate_date_range_for_year(year)

    try:
        driver = create_driver()
        
        # The opinions website is limited to 200 results. Thus, we query for
        # one month at a time. Max I've seen for a month is around 120 results
        # for date_range in opiniondates.date_groups:
        logging.info(f"Getting opinions for {year}...")
        jan = date_range[0]
        # for month in date_range:
        get_opinions_for_date_range(driver, jan['begin'], jan['end'])
        write_opinions_to_file(results, output_filename)
    except Exception as e:
        logging.exception(f"❌ Unhandled error: {e}")
    finally:
        driver.quit()

    # write_opinions_to_file(results, output_filename)
    logging.info("✅ Successfully retrieved opinions.")

if __name__ == '__main__':
    main()
