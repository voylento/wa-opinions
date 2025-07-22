import os
import shutil
import stat
import subprocess

# === CONFIG ===
version = "127.0.6533.72"
chrome_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/mac-arm64/chrome-mac-arm64.zip"
driver_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/mac-arm64/chromedriver-mac-arm64.zip"

chrome_zip = "chrome-mac-arm64.zip"
driver_zip = "chromedriver-mac-arm64.zip"

# === CLEAN UP OLD STUFF ===
if os.path.exists("cft"):
    print("Removing old cft directory...")
    shutil.rmtree("cft")
for f in (chrome_zip, driver_zip, "chrome-mac-arm64", "chromedriver-mac-arm64"):
    if os.path.exists(f):
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)

# === DOWNLOAD USING CURL ===
print("Downloading Chrome for Testing with curl...")
subprocess.run(["curl", "-LO", chrome_url], check=True)

print("Downloading Chromedriver with curl...")
subprocess.run(["curl", "-LO", driver_url], check=True)

# === UNZIP USING SYSTEM unzip ===
print("Unzipping Chrome for Testing...")
subprocess.run(["unzip", chrome_zip], check=True)

print("Unzipping Chromedriver...")
subprocess.run(["unzip", driver_zip], check=True)

# === CREATE cft/ AND MOVE DIRECTORIES ===
os.mkdir("cft")
shutil.move("chrome-mac-arm64", os.path.join("cft", "chrome-mac-arm64"))
shutil.move("chromedriver-mac-arm64", os.path.join("cft", "chromedriver-mac-arm64"))

# === MAKE CHROMEDRIVER EXECUTABLE ===
chromedriver_path = os.path.join("cft", "chromedriver-mac-arm64", "chromedriver")
st = os.stat(chromedriver_path)
os.chmod(chromedriver_path, st.st_mode | stat.S_IEXEC)

# === CLEAN UP ZIP FILES ===
os.remove(chrome_zip)
os.remove(driver_zip)

print("\n✅ Setup complete!")
print("Chrome for Testing and Chromedriver are now in ./cft/")
