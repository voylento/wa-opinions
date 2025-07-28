#!/usr/bin/env python3

# Std library imports
import argparse
from dataclasses import dataclass
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging
import os
import re

# 3rd party imports
from selenium.webdriver.common.by import By

# Local imports
from date_utils import date1_less_than_date2, get_next_date, last_day_of_current_year 
from db_ops import get_connection, close_connection, update_metadata, insert_case_with_details
from driver_factory import create_driver

# This program loops through a subset of the Washington State Court of Appeals hearing schedule, captures the information 
# I'm interested in, and writes the information to a sqlite database. 
#
# For each day's schedule, I pull out:
# - Case Number (Anchor case and consolidated cases if they exist)
# - Date of Consideration (I sometimes refer to this as arguments date in variable name, but not all cases have oral arguments)
# - Whether the case has Oral argument or not
# - The judicial panel considering the case
# - The Superior Court from which the case was appealed and the Superior Court case number (if present)
# - The case title
# - The litigants
# - The attorneys
# -
# - Having explored the data, I have found that not all cases that sit before a judicial panel for consideration, and have
# - an opinion released, show up in the public-facing schedule cases. For the period 2012-2025, that amounts to 6% of the
# - cases in Division 1, 5% in Division 2, and 3.5% in Division 3

# - Oral argument (consideration) schedules only availbe for 2012 and later.
MIN_DATE = date(2012, 1, 1)

# Create a logs directory off the root of the project
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Create a log filename with timestamp
log_filename = datetime.now().strftime("scrape_%Y%m%d_%H%M%S.log")
log_path = os.path.join(LOG_DIR, log_filename)

# Simple program, simple logging
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
    lower_court: str = ""
    lower_court_case_number: str = ""

def process_page(index: int, elements: list, argument_date: str, panel: list[str]) -> list[CaseData]:
    """ 
        Processes the content looking for case information. There are 7 patterns we must be aware of:
        1. Case #, Title
        2. Case #, County Court, Title
        3. Case # (Anchor Case), Case # (Consolidated Case)+ 
        4. Case # (Anchor Case), Lower Court, Case # (Consolidated Case)+
        5. Panel, followed by one of patterns 1-4
        6. No Oral Argument, followed by one of patterns 1-4
        7. Panel, No Oral Argument, followed by one of patterns 1-4
        
        Below are a couple live pages that capture most of the variety:
        https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2013&file=20130226
        https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2013&file=20130225
    """
    cases: list[CaseData] = []
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

def extract_litigants_attorneys(index: int, elements: list) -> tuple[list[tuple[str, str]], list[str]]:
    """
        Below is the stucture of the html that contains the litigant and attorney info. This 
        example is pulled from the 1st case on the page:

        https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2013&file=20130225

        Note that attorney names are listed on a per-litigant basis on the web page. I do not 
        track that. I just track which attorneys are associated with a case. This leads to 
        duplicate entries, but they are filtered out at the db layer. See case 682539 on the 
        link above to see what I mean.

        It is expected that when this function is called, elements[index] points to the first 
        row in the table, which is the heading row. If it isn't, we don't know the structure 
        we're dealing with so we return empty lists.

        <table width="80%" align="center">
			<tr>
                <td width="60%">
                    <strong>Litigants:</strong>
                </td>
                <td>
                    <strong>Attorneys of Record:</strong>
                </td>
            </tr>
				
            <tr>
                <td>Phonsavanh Phongmanivan (Appellant)</td>
                <td>Washington Appellate Project</td>
            </tr>
            <tr>
                <td>&nbsp;</td>
                <td>Gregory Charles Link</td>
            </tr>
            <tr>
                <td>&nbsp;</td>
                <td>Susan F Wilk</td>
            </tr>
            <tr>
                <td>&nbsp;</td>
                <td>David L. Donnan</td>
            </tr>
	        <tr>
                <td>State of Washington  (Respondent)</td>
				<td>Prosecuting Atty King County</td>
            </tr>
            <tr>
                <td>&nbsp;</td>
                <td>Dennis John Mccurdy</td>
            </tr>
		</table>
    """
    litigants: list[tuple[str, str]] = [] 
    attorneys: list[str] = []

    target_table = None
    el = elements[index]
    text = el.text.strip()
    if text.startswith("Litigants"):
        # Use XPath to find the parent table of this element so that
        # the code can traverse the rows 
        target_table = el.find_element(By.XPATH, "./ancestor::table[1]")

    if target_table is not None:
        # We have the table, loop through each row...
        rows = target_table.find_elements(By.TAG_NAME, "tr")
        # ...but skip the header row.
        for row in rows[1:]:
            cols = row.find_elements(By.TAG_NAME, "td")
            # Every row should have 2 columns. 1st col is litigant, 2nd is attorney. If there aren't 
            # 2 columns, something is off, just skip it.
            if len(cols) == 2:
                # In each row, litigant in the 1st column, attorney in the 2nd column
                raw_litigant = cols[0].text.strip()
                raw_attorney = cols[1].text.strip()
                # only process non-empty (e.g. &nbsp;) litigant entries
                if raw_litigant and raw_litigant != '\xa0' and raw_litigant != '&nbsp;':
                    # Capture name/role if available, e.g. John Doe (Defendant). If we don't
                    # capture both groups, put the whole string as the litigant name and set role to empty str
                    m = re.match(r'^(.*?)\s*\((.*?)\)\s*$', raw_litigant)
                    if m:
                        name = m.group(1).strip()
                        role = m.group(2).strip()
                    else:
                        name = raw_litigant
                        role = ""
                    litigants.append((name, role))

                # only process non-empty attorney entries. This should not happen given my understanding of
                # how the documents are structured, but there are thousands of pages and if it does happen 
                # just ignore.
                if raw_attorney and raw_attorney != '\xa0' and raw_attorney != '&nbsp;':
                    attorneys.append(raw_attorney)

    return litigants, attorneys

