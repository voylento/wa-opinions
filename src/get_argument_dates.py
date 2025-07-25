#!/usr/bin/env python3

# Std library imports
import argparse
import calendar
import csv
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta 
from dateutil.relativedelta import relativedelta
import logging
import os
import re
import sys
import time

# 3rd party imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

# Local imports
from db_ops import get_connection, close_connection, update_metadata, insert_case_with_details
from driver_factory import create_driver

# This program loops through a subset of the Washington State Court of Appeals  hearing schedule and captures the information 
# I'm interested in, and writes the information to standard output. 
#
# For each day's docket, I pull out:
# - Case Number (Anchor case and consolidated cases if relevant)
# - Date of Consideration (I refer to this as oral arguments, but not all cases have oral arguments)
# - Whether the case has Oral argument or not
# - The judicial panel hearing the case (or considering it if no oral argument)
# - The case title

MIN_DATE = date(2012, 1, 1)

# Create a logs directory
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Create a log filename with timestamp
log_filename = datetime.now().strftime("scrape_%Y%m%d_%H%M%S.log")
log_path = os.path.join(LOG_DIR, log_filename)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path, mode='w', encoding='utf-8'),
        logging.StreamHandler() # want a console log too
    ]
)

@dataclass
class Division:
    division: int
    url: str
    output_file: str
    
divisions = [
    Division(
        division = 1, 
        url = "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=",
        output_file = "division_1_panel_info.tsv",
     ),
    Division(
        division = 2,
        url = "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a02&year=",
        output_file = "division_2_panel_info.tsv",
    ),
    Division(
        division = 3,
        url = "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a03&year=",
        output_file = "division_3_panel_info.tsv",
    ),
]

@dataclass
class CaseData:
    case_numbers: list[tuple[str, bool]]
    case_title: str
    argument_date: str
    panel: list[str]
    oral_argument: bool
    litigants: list[tuple[str, str]]
    attorneys: list[str]

    # future proof fields I can add later
    lower_court: str = ""
    lower_court_case_number: str = ""

def date1_less_than_date2(date1: str, date2: str) -> bool:
    d1 = datetime.strptime(date1, "%Y%m%d")
    d2 = datetime.strptime(date2, "%Y%m%d")
    return d1 < d2

def get_next_date(d: str) -> str:
    """
        Input: date string in the format yyyymmdd
        Output: day after the input date in yyyymmdd format
    """

    # Parse incoming date string
    dt = datetime.strptime(d, "%Y%m%d")
    # Add one day
    next_dt = dt + timedelta(days=1)
    # Return in the same format
    return next_dt.strftime("%Y%m%d")

def last_date_of_current_month() -> str:
    today = date.today()
    year = today.year
    month = today.month
    last_day = calendar.monthrange(year, month)[1]
    last_date = date(year, month, last_day)

    return last_date.strftime("%Y%m%d")

def last_day_of_next_month() -> date:
    today = date.today()
    first_next = (today.replace(day=1) + relativedelta(months=1))
    first_after = (first_next + relativedelta(months=1))
    return first_after - timedelta(days=1)

def last_day_of_current_year() -> date:
    today = date.today()
    # last day of current year is always 12/31, duh
    last_day = date(today.year, 12, 31)
    return last_day

def process_page(index, elements, argument_date, panel) -> list[CaseData]:
    """ 
        Processes the content looking for case information. There are 7 patterns we must be aware of:
        1. Case #, Title
        2. Case #, County Court, Title
        3. Case # (Anchor Case), Case # (Consolidated Case)+ 
        4. Case # (Anchor Case), County Court, Case # (Consolidated Case)+
        5. Panel, followed by one of patterns 1-4
        6. No Oral Argument, followed by one of patterns 1-4
        7. Panel, No Oral Argument, followed by one of patterns 1-4
    """
    # global cases
    # global panel
    # global is_oral_argument

    cases = []
    is_oral_argument = True

    while index < len(elements):
        line = elements[index].text.strip()
        if is_case_number(line):
            new_index, case = process_case(index, elements, argument_date, panel, is_oral_argument)
            cases.append(case)
            is_oral_argument = True # if case num if 1st in sequence, then there are oral arguments
            index = new_index
        elif is_no_oral_argument(line):
            is_oral_argument = False # if no oral arguments, that always listed before case #
            index += 1
        elif is_panel(line):
            panel = extract_panel(line) # if panel changes during day, that is noted before the case at which it changes
            index += 1                  # Also, I assume it lasts rest of day or until another noted panel change
        else:
            index += 1 # skip over lines that don't start a new case sequence

    return cases

