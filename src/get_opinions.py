#!/usr/bin/env python3

import argparse
import calendar
from dataclasses import dataclass
from datetime import datetime, date
import logging
import os
import re

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import Select

from db_ops import get_connection, close_connection, update_case_opinion, insert_case_with_details 
from driver_factory import create_driver

# This program loops through the Washington State Court of Appeals Opinions Release page, which is shown
# in the global variable opinions_url. That page seems to be limited to showing 200 results, so this
# program structures searches on the month boundary. To date, I have never seen a month with more than
# 170 opinion releases. 
#
# It is expected that the appellate court scheduling program has been run prior to running this program
# and that all cases referred to in the opinion release pages have already been scraped from the schedules
# pages and entered into the db. This program updates those db entries to include the opinion release date
# and the opinion type (e.g. published, unpublished, or published in part)
#
# Initially the programs only allowed scraping data for 2024 and beyond. When I extended the functionality
# to start scraping from the earliest date that WA COA supported, I found that some cases that show up on
# the opinions release pages never appeared in the public scheduling pages. In this case, I insert as much
# information into the db, reasoning that partial information is better than no information.
#
# Queries before 2013 are always empty, so we make the minimum date Jan 1, 2013.

MIN_DATE = date(2013, 1, 1)

opinions_url = "https://www.courts.wa.gov/opinions/" 

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

@dataclass(slots=True)
class Opinion:
    case_number: str
    case_title: str
    division: str
    opinion_date: str
    opinion_type: str

def update_opinions_in_db(opinions: list[Opinion], begin_dt: str, end_dt: str) -> None:
    if len(opinions) > 199:
        logging.warning(f"⚠️ Warning! 200 opinions this month and website only returns 200 max. May be missing opinions.")
    else:
        logging.info(f"Updating opinions for {len(opinions)} cases for period {begin_dt} to {end_dt}")
    exception_count = 0

    conn = get_connection()

    with conn:  # automatic transaction
        for op in opinions:
            try:
                updated = update_case_opinion(conn, op.case_number, op.opinion_date, op.opinion_type)
                if not updated:
                    logging.info(
                        f"ℹ️ No matching case found for opinion update: "
                        f"{op.case_number} ({op.opinion_date}, {op.opinion_type}) "
                        f"Inserting as new case with incomplete information."
                    )
                    # I found some instances, espicially in cases over a decade ago, in which there are
                    # cases in the opinions release pages for which we never found a consideration date. 
                    # Example: 673688, division 1. A case with incomplete information is better than not 
                    # having it at all, so insert it.
                    insert_case_with_details(
                        conn=conn,
                        division=op.division,
                        case_numbers=[(op.case_number,False)],
                        case_title=op.case_title,
                        panel_date="",
                        oral_arguments=False,
                        judges=[],
                        litigants=[],
                        attorneys=[],
                        lower_court="",
                        lower_court_case_number=""
                    )
            except Exception as e:
                exception_count += 1
                logging.error(
                    f"❌ Error updating opinion for case {op.case_number} "
                    f"({op.opinion_date}, {op.opinion_type}): {e}",
                    exc_info=True
                )
                if exception_count > 5:
                    logging.exception(
                        "❌ More than 5 exceptions while updating opinions. Aborting."
                    )
                    raise  # triggers automatic rollback

    close_connection(conn)

