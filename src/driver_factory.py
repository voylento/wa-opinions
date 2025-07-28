import os
import platform
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def create_driver(project_root: Optional[str] = None, headless: bool =True) -> webdriver.Chrome:
    # Resolve project root if not provided
    if project_root is None:
        # Assume this file is in root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

    system = platform.system().lower()
    arch = platform.machine().lower()

    # Figure out platform-specific paths
    if system == "darwin":
        # macOS arm64 only (this is your tested platform)
        chrome_binary = os.path.join(
            project_root, "cft", "chrome-mac-arm64",
            "Google Chrome for Testing.app", "Contents", "MacOS", "Google Chrome for Testing"
        )
        driver_binary = os.path.join(project_root, "cft", "chromedriver-mac-arm64", "chromedriver")

    elif system == "linux":
        chrome_binary = os.path.join(project_root, "cft", "chrome-linux64", "chrome")
        driver_binary = os.path.join(project_root, "cft", "chromedriver-linux64", "chromedriver")

    elif system == "windows":
        # Native Windows (if someone runs Python there)
        chrome_binary = os.path.join(project_root, "cft", "chrome-win64", "chrome.exe")
        driver_binary = os.path.join(project_root, "cft", "chromedriver-win64", "chromedriver.exe")

    else:
        raise RuntimeError(f"Unsupported system: {system} / {arch}")

    # Build Chrome options
    options = Options()
    options.binary_location = chrome_binary
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--remote-debugging-port=9222")

    service = Service(driver_binary)
    driver = webdriver.Chrome(service=service, options=options)
    return driver
