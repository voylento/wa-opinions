import os

# Directory of *this script*
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build paths relative to project root (script is in src/, cft is in root)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

chrome_binary = os.path.join(PROJECT_ROOT, "cft", "chrome-mac-arm64", "Google Chrome for Testing.app", "Contents", "MacOS", "Google Chrome for Testing")
driver_binary = os.path.join(PROJECT_ROOT, "cft", "chromedriver-mac-arm64", "chromedriver")
