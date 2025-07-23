
# WA‑Opinions

Tool to gather information on appellate cases before the Washington State Court of Appeals, Division 1.

## Motivation
I became interested in following appellate court cases in Washington. In particular, I enjoy reading the opinions that get released. Beyond that, I wanted to see how long it takes the appellate court to process cases between the time an appellate court panel considers a case and the time they release an opinion. Pulling that information together manually is tedious, so I wrote Python scripts to do it for me.

These scripts generate:
- **cases_decided.html** – cases with released opinions
- **cases_waiting.html** – cases still awaiting an opinion

I run this weekly, and the results are uploaded to:
- [Voylento.com — cases_decided.html](https://voylento.com/cases_decided.html)
- [Voylento.com — cases_waiting.html](https://voylento.com/cases_waiting.html)

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

## License
MIT License.
