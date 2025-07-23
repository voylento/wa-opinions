
# Washington State Appellate Court Case Tracker

This is a tool that gathers information about appellate court cases in Washington State and compiles that information into html reports. 

## Motivation
I once saw a news article referring to an appellate court opinion. I looked up the opinion, read it, and found it interesting and started reading more appellate opinions. I have been surprised at the number of times I've been involved in discussions that touch on issues of law and how little I and other laymen understand about how law works. The more I read opinions, the more I realize how misinformed I and others often are about legal issues we read about, have friends or families impacted by, or face ourselves. Familiarity with appellate court opinions can disabuse us of a lot of the nonsense that clutters our minds about the law.  

As I learned more about our court system in Washington, I became more curious about how long cases take to wind through the appellate court system. Tracking that information is tedious so I decided to write some scripts to help me pull it all together. This project does that for me. For now, this code creates html reports that track when cases are scheduled for consideration before an appellate panel, when opinions are released, and a few other pieces of information. The report also includes links to the public opinions. This is a work in progress.

These scripts generate:
- **cases_decided.html** – cases with released opinions
- **cases_waiting.html** – cases that have been before an appellate panel and are still awaiting an opinion

I run this weekly and the results are uploaded to:
- [Voylento.com — cases_decided.html](https://voylento.com/cases_decided.html)
- [Voylento.com — cases_waiting.html](https://voylento.com/cases_waiting.html)

As of now, this only tracks Division 1. Other divisions will be added.

## Supported Platforms
✅ macOS (arm64) — tested  
✅ Ubuntu/Debian Linux (x86_64) — tested  
✅ Windows via WSL 2 with an Ubuntu distribution — tested  
❌ Other platforms/architectures — not currently supported

> **Note:** For Windows users, run this project inside WSL 2 with Ubuntu. The instructions below for Ubuntu apply.

## Dependencies
This project uses:
- [Chrome for Testing](https://developer.chrome.com/docs/chrome-for-testing/) and the matching [Chromedriver](https://chromedriver.chromium.org/)
- [Selenium](https://pypi.org/project/selenium/)

## Setup

### 1. Install Chrome for Testing and Chromedriver
Run the provided setup script, which will:
- Detect your platform
- Download the correct Chrome for Testing build
- Download the matching Chromedriver
- Place them into a `cft/` subdirectory

```bash
python3 setup_cft.py
```

### 2. Install required system packages (Linux/Ubuntu only)
On a minimal Ubuntu/Debian system, install these libraries first:

```bash
sudo apt update
sudo apt install -y curl unzip \
  libnss3 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 \
  libxdamage1 libxext6 libxi6 libxtst6 libxrandr2 libgbm1 \
  libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libgtk-3-0 \
  libasound2t64
```

These packages provide all the runtime libraries Chrome needs, even in headless mode.

### 3. Install Python dependencies
Create and activate a virtual environment, then install requirements:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run
Use the provided `run` script to execute the full workflow:

```bash
./run
```

This runs a series of Python scripts and coreutils to:
- Download current case data
- Process and merge the data
- Generate the reports: `cases_decided.html` and `cases_waiting.html`

## Running individual parts
To run isolated parts of the process, inspect the `run` shell script. It shows how the various Python scripts are stitched together.

## Contributions
I'm not taking contributions at this time as there are a number of core design and capability changes I intend to make.

## License
MIT License.