def get_opinions_for_date_range(driver: WebDriver, begin_dt: str, end_dt: str) -> None:
    results: list[Opinion] = []

    driver.get(opinions_url)

    # The WA COA opinions release page require that you search based on start
    # date and end date. I have found that entering a period of longer than a month
    # may result in cases being missed, so the program searches on month blocks
    court_level = Select(driver.find_element(By.NAME, "courtLevel"))
    # some day I'll add Supreme Court cases to the program, but just COA for now.
    court_level.select_by_visible_text("Court of Appeals Only")

    begin_date = driver.find_element(By.NAME, "beginDate")
    begin_date.send_keys(begin_dt)

    end_date = driver.find_element(By.NAME, "endDate")
    end_date.send_keys(end_dt)

    search_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    search_button.click()

    driver.implicitly_wait(1)

    # Sadly, there are no ids or other elements that make it easy to grab the information
    # desired. Must use XPATH.

    # First, it is possible no search results were returned. Let's check for the first.
    try:
        element = driver.find_element(By.XPATH, "//*[contains(text(), 'No opinions matched the entered search criteria')]")
        # There is text telling us there were no opinions for this date range. Log it and move on
        logging.info(f"ℹ️ No opinions for the time period {begin_dt} to {end_dt}")
        return
    except NoSuchElementException:
        # do nothing, just continue
        pass

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

                try:
                    # Parse the date string (handles "Jan. 25, 2025" format) and convert to mm/dd/yyyy
                    parsed_date = datetime.strptime(filing_date, "%b. %d, %Y")
                    file_date = parsed_date.strftime("%m/%d/%Y")
                except ValueError:
                    # Keep original date string if parsing fails
                    logging.error(f"Error parsing date for {filing_date}")
                    pass
                    
                if opinion_type == "Opinions Published in Part":
                    opinion_type_text = "Published in Part"
                elif opinion_type == "Published Opinions":
                    opinion_type_text = "Published"
                elif opinion_type == "Unpublished Opinions":
                    opinion_type_text = "Unpublished"

                # just the digits, please
                case_num = re.sub(r"\D", "", case_info.rstrip())
                appellate_div = division.rstrip()
                # Decimal, not Roman, thank you.
                if appellate_div == "I":
                    appellate_div = "1"
                elif appellate_div == "II":
                    appellate_div = "2"
                elif appellate_div == "III":
                    appellate_div = "3"

                results.append(
                    Opinion(
                        case_number=case_num, 
                        case_title=case_title,
                        division=appellate_div,
                        opinion_date=file_date, 
                        opinion_type=opinion_type_text
                    )
                )

    update_opinions_in_db(results, begin_dt, end_dt)

def generate_date_range_for_year(year: int) -> list[dict[str, str]]:
    """
        Input: a year 
        Output: a list with an entry for each month that contains the first day
                of the month and last day of the month in mm/dd/yyyy format

        NOTE: After running for 2013 through 2025 in late July 2025, I found a single 
        month--April 2020--has 200 opinions. Since the site will only display up to 200, there may have been
        more. I hard-coded a special case for April 2020.
    """
    result = []
    for month in range(1, 13):
        _, last_day = calendar.monthrange(year, month)
        if year == 2020 and month == 4:
            begin_str = f"{month:02d}/01/{year}"
            end_str = f"{month:02d}/15/{year}"
            result.append({"begin": begin_str, "end": end_str})
            begin_str = f"{month:02d}/16/{year}"
            end_str = f"{month:02d}/30/{year}"
            result.append({"begin": begin_str, "end": end_str})
        else:
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

def parse_args() -> int:
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

def main() -> None:
    # Only support scraping per year. It is assumed a full db is being built out. There are practical reasons
    # for not allowing the user to auto scrape more than a year in one invocation, and practical reasons not
    # to support less. It is my compromise. Works for me. Doubt anyone else will ever use this.
    year = parse_args()
    date_range = generate_date_range_for_year(year)

    try:
        driver = create_driver()
        
        # The opinions website is limited to 200 results. Thus, we query for
        # one month at a time. Max I've seen for a month is around 150 results
        # for date_range in opiniondates.date_groups:
        logging.info(f"Getting opinions for {year}...")
        # for month in date_range:
        for month in date_range:
            get_opinions_for_date_range(driver, month['begin'], month['end'])
    except Exception as e:
        logging.exception(f"❌ Unhandled error: {e}")
    finally:
        driver.quit()

    # write_opinions_to_file(results, output_filename)
    logging.info("✅ Successfully retrieved opinions.")

if __name__ == '__main__':
    main()
