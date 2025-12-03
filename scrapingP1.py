import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}
base_link = 'https://eg.hatla2ee.com'
all_car_details = []

# Define the exact start and end pages for this script 34an h3mlha 3la agza2
START_PAGE = 1
END_PAGE = 1


def extract_basic_info_from_card(card_soup):
    """Extract basic info from the listing card"""
    info = {}

    # Find the text section with year, mileage, transmission, fuel
    text_section = card_soup.find('div', class_='text-xs flex flex-wrap items-center')
    if text_section:
        spans = text_section.find_all('span')
        text_items = [s.get_text(strip=True) for s in spans if s.get_text(strip=True)]

        if len(text_items) >= 4:
            info['Year'] = text_items[0]
            info['Mileage_in_KM'] = text_items[1].replace(' KM', '').replace(',', '')
            info['Transmission'] = text_items[2]
            info['Fuel_Type'] = text_items[3]

    # Extract price
    price_div = card_soup.find('div', class_='text-lg lg:text-xl font-bold text-primary')
    if price_div:
        price_text = price_div.get_text(strip=True)
        price_match = re.search(r'([\d,]+)', price_text)
        if price_match:
            info['Price'] = price_match.group(1).replace(',', '')

    # Extract make/model
    tag_links = card_soup.find_all('a', class_='inline-flex items-center gap-1 text-gray-500')
    for link in tag_links:
        text = link.get_text(strip=True)
        if link.find('svg'):
            continue
        if 'Make' not in info:
            info['Make'] = text
        elif 'Model' not in info:
            info['Model'] = text
            break

    # Extract city
    city_link = card_soup.find('a', title=lambda t: t and 'For Sale' in t if t else False)
    if city_link:
        info['City'] = city_link.get_text(strip=True)

    return info


#scraaping
for i in range(START_PAGE, END_PAGE + 1):
    print(f"Scraping page {i}  :)")
    url = f'https://eg.hatla2ee.com/en/car/search?page={i}'

    try:
        page_response = requests.get(url, headers=HEADERS, timeout=20)
        page_response.raise_for_status()
        soup = BeautifulSoup(page_response.text, 'html.parser')

        car_containers = soup.find_all('div', attrs={'data-slot': 'card-content'})

        if not car_containers:
            print(f"No cars found on page {i}.")
            break

        print(f"Found {len(car_containers)} cars on page {i} ")

        for car in car_containers:
            try:
                # Extract title from card
                title_span = car.select_one("span.font-semibold.fs-body")
                car_title = title_span.get_text(strip=True) if title_span else 'N/A'
                print(f"getting data: {car_title}")

                # Extract card info
                current_car_details = extract_basic_info_from_card(car)
                current_car_details['Title'] = car_title

                # Find detail page
                link_tag = car.find('a', class_='no-underline')
                if not link_tag:
                    continue

                full_url = base_link + link_tag.get('href')

                # Fetch detail page
                sub_page = None
                for attempt in range(3):
                    try:
                        sub_page_response = requests.get(full_url, headers=HEADERS, timeout=20)
                        sub_page_response.raise_for_status()
                        sub_page = sub_page_response.text
                        break
                    except requests.exceptions.RequestException:
                        time.sleep(attempt * 2 + 1)

                if not sub_page:
                    continue

                detail_soup = BeautifulSoup(sub_page, "html.parser")

                # Extract date
                date_tag = detail_soup.find('div', class_='galleryIconWrap date')
                if date_tag and date_tag.find('span'):
                    current_car_details['Date'] = date_tag.find('span').text.strip()

                # Extract description fields
                desc_items = detail_soup.find_all('div', class_='DescDataItem')
                for item in desc_items:
                    label_tag = item.find('span', class_='DescDataSubTit')
                    value_tag = item.find('span', class_='DescDataVal')
                    if not label_tag or not value_tag:
                        continue

                    label = label_tag.text.strip()
                    value = value_tag.text.strip()

                    if 'Color' in label or 'اللون' in label:
                        current_car_details['Color'] = value
                    elif 'Class' in label or 'الفئة' in label:
                        current_car_details['Class'] = value
                    elif 'Body' in label or 'الشكل' in label:
                        current_car_details['Body_Style'] = value
                    elif 'Cylinder' in label or 'السلندر' in label:
                        current_car_details['Cylinder_Count'] = value
                    elif 'Engine' in label or 'سعة المحرك' in label:
                        current_car_details['Engine_Capacity'] = value

                all_car_details.append(current_car_details)
                print("Successfully scraped")

                time.sleep(random.uniform(1, 3))

            except Exception as e:
                print(f"Error scraping car: {e}")

    except Exception as e:
        print(f"Error loading page {i}: {e}")


print(f"Scraping complete {len(all_car_details)} cars scraped.")


if all_car_details:
    df = pd.DataFrame(all_car_details)

    desired_columns = [
        'Price', 'Date', 'Make', 'Model', 'Year', 'Mileage_in_KM',
        'Transmission', 'City', 'Color', 'Fuel_Type', 'Class',
        'Body_Style', 'Cylinder_Count', 'Engine_Capacity', 'Title'
    ]

    final_columns = [c for c in desired_columns if c in df.columns]
    df = df[final_columns]

    output_file = f'scraped_cars_{START_PAGE}-{END_PAGE}.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"\nSaved to '{output_file}'")
else:
    print("\nNo data scraped.")