def process_case(index: int, elements: list, argument_date: str, panel: list[str], is_oral_argument: bool) -> tuple[int, CaseData]:
    """
        This function processes a single case on a schedule page. It is assumed that this function is 
        called when the index into the list of elements is at the case number. The argument date, judicial 
        panel, and question of whether consideration will include oral arguments should have already been
        processed (and passed in as arguments).

        Returns an index to the beginning of the next case to be processed and a CaseData object

        See 
        https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2013&file=20130225 
        for an example of case layouts within a page.
    """
    case_numbers: list[str] = []
    litigants: list[tuple[str, str]] = []
    attorneys: list[str] = []
    lower_court = ""
    lower_court_case_number = ""
    line = elements[index].text.strip()
    is_combined = is_combined_case(line)
    
    case_numbers.append(extract_case_number(line))
    index = index + 1

    # We have the case number. Now we need to see if the lower court and lower court case number
    # are available. After that, see if there are other appellate case numbers that are consolidated
    # into this case. See case 678256 on the webpage below as an example of the layout.
    #
    # https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2013&file=20130225
    line = elements[index].text.strip()
    # Oddly, the lower court (County court) are printed after the anchor case but before the consolidated case numbers. Skip it
    # and get the cases that follow.
    if is_lower_court_field(line):
        lower_court, lower_court_case_number = parse_lower_court_info(line)
        index = index + 1
    while is_case_number(line):
        case_numbers.append(extract_case_number(line))
        index = index + 1
        line = elements[index].text.strip()

    # Case title comes after Case number and County Court info
    title = elements[index].text.strip()
    index = index + 1
    
    # Litigants and Attorneys of Record are recorded in a table after the title
    line = elements[index].text.strip()
    if line.startswith("Litigants"):
        litigants, attorneys = extract_litigants_attorneys(index, elements)

    # In the database, we mark which case number is the primary case number as that
    # is the case number that will predominately be searched against.
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
        lower_court=lower_court,
        lower_court_case_number=lower_court_case_number
        )
    
    return index + 1, case_data

def is_argument_date(line: str) -> bool:
    if line[:5] == "Date:":
        return True
    else:
        return False
    
def extract_date(line: str) -> str:
    # Extract date from a field in the format: "Date: Thursday, September 10, 2024"
    if "Date: " in line:
        line = line.split("Date: ")[1].strip()

    date_obj = datetime.strptime(line, "%A, %B %d, %Y").date()
    return date_obj.strftime("%m/%d/%Y")

def is_panel(line: str) -> bool:
    if line[:7] == "Panel: ":
        return True
    else:
        return False

def extract_panel(line: str) -> list[str]:
    name_part = line.split("Panel: ")[1].strip()
    panel = name_part.split(",")
    return panel

def is_case_number(line: str) -> bool:
    data = line.strip()
    if len(data) < 6:
        return False  # case numbers have 6 digits, or 7 if the case number includes a '-' before last number

    if data[:6].isdigit():
        return True
    if data[:5].isdigit() and data[5] == '-' and data[6].isdigit():
        return True

    return False

