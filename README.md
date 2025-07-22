# opinions
- Tool to get information on docket for Washington State Court of Appeals, Division 1

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

## NOTE
This project uses Selenium Chrome driver to open Chrome and navigate the pages. Chrome must be installed on the machine and the selenium driver and chrome version must match.

## Get the Oral Arguments Schedule
```bash
source venv/bin/activate
./get_argument_dates >  schedule.txt
deactivate
```

## Get the Opinions
```bash
source venv/bin/activate
./get_opinions > opinions.txt
deactivate
```

## Reconcile cases schedule against opinions to create cases decided report
```bash
source venv/bin/activate
./reconcile.py schedule.txt opinions.txt > cases_decided.txt
deactivate
```

## Aggregate stats from cases_decided report
```bash
./get_stats cases_decided.txt > stats.txt
```

## Consolidate cases decided report and stats into html page
```bash
./to_html.py cases_decided.txt stats.txt > cases_decided.html
```

## Create report showing cases considered and still awaiting an opinion
```bash
awk 'NF > 1 {print  $1}' schedule.txt > cases_argued.txt
grep -vf <(awk '{print $1}' cases_decided.txt | sort -u) <(sort -u cases_argued.txt) missing_opinions.txt
grep -f missing_opinions.txt schedule.txt > cases_waiting.txt
./missing_to_html.py cases_waiting.txt > cases_waiting.html
```

## Remove intermediary files
```bash
rm schedule.txt opinions.txt cases_decided.txt stats.txt cases_argued.txt missing_opinions.txt cases_waiting.txt
```

## Do all the steps above (less Setup) and open the html reports
```bash
./run
```
