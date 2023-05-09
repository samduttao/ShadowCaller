import phonenumbers
import requests
import argparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def validate_phone_number(phone_number):
    """
    Validates the given phone number and returns a parsed object if valid.
    """
    try:
        parsed_number = phonenumbers.parse(phone_number)
    except phonenumbers.phonenumberutil.NumberParseException:
        return None
    
    if not phonenumbers.is_possible_number(parsed_number):
        return None
    
    if not phonenumbers.is_valid_number(parsed_number):
        return None
    
    return parsed_number

def lookup_phone_number(parsed_number):
    """
    Looks up information about the given phone number using various APIs.
    """
    response = requests.get(f"https://api.telnyx.com/anonymous/v2/number_lookup/{parsed_number.country_code}{parsed_number.national_number}")
    if response.status_code != 200:
        return None
    
    data = response.json()
    carrier = data.get("carrier", {}).get("name", None)
    line_type = data.get("line_type", None)
    
    return {
        "country": phonenumbers.region_code_for_number(parsed_number),
        "region": phonenumbers.geocoder.description_for_number(parsed_number, "en"),
        "carrier": carrier,
        "line_type": line_type,
    }

def search_social_media(phone_number):
    """
    Searches for social media profiles and activity associated with the given phone number.
    """
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://www.google.com/")
        search_box = driver.find_element_by_name("q")
        search_box.send_keys(f'"{phone_number}"')
        search_box.submit()
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        results = soup.find_all("div", class_="g")
        
        for result in results:
            link = result.find("a")
            if not link:
                continue
            
            href = link.get("href")
            if "twitter.com" in href:
                print(f"Twitter: {href}")
            elif "facebook.com" in href:
                print(f"Facebook: {href}")
            elif "linkedin.com" in href:
                print(f"LinkedIn: {href}")
                
    finally:
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A tool to find social media profiles associated with a phone number.")
    parser.add_argument("phone_number", type=str, help="The phone number to look up (in international format, e.g. +14155552671)")
    args = parser.parse_args()

    parsed_number = validate_phone_number(args.phone_number)
    if not parsed_number:
        print("Invalid phone number")
        exit(1)

    phone_info = lookup_phone_number(parsed_number)
    if not phone_info:
        print("Could not look up phone number")
        exit(1)

    print("Phone number information:")
    print(f"Country: {phone_info['country']}")
    print(f"Region: {phone_info['region']}")
    print(f"Carrier: {phone_info['carrier']}")
    print(f"Line type: {phone_info['line_type']}")

    print("Social media information:")
    search_social_media(args.phone_number)