def extract_litigants_attorneys(index, elements) -> tuple[list, list]:
    litigants = set()
    attorneys = set()

    target_table = None
    el = elements[index]
    text = el.text.strip()
    if text.startswith("Litigants"):
        target_table = el.find_element(By.XPATH, "./ancestor::table[1]")

    if target_table is not None:
        rows = target_table.find_elements(By.TAG_NAME, "tr")
        # skip header row
        for row in rows[1:]:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 2:
                raw_litigant = cols[0].text.strip()
                raw_attorney = cols[1].text.strip()
                if raw_litigant and raw_litigant != '\xa0' and raw_litigant != '&nbsp;':
                    m = re.match(r'^(.*?)\s*\((.*?)\)\s*$', raw_litigant)
                    if m:
                        name = m.group(1).strip()
                        role = m.group(2).strip()
                    else:
                        name = raw_litigant
                        role = ""
                    litigants.add((name, role))

                if raw_attorney and raw_attorney != '\xa0' and raw_attorney != '&nbsp;':
                    attorneys.add(raw_attorney)


    return list(litigants), list(attorneys)

def process_case(index, elements, argument_date, panel, is_oral_argument) -> CaseData:
    # Assumes that this is called when index points to a case number on the page

    # global argument_date
    # global panel
    # global is_oral_argument

    case_numbers = []
    litigants = []
    attorneys = []
    county_court_info = ""
    line = elements[index].text.strip()
    is_combined = is_combined_case(line)
    
    case_numbers.append(extract_case_number(line))
    index = index + 1

    # if it is a combined case, the first case listed is the anchor case and the cases listed
    # after are the cases consolidated into the anchor case
    if is_combined:
        line = elements[index].text.strip()
        if is_county_court_field(line):
            index = index + 1
            line = elements[index].text.strip()
        while is_case_number(line):
            case_numbers.append(extract_case_number(line))
            index = index + 1
            line = elements[index].text.strip()
    else:
        line = elements[index].text.strip()
        if is_county_court_field(line):
            county_court_info = line
            index = index + 1

    # Case title comes after Case number and County Court info
    title = elements[index].text.strip()
    index = index + 1
    
    # Litigants and Attorneys of Record are recorded in a table after the title
    line = elements[index].text.strip()
    if line.startswith("Litigants"):
        litigants, attorneys = extract_litigants_attorneys(index, elements)

    is_first = True
    augmented_case_numbers = []
    for num in case_numbers:
        if is_first:
            augmented_case_numbers.append((num, True))
            is_first = False
        else:
            augmented_case_numbers.append((num, False))

    case_data = CaseData(
        case_numbers=augmented_case_numbers,
        case_title=title,
        argument_date=argument_date,
        panel=panel,
        oral_argument=is_oral_argument,
        litigants=litigants,
        attorneys=attorneys,
        )
    
    return index + 1, case_data

def extract_title(line) -> str:
    return line.strip()

def is_argument_date(line) -> bool:
    if line[:5] == "Date:":
        return True
    else:
        return False
    
def extract_date(line) -> str:
    # Extract date from a field in the format: "Date: Thursday, September 10, 2024"
    if "Date: " in line:
        line = line.split("Date: ")[1].strip()

    date_obj = datetime.strptime(line, "%A, %B %d, %Y").date()
    return date_obj.strftime("%m/%d/%Y")

def is_panel(line) -> bool:
    if line[:7] == "Panel: ":
        return True
    else:
        return False

def extract_panel(line) -> list[str]:
    name_part = line.split("Panel: ")[1].strip()
    panel = name_part.split(",")
    return panel

def is_case_number(line) -> bool:
    data = line.strip()
    if len(data) < 6:
        return False  # case numbers have 6 digits, or 7 if the case number includes a '-' before last number

    if data[:6].isdigit():
        return True
    if data[:5].isdigit() and data[5] == '-' and data[6].isdigit():
        return True

    return False

def extract_case_number(line) -> str:
    return re.sub(r"\D", "", line)

def is_combined_case(line) -> bool:
    # Assumes field is a case # (without dash) and just checking if it ends with (Anchor Case)
    if "Anchor Case" in line:
        return True
    return False 

def is_consolidated_case(line) -> bool:
    # Assumes field is case # in format nnnnn-n and just checking if it ends with (Consolidated)
    if "Consolidated" in line:
        return True
    return False

def is_county_court_field(line) -> bool:
    if "Superior Court" in line:
        return True
    return False

def is_no_oral_argument(line) -> bool:
    if "No Oral Argument" in line:
        return True
    return False

def write_cases(report, filename):
    OUTPUT_DIR = "output"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(report)

