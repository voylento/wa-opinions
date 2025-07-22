#!/usr/bin/env python3
import sys
import csv
import math
from collections import Counter
from dat import settledcases

def standard_deviation(days_list):
    mean = sum(days_list) / len(days_list)
    variance = sum((x - mean) ** 2 for x in days_list) / (len(days_list))
    return math.sqrt(variance)

# Function to read and parse a tab-delimited file
def read_tab_delimited_file(file_path):
    data = []
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            data.append(row)
    return data

# Function to calculate the number of days between two dates
def main():
    if len(sys.argv) != 2:
        print("Usage: get_stats cases_decided.txt")
        sys.exit(1)

    cases_decided_file = sys.argv[1]

    cases_decided = read_tab_delimited_file(cases_decided_file)

    total_opinions = len(cases_decided)
    days_pub = []
    days_unpub = []
    days_unpub_oral = []
    days_unpub_nonoral = []
    total_pub = 0
    total_unpub = 0
    total_pub_oral = 0
    total_pub_nonoral = 0
    total_unpub_oral = 0
    total_unpub_nonoral = 0
    total_days_pub = 0
    total_days_pub_oral = 0
    total_days_pub_nonoral = 0
    total_days_unpub = 0
    total_days_unpub_oral = 0
    total_days_unpub_nonoral = 0
    highest_days_pub = 0
    highest_days_unpub = 0
    highest_days_unpub_had_oral = False

    for case in cases_decided:
        if case[0] in settledcases.settled_cases:
            continue
        opinion_type = case[4]
        had_oral_argument = case[3]
        number_days = int(case[5])
        
        if opinion_type == "PUB" or opinion_type == "PIP":
            total_pub += 1
            total_days_pub += number_days

            if had_oral_argument == "Yes":
                total_pub_oral += 1
                total_days_pub_oral += number_days
            else:
                total_pub_nonoral += 1
                total_days_pub_nonoral += number_days

            if number_days > highest_days_pub:
                next_highest_days_pub = highest_days_pub
                highest_days_pub = number_days

            days_pub.append(number_days)

        elif opinion_type == "UPUB":
            total_unpub += 1
            total_days_unpub += number_days

            if had_oral_argument == "Yes":
                total_unpub_oral += 1
                total_days_unpub_oral += number_days
                days_unpub_oral.append(number_days)
            else:
                total_unpub_nonoral += 1
                total_days_unpub_nonoral += number_days
                days_unpub_nonoral.append(number_days)

            if number_days > highest_days_unpub:
                next_highest_days_unpub = highest_days_unpub
                highest_days_unpub = number_days
                if had_oral_argument:
                    highest_days_unpub_had_oral = True
                else:
                    highest_days_unpub_had_oral = False

            days_unpub.append(number_days)

    days_pub.sort()
    days_pub.reverse()
    days_unpub.sort()
    days_unpub.reverse()
    days_unpub_oral.sort()
    days_unpub_oral.reverse()
    days_unpub_nonoral.sort()
    days_unpub_nonoral.reverse()

    print(f"Total Opinions: {total_opinions}")
    print(f"Total Published Opinions: {total_pub}")
    print(f"Total Published Opinions with oral argument: {total_pub_oral}")
    print(f"Total Published Opinions w/o oral argument: {total_pub_nonoral}")
    print(f"Max Days for Published Opinion: {highest_days_pub}")

    # get stats for published opinions
    n = len(days_pub)
    mean = round((sum(days_pub)/n), 1)
    mid = n // 2
    if n % 2 == 0:
        median = (days_pub[mid -1] + days_pub[mid]) / 2
    else:
        median = days_pub[mid]
    counter = Counter(days_pub)
    max_days = max(counter.values())
    mode_values = [k for k, v in counter.items() if v == max_days]
    mode_count = days_pub.count(mode_values[0])
    std_dev = standard_deviation(days_pub)
    print(f"Mean Days for Published Opinions: {mean}") 
    print(f"Median Days for Published Opinions: {median}")
    print(f"Mode Days for Published Opinions: {mode_values}, mode values occured {mode_count} times")
    print(f"Std Dev for Published Opinions: {round(std_dev, 1)}")
    top_ten = days_pub[0:10]
    print(f"Top 10 waits for published opinion: {top_ten}")

    print(f"Total Unpublished Opinions: {total_unpub}")
    print(f"Total Unpublished Opinions with oral argument: {total_unpub_oral}")
    print(f"Total Unpublished Opinions w/o oral arguemnt: {total_unpub_nonoral}")
    print(f"Max Days for Unpublished Opinion: {highest_days_unpub}")

    n = len(days_unpub_oral)
    mean = round(sum(days_unpub_oral)/n, 1)
    mid = n // 2
    if n % 2 == 0:
        median = (days_unpub_oral[mid - 1] + days_unpub_oral[mid]) / 2
    else:
        median = days_unpub_oral[mid]
    counter = Counter(days_unpub_oral)
    max_days = max(counter.values())
    mode_values = [k for k, v in counter.items() if v == max_days]
    mode_count = days_unpub_oral.count(mode_values[0])
    std_dev = standard_deviation(days_unpub_oral)
    print(f"Mean Days for Unpublished Opinion with oral argument: {mean}")
    print(f"Median Days for Unpublished Opinion with oral argument: {median}")
    print(f"Mode Days for Unpublished Opinion with oral argument: {mode_values}, mode values occurred {mode_count} times")
    top_ten = days_unpub_oral[0:10]
    print(f"Top 10 waits for unpublished opinion with oral argument: {top_ten}")
    
    n = len(days_unpub_nonoral)
    mean = round(sum(days_unpub_nonoral)/n, 1)
    mid = n // 2
    if n % 2 == 0:
        median = (days_unpub_nonoral[mid - 1] + days_unpub_nonoral[mid]) / 2
    else:
        median = days_unpub_nonoral[mid]
    counter = Counter(days_unpub_nonoral)
    max_days = max(counter.values())
    mode_values = [k for k, v in counter.items() if v == max_days]
    mode_count = days_unpub_nonoral.count(mode_values[0])
    std_dev = standard_deviation(days_unpub_nonoral)
    print(f"Mean Days for Unpublished Opinion w/o oral argument: {mean}")
    print(f"Median Days for Unpublished Opinion w/oral argument: {median}")
    print(f"Mode Days for Unpublished Opinion w/oral argument: {mode_values}, mode values occurred {mode_count} times")
    top_ten = days_unpub_nonoral[0:10]
    print(f"Top 10 waits for unpublished opinion w/o oral argument: {top_ten}")
    

if __name__ == "__main__":
    main()
                                                 