def extract_case_number(line: str) -> str:
    return re.sub(r"\D", "", line)

def is_combined_case(line: str) -> bool:
    # Assumes field is a case # (without dash) and just checking if it ends with (Anchor Case)
    if "Anchor Case" in line:
        return True
    return False 

def is_consolidated_case(line: str) -> bool:
    # Assumes field is case # in format nnnnn-n and just checking if it ends with (Consolidated)
    if "Consolidated" in line:
        return True
    return False

def is_lower_court_field(line: str) -> bool:
    if "Superior Court" in line:
        return True
    return False

def parse_lower_court_info(lower_court_text: str) -> tuple[str, str]:
    # Here is an example of how the lower court information is 
    # provided (parens mine): 'King County Superior Court     10-3-05604-5'
    parts = lower_court_text.strip().rsplit(None, 1)
    if len(parts) == 2:
        court_name, case_number = parts[0], parts[1]
        # Sanity check: case number shouldn't contain "Court"
        if "Court" not in case_number:
            return court_name, case_number

    # Fallback: couldn't reliably parse
    return lower_court_text.strip(), ""

def is_no_oral_argument(line: str) -> bool:
    if "No Oral Argument" in line:
        return True
    return False

def write_cases_to_db(conn, div: int, cases: list[CaseData], argument_date: str) -> None:
    # the logging here is to give the user validation that the program is running. 
    logging.info(f"Writing {len(cases)} cases for {cases[0].argument_date}")
    exception_count = 0

    with conn: # context manager opens a transaction and will commit/rollback automatically
        for case in cases:
            try:
                insert_case_with_details(
                    conn=conn,
                    division=str(div),  # Convert int to str
                    case_numbers=case.case_numbers,
                    case_title=case.case_title,
                    panel_date=case.argument_date,
                    oral_arguments=case.oral_argument,
                    judges=case.panel,
                    litigants=case.litigants,
                    attorneys=case.attorneys,
                    lower_court=case.lower_court,
                    lower_court_case_number=case.lower_court_case_number
                )
            except Exception as e:
                exception_count += 1
                first_num = case.case_numbers[0] if case.case_numbers else "UNKNOWN"
                logging.error(
                    f"❌ Unhandled error writing case {first_num}: {e} "
                    f"(division {div}, date {case.argument_date})",
                    exc_info=True
                )
                if exception_count > 5:
                    logging.exception(
                        "❌ More than 5 exceptions attempting to write cases to database. Aborting batch."
                    )
                    raise # triggers automatic rollback

    update_metadata(f"last_processed_date_{div}", argument_date)


def process_cases(driver, url: str, division: int, start_dt: str, end_dt: str) -> None:
    conn = get_connection()
    try:
        while date1_less_than_date2(start_dt, end_dt):
            argument_date: str | None = None
            cases: list[CaseData] = []
            panel: list[str] = []
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
                if argument_date is None:
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
            if argument_date is not None:  # Only process if we have a valid date
                cases = process_page(index, strong_elements, argument_date, panel)
                if len(cases) > 0:
                    write_cases_to_db(conn, division, cases, argument_date)

            start_dt = get_next_date(start_dt)
    finally:
        close_connection(conn)

def parse_date_arg(arg_value: str) -> date:
    """
        Input: date as string in yyyymmdd format
        Output: date object 
    """
    try:
        return datetime.strptime(arg_value, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid date format: '{arg_value}'. Use YYYY-MM-DD."
        )

def parse_begin_end_dates(parser) -> [date, date]:
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


    begin_date = args.start
    if begin_date < MIN_DATE:
        parser.error(f"Begin date cannot be before {MIN_DATE.isoformat()}")

    end_date = args.end
    max_end = last_day_of_current_year()
    if end_date > max_end:
        parser.error(f"End date cannot be after {max_end.isoformat()}")

    if begin_date > end_date:
        parser.error("Begin date must be on or before end date.")

    return begin_date, end_date

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape WA appellate cases between two dates."
    )
    begin_date, end_date = parse_begin_end_dates(parser)

    start_dt = begin_date.strftime("%Y%m%d")
    end_dt = end_date.strftime("%Y%m%d")

    logging.info(f"Logging started. Writing to {log_path}")
    logging.info(f"✅ Using date range {start_dt} to {end_dt}.")

    driver = create_driver()
    
    try:
        # Process per appellate division because each divisioin has a slightly different url
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
