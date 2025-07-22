# WA-Opinions
Tool to get information on appellate cases before the Washington State Court of Appeals, Division 1

## Motivation
I became interested in following appellate court cases in Washington. In particular, I enjoy reading the opinions that get released. Beyond that, I am interested in seeing how long it takes the appellate court to process cases from between the time the assigned appellate court panel considers a case and the time they release an opinion. Pulling that information together is very tedious so I wrote some Python scripts to do it for me. These scripts create an html file for for cases that have an opinion released (cases_decided.html) and another html file (cases_waiting.html) for cases that are still waiting for an opinion. This program is run weekly and the files are uploaded to [Voylento.com -- cases_decided.html](https://voylento.com/cases_decided.html) and [Voylento.com -- cases_waiting.html](https://voylento.com/cases_waiting.html). 

## Dependencies
This project uses Selenium web driver and Chrome for Testing. As of this check in, only macOS amd64 is supported. Support for Windows (WLS/2) and Ubuntu are on the roadmap.


## Setup
First, install Chrome for Testing and the corresponding Selenium web driver:
```bash
python3 setup_cft.py
```

That should install the Chrome for Testing and Selenium web driver in the cft subdirectory. After that, install the Python dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

## Run
```base
./run
```

`run` is a bash script that runs a series of Python scripts and coreutils to download information about cases and then processe the data into two reports: cases_decided.html and cases_waiting.html

To run isolated parts of the process, look at the `run` shell program to see how it is stitched together.
