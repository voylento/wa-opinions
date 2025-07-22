import os
import platform
import shutil
import stat
import subprocess

system = platform.system().lower()
arch = platform.machine().lower()

# === CONFIG ===
version = "127.0.6533.72"

# Default placeholders
chrome_zip_url = ""
driver_zip_url = ""
chrome_zip_name = ""
driver_zip_name = ""
chrome_dir_name = ""
driver_dir_name = ""

if system == "darwin" and arch in ("arm64", "aarch64"):
    chrome_zip_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/mac-arm64/chrome-mac-arm64.zip"
    driver_zip_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/mac-arm64/chromedriver-mac-arm64.zip"
    chrome_zip_name = "chrome-mac-arm64.zip"
    driver_zip_name = "chromedriver-mac-arm64.zip"
    chrome_dir_name = "chrome-mac-arm64"
    driver_dir_name = "chromedriver-mac-arm64"

elif system == "linux":
    chrome_zip_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/linux64/chrome-linux64.zip"
    driver_zip_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/linux64/chromedriver-linux64.zip"
    chrome_zip_name = "chrome-linux64.zip"
    driver_zip_name = "chromedriver-linux64.zip"
    chrome_dir_name = "chrome-linux64"
    driver_dir_name = "chromedriver-linux64"

else:
    raise RuntimeError(f"Unsupported system: {system} / {arch}")

# === CLEAN UP OLD STUFF ===
if os.path.exists("cft"):
    print("Removing old cft directory...")
    shutil.rmtree("cft")
for f in (chrome_zip_name, driver_zip_name, chrome_dir_name, driver_dir_name):
    if os.path.exists(f):
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)

# === DOWNLOAD USING CURL ===
print(f"Downloading Chrome for Testing ({system}) with curl...")
subprocess.run(["curl", "-LO", chrome_zip_url], check=True)

print(f"Downloading Chromedriver ({system}) with curl...")
subprocess.run(["curl", "-LO", driver_zip_url], check=True)

# === UNZIP USING SYSTEM unzip ===
print("Unzipping Chrome for Testing...")
subprocess.run(["unzip", chrome_zip_name], check=True)

print("Unzipping Chromedriver...")
subprocess.run(["unzip", driver_zip_name], check=True)

# === CREATE cft/ AND MOVE DIRECTORIES ===
os.mkdir("cft")
shutil.move(chrome_dir_name, os.path.join("cft", chrome_dir_name))
shutil.move(driver_dir_name, os.path.join("cft", driver_dir_name))

# === MAKE CHROMEDRIVER EXECUTABLE ===
chromedriver_path = os.path.join("cft", driver_dir_name, "chromedriver")
if system == "windows":
    chromedriver_path += ".exe"
st = os.stat(chromedriver_path)
os.chmod(chromedriver_path, st.st_mode | stat.S_IEXEC)

# === CLEAN UP ZIP FILES ===
os.remove(chrome_zip_name)
os.remove(driver_zip_name)

print("\n✅ Setup complete!")
print("Chrome for Testing and Chromedriver are now in ./cft/")
