import phonenumbers
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys


def validate_phone_number(phone_number):
    """
    Validate the given phone number and return it in E.164 format.
    """
    try:
        parsed_number = phonenumbers.parse(phone_number, None)
    except phonenumbers.NumberParseException:
        print(f"Invalid phone number: {phone_number}")
        sys.exit(1)

    if not phonenumbers.is_valid_number(parsed_number):
        print(f"Invalid phone number: {phone_number}")
        sys.exit(1)

    return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)


def lookup_phone_number(phone_number):
    """
    Lookup information about the given phone number using web APIs.
    """
    url = f"https://www.truecaller.com/search/in/{phone_number}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    # Use a session to persist cookies across requests
    with requests.Session() as session:
        # Load the initial page to get the session cookie
        session.get(url, headers=headers)

        # Make a POST request to the API to get phone number details
        api_url = "https://www.truecaller.com/v2/search"
        response = session.post(api_url, json={"search": f"{phone_number}"})

        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            sys.exit(1)

        # Parse the JSON response and extract the relevant fields
        result = response.json()["data"][0]
        name = result.get("name")
        location = result.get("location")
        carrier = result.get("carrier")
        line_type = result.get("line_type")

        # Return the phone number details as a dictionary
        return {
            "name": name,
            "location": location,
            "carrier": carrier,
            "line_type": line_type
        }


def lookup_social_media(phone_number):
    """
    Lookup social media profiles and activity associated with the given phone number using web scraping.
    """
    url = f"https://www.google.com/search?q={phone_number}"
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    # Load the Google search results page and extract the URLs
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = soup.find_all("a")
    urls = [link.get("href") for link in links]

    # Filter the URLs to those that are likely to be social media profiles
    social_media_urls = []
    for url in urls:
        if "facebook.com" in url:
            social_media_urls.append(url)
        elif "twitter.com" in url:
            social_media_urls.append(url)
        elif "instagram.com" in url:
            social_media_urls.append(url)

    # Visit each social media profile and extract activity data
    activity = {}
    for url in social_media_urls:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        if "facebook.com" in url:
            # Extract Facebook activity data
            likes = soup.find("div", {"class": "_4-u2 _6590 _3xaf _4-u8"})
            if likes is not None:
                likes = likes.text.strip
        elif "twitter.com" in url:
            # Extract Twitter activity data
            tweets = soup.find_all("div", {"class": "css-901oao css-bfa6kz r-111h2gw r-18u37iz r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-13qz1uu r-qvutc0"})
            if tweets:
                tweets_count = len(tweets)
                activity["twitter"] = {"tweets": tweets_count}

        elif "instagram.com" in url:
            # Extract Instagram activity data
            posts = soup.find("span", {"class": "g47SY"})
            if posts is not None:
                posts_count = posts.text.replace(",", "")
                activity["instagram"] = {"posts": posts_count}

    # Quit the browser driver
    driver.quit()

    # Return the social media activity data as a dictionary
    return activity
