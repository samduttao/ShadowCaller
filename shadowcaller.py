import phonenumbers
from phonenumbers import geocoder, carrier
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

number = input("Enter phone number in international format: ")
try:
    parsed_number = phonenumbers.parse(number)
    country = geocoder.country_name_for_number(parsed_number)
    provider = carrier.name_for_number(parsed_number, 'en')
    print("Country: ", country)
    print("Provider: ", provider)

    # Social media search
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.google.com/")
    search_box = driver.find_element_by_name("q")
    search_box.send_keys(number)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    results = soup.find_all('a')
    for result in results:
        link = result.get('href')
        if "facebook.com" in link:
            print("Facebook profile found: ", link)
        elif "twitter.com" in link:
            print("Twitter profile found: ", link)
        elif "instagram.com" in link:
            print("Instagram profile found: ", link)
        elif "linkedin.com" in link:
            print("LinkedIn profile found: ", link)
    
    # Reverse phone lookup
    url = "https://www.truecaller.com/search/in/" + number
    driver.get(url)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    name = soup.find('span', {'class': 'profileTitle'}).text
    location = soup.find('div', {'class': 'detail'}).find_all('span')[1].text
    print("Name: ", name)
    print("Location: ", location)
    
    # Carrier lookup
    url = "https://www.carrierlookup.com/index.php/carrier_lookup_api/?num=" + number
    response = requests.get(url).json()
    carrier_name = response["carrier_name"]
    print("Carrier: ", carrier_name)

    driver.quit()
except phonenumbers.phonenumberutil.NumberParseException:
    print("Invalid phone number")
