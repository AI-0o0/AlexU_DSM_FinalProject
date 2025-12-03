import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# --- Setup ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}
base_link = 'https://eg.hatla2ee.com'
all_car_details = []

# Define the exact start and end pages for this script
START_PAGE = 1
END_PAGE = 1030

for i in range(START_PAGE, END_PAGE + 1):
    print(f"Scraping page {i}...")
    url = f'https://eg.hatla2ee.com/en/car/search?page={i}'
    try:
        page_response = requests.get(url, headers=HEADERS, timeout=20)
        page_response.raise_for_status()
        page = page_response.text
        soup = BeautifulSoup(page, 'html.parser')

        # Find all car cards using data-slot attribute
        car_containers = soup.find_all('div', attrs={'data-slot': 'card-content'})

        if not car_containers:
            print(f"\nNo car listings found on page {i}. This might be the last page or the structure changed.")
            break

        print(f"Found {len(car_containers)} cars on page {i}")

        for car in car_containers:
            try:
                # Find the link inside the card (the <a> tag with no-underline class)
                link_tag = car.find('a', class_='no-underline')

                if not link_tag:
                    print("No link found in this card, skipping...")
                    continue

                link_url = link_tag.get('href')
                full_url = base_link + link_url

                # Get car title from the link's title attribute
                car_title = link_tag.get('title', 'N/A')

                print(f"Processing: {car_title}")

                # Retry mechanism for getting the detail page
                sub_page = None
                for attempt in range(3):
                    try:
                        sub_page_response = requests.get(full_url, headers=HEADERS, timeout=20)
                        sub_page_response.raise_for_status()
                        sub_page = sub_page_response.text
                        break
                    except requests.exceptions.RequestException as e:
                        print(f"  Attempt {attempt + 1} failed. Error: {e}. Retrying...")
                        time.sleep(attempt * 2 + 1)

                if sub_page is None:
                    print(f"  Could not retrieve {full_url} after multiple attempts. Skipping.")
                    continue

                detail_soup = BeautifulSoup(sub_page, "html.parser")

                current_car_details = {
                    'Title': car_title,
                    'URL': full_url
                }

                # Extract price
                price_span = detail_soup.find('span', class_='usedUnitCarPrice')
                current_car_details['Price'] = price_span.text.strip() if price_span else "N/A"

                # Extract date
                date_tag = detail_soup.find('div', class_='galleryIconWrap date')
                current_car_details['Date'] = date_tag.find('span').text.strip() if date_tag and date_tag.find(
                    'span') else "N/A"

                # Extract all description data items
                desc_items = detail_soup.find_all('div', class_='DescDataItem')
                for item in desc_items:
                    label_tag = item.find('span', class_='DescDataSubTit')
                    value_tag = item.find('span', class_='DescDataVal')
                    if label_tag and value_tag:
                        label = label_tag.text.strip()
                        value = value_tag.text.strip()
                        current_car_details[label] = value

                all_car_details.append(current_car_details)
                print(f"Successfully scraped {car_title}")

                # Random delay to appear human-like
                time.sleep(random.uniform(1, 3))

            except Exception as e:
                print(f"Could not process one car. Error:{e}. Skipping.")

    except Exception as e:
        print(f"\nCould not load page {i}. Error: {e}")

# --- Final saving step ---
print(f"Scraping completeSuccessfully scraped  {len(all_car_details)} cars,Elfar7a (*_*)!")

if all_car_details:
    df = pd.DataFrame(all_car_details)

    if 'The model' in df.columns: #lzom el 7enka
        df = df.rename(columns={'The model': 'Model'})

    output_file = f'hatla2ee_scraped_cars_{START_PAGE}-{END_PAGE}.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"  Total columns: {len(df.columns)}")
    print(f"  Columns: {', '.join(df.columns)}")
else:
    print("\n No data was scraped. Check your internet connection or if the website structure changed. 7slt mrteen X) ")