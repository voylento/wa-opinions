#!/usr/bin/env python3

import sys
import csv
from datetime import datetime

# Function to read and parse a tab-delimited file
def read_tab_delimited_file(file_path):
    data = []
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            data.append(row)
    return data

# Function to calculate the number of days between two dates
def days_between_dates(date1, date2):
    date_format = "%m/%d/%Y"
    d1 = datetime.strptime(date1, date_format)
    d2 = datetime.strptime(date2, date_format)
    return abs((d2 - d1).days)

def main():
    if len(sys.argv) != 3:
        print("Usage: reconcile.py oral_argument_schedule.txt opinions.txt")
        sys.exit(1)

    oral_arguments_schedule_file = sys.argv[1]
    opinions_file = sys.argv[2]

    oral_arguments_schedule = read_tab_delimited_file(oral_arguments_schedule_file)
    opinions = read_tab_delimited_file(opinions_file)

    opinions_dict = {row[1]: row for row in opinions}
    
    output_data = []
    for oral_arg in oral_arguments_schedule:
        case_number = oral_arg[0]
        if case_number in opinions_dict:
            oral_arg_date = oral_arg[1]
            # It is called the oral argument schedule, but it is really the "consideration date". Not all
            # cases have oral arguments. Some are considered by the appellate panel without oral argument
            included_oral_arguments = oral_arg[2]
            opinion_release_date = opinions_dict[case_number][0]
            opinion_type = opinions_dict[case_number][3]
            case_title = opinions_dict[case_number][4]

            # Calculate days between oral argument and opinion release
            days = days_between_dates(oral_arg_date, opinion_release_date)

            output_data.append([
                case_number,
                oral_arg_date,
                opinion_release_date,
                included_oral_arguments,
                opinion_type,
                days,
                case_title
            ])

    # Sort output data by the opinion release date
    output_data_sorted = sorted(output_data, key=lambda x: datetime.strptime(x[2], "%m/%d/%Y"), reverse=True)

    writer = csv.writer(sys.stdout, delimiter='\t', lineterminator='\n')
    writer.writerows(output_data_sorted)

if __name__ == "__main__":
    main()
                                                 
