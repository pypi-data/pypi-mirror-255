import undetected_chromedriver as uc
import re
import requests
from bs4 import BeautifulSoup
import subprocess
import os

counter = 0

def extract_emails(text):
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(pattern, text)
    return emails

def move_processed_numbers(phone_number, processed_phone_file_name):
    with open(processed_phone_file_name, 'r') as processed_file:
        processed_numbers = processed_file.readlines()
        if f"{phone_number}\n" in processed_numbers:
            return 

    with open(processed_phone_file_name, 'a') as processed_file:
        processed_file.write(f"{phone_number}\n")


def extract_emails_from_phone_file(phone_file_name, emails_file_name, processed_phone_file_name):
    global counter
    driver = None

    try:
        while True:
            driver = uc.Chrome()
            
            processed_phone_numbers = set()
            if os.path.exists(processed_phone_file_name):
                with open(processed_phone_file_name, 'r') as processed_file:
                    processed_phone_numbers = {phone.strip() for phone in processed_file.readlines()}

            with open(phone_file_name, 'r') as file:
                phone_numbers = [phone.strip() for phone in file.readlines() if phone.strip() not in processed_phone_numbers]

            all_emails = set()

            for phone in phone_numbers:
                if "+1" in phone:
                    phone = phone.replace("+1" , "")
                try:
                    url = f'https://www.smartbackgroundchecks.com/phone/{phone}'
                    driver.get(url)

                    page_source = driver.page_source

                    pattern = r'<a\s+href="(.*?)".*?>'

                    links = re.findall(pattern, page_source)

                    target_links = [link for link in links if link.startswith('https://www.smartbackgroundchecks.com/people/')]

                    unique_links = list(set(target_links))

                    for link in unique_links:
                        try:
                            driver.get(link)
                            emails_on_page = extract_emails(driver.page_source)
                            if emails_on_page:
                                for email in emails_on_page:
                                    if email not in all_emails:
                                        all_emails.add(email)
                                        emails_file_name = emails_file_name.replace(".txt","")
                                        with open(emails_file_name+"_emails_only.txt", 'a') as file:
                                            file.write(f"{email}\n")
                                        with open(emails_file_name+"_with_phone.txt", 'a') as file:
                                            file.write(f"{phone}:{email}\n")
                                        counter += 1
                                        print(f"{counter}: {phone} >> {email}")
                                        move_processed_numbers(phone, processed_phone_file_name)
                        except Exception as e:
                            print(f"Error while processing link {link}: {e}")
                except Exception as e:
                    print(f"Error while processing phone number {phone}: {e}")
                    continue

            input(" All phone numbers have been processed - Press enter to exit ")

    finally:
        if driver is not None:
            driver.quit()

def get_package_version(package_name):
    try:
        output = subprocess.check_output(['pip', 'show', package_name], universal_newlines=True)
        lines = output.strip().split('\n')
        version_line = next((line for line in lines if line.startswith('Version:')), None)
        if version_line:
            _, version = version_line.split(':')
            return version.strip()
        else:
            return None
    except subprocess.CalledProcessError:
        return None

def checker():

    url = "https://pypi.org/project/email-extractor-unicode/"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        input(f"Error occurred: {e}")
        exit()

    soup = BeautifulSoup(response.text, "html.parser")

    h1_element = soup.find("h1", class_="package-header__name")

    if h1_element:
        package_name_version = h1_element.get_text().strip()

        version_number = re.search(r'\d+\.\d+\.\d+', package_name_version)
        if version_number:
            installed_version_number = version_number.group(0)
            package_name = 'email-extractor-unicode'
            version_number = get_package_version(package_name)
            if str(installed_version_number) != str(version_number):
                subprocess.check_call(["pip", "install", "email-extractor-unicode", "--upgrade"])

    os.system("cls")
    phone_file_name = input("Please type phone file name or path to file: ")
    emails_file_name = input("How do you want to save emails? eg, emails.txt: ")
    processed_phone_file_name = "processed_phone.txt"
    extract_emails_from_phone_file(phone_file_name, emails_file_name, processed_phone_file_name)