def convert_cases_to_report(cases):
    report = []

    for case in cases:
        line_item = [
            case['case_numbers'][0],
            case['argument_date'],
            case['oral_argument'],
            case['panel'],
            case['case_title'],
            case['litigants'],
            case['attorneys'],
        ]
        report.append(line_item)
        # if multiple case numbers, print the consolidated case numbers
        # on their own line, with no other case data
        if len(case['case_numbers']) > 1:
            for num in range(1, len(case['case_numbers'])):
                report.append([case['case_numbers'][num]])


    return report

def write_cases_to_db(conn, div, cases):
    logging.info(f"Writing {len(cases)} cases for {cases[0].argument_date}")

    for case in cases:
        insert_case_with_details(
            conn,
            division=div,
            case_numbers=case.case_numbers,
            case_title=case.case_title,
            panel_date=case.argument_date,
            oral_arguments=case.oral_argument,
            judges=case.panel,
            litigants=case.litigants,
            attorneys=case.attorneys
            )

def process_cases(driver, url, division, start_dt, end_dt):
    conn = get_connection()
    try:
        while date1_less_than_date2(start_dt, end_dt):
            argument_date = None
            cases = []
            panel = []
            year = start_dt[:4]
            full_url = url + year + "&file=" + start_dt

            driver.get(full_url)

            # Sadly, a dearth of id attributes in the html.
            # All fields I want to capture are inside a strong tag. Not all fields inside a strong tag are fields I want to capture
            strong_elements = driver.find_elements(By.TAG_NAME, "strong")

            num_lines = len(strong_elements)

            if num_lines == 0: 
                start_dt = get_next_date(start_dt)
                continue

            # The header section of the page gives the date and day's judicial panel before listing
            # case details. Get that first.
            # Note: panels can change throughout the day and such changes are noted, but that is in the case data
            index = 0
            while len(panel) == 0 and index < num_lines:
                line = strong_elements[index].text.strip()
                # line = lines[index].strip()

                # have the content, increase index for next round, or for when we break
                index += 1 

                # argument date is first field we're interested in from the web page. read until we get it
                if argument_date == None:
                    if is_argument_date(line):
                        argument_date = extract_date(line)
                        continue # No need for more processing on this field
                    else:
                        continue # Keep going until we get to Date for appeals argument

                # panel is the next field we're interested in from the web page. read until we get it
                if len(panel) == 0:
                    if (is_panel(line)):
                        panel = extract_panel(line)
                        break   # once we have the panel, we can break out of the while loop
                                # to process the actual cases argued on this date

            # Now that we have the date and the judicial panel, get the actual cases
            cases = process_page(index, strong_elements, argument_date, panel)
            if len(cases) > 0:
                write_cases_to_db(conn, division, cases)
                conn.commit()
                update_metadata(f"last_processed_date_{division}", argument_date)

            start_dt = get_next_date(start_dt)
    finally:
        close_connection(conn)

def parse_date_arg(arg_value: str) -> date:
    try:
        return datetime.strptime(arg_value, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid date format: '{arg_value}'. Use YYYY-MM-DD."
        )

def main():
    parser = argparse.ArgumentParser(
        description="Scrape WA appellate cases between two dates."
    )
    parser.add_argument(
        "--start",
        required=True,
        type=parse_date_arg,
        help="Begin date (YYYY-MM_DD, not before 2012-01-01)"
    )
    parser.add_argument(
        "--end",
        required=True,
        type=parse_date_arg,
        help="End date (YYYY-MM-DD, not after last day of current year)"
    )

    args = parser.parse_args()
    begin_date: date = args.start
    end_date: date = args.end

    if begin_date < MIN_DATE:
        parser.error(f"Begin date cannot be before {MIN_DATE.isoformat()}")
    max_end = last_day_of_current_year()
    if end_date > max_end:
        parser.error(f"End date cannot be after {max_end.isoformat()}")
    if begin_date > end_date:
        parser.error("Begin date must be on or before end date.")

    start_dt = begin_date.strftime("%Y%m%d")
    end_dt = end_date.strftime("%Y%m%d")

    logging.info(f"Logging started. Writing to {log_path}")

    logging.info(f"✅ Using date range {start_dt} to {end_dt}.")

    driver = create_driver()
    
    try:
        for d in divisions: 
            logging.info(f"▶ Processing division {d.division} from {start_dt} to {end_dt}")
            process_cases(driver, d.url, d.division, start_dt, end_dt)
    except Exception as e:
        logging.exception(f"❌ Unhandled error: {e}")
    finally:
        driver.quit()

    logging.info("✅ Completed.")

if __name__ == "__main__":
    main()
