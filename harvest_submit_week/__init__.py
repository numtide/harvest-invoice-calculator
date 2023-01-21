#!/usr/bin/env python3

import sys
import os
import traceback
from typing import NoReturn
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from tempfile import NamedTemporaryFile
import subprocess

# for debugging
def screen(driver: webdriver.Chrome):
    driver.save_screenshot("/tmp/debug.png")
    subprocess.Popen(["eog", "/tmp/debug.png"])


def die(msg: str) -> NoReturn:
    print(msg, file=sys.stderr)
    sys.exit(1)


def ensure_env(var: str) -> str:
    val = os.environ.get(var)
    if not val:
        die(f"environment variable '{var}' is required. Set it in your .envrc.local!")
    return val


def submit_week(driver: webdriver.Chrome, start_url, email: str, password: str):
    driver.get(start_url)
    email_field = driver.find_element(By.ID, "email")
    email_field.clear()
    email_field.send_keys(email)

    password_field = driver.find_element(By.ID, "password")
    password_field.clear()
    password_field.send_keys(password)

    login = driver.find_element(By.ID, "log-in")
    login.click()

    submit = driver.find_element(By.CSS_SELECTOR, "button.test-submit-button")
    submit.click()


def main() -> None:
    start_url = "https://numtide.harvestapp.com/time"
    email = ensure_env("HARVEST_EMAIL")
    password = ensure_env("HARVEST_PASSWORD")
    chrome_options = Options()
    chrome_options.headless = True
    driver = webdriver.Chrome(options=chrome_options)

    try:
        submit_week(driver, start_url, email, password)
    except Exception as e:
        print("submitting fails with:")
        traceback.print_exception(e)

        with NamedTemporaryFile(suffix=".png", delete=False) as f:
            driver.save_screenshot(f.name)
            print(f"Stored screenshot of harvest under {f.name}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
