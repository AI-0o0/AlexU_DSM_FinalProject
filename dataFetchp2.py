import requests
import pandas as pd
import json
import time


def fetch_rental_data(limit=200, offset=0):
    """Fetch rental data from API with pagination"""
    url = "https://realtor16.p.rapidapi.com/search/forrent"
    # another endpoint cause why not :>

    #parameters for the get req
    querystring = {
        "location": "houston,tx",
        "search_radius": "0",
        "limit": str(limit),
        "offset": str(offset)
    }
    #headers 34an el maw23 my2fl4 3lina
    headers = {
        "x-rapidapi-key": "407025312dmsh32922775f3dcb44p1df808jsn8534d5a66041",
        "x-rapidapi-host": "realtor16.p.rapidapi.com"
    }
    # 34an el debugging
    print(f"Fetching data (offset={offset}, limit={limit})...")

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=30) #sends req
        print(f"Status Code: {response.status_code}") #for debugging bardo

        if response.status_code == 200: # 200 == elfar7a
            print(" Data fetched successfully!")
            return response.json()
        elif response.status_code == 429: # 2rar ezalah
            print("Rate limit hit (429)")
            return None
        else:
            print(f" ERror: {response.status_code}")
            print(response.text[:200]) ## first 200 letter bcuz sometimes its big block of text lol
            return None
    except Exception as e:
        print(f"request error: {e}")
        return None


def extract_property_data(properties):
    """Extract relevant fields from properties"""
    extracted_data = []

    for prop in properties:
        record = {}
        desc = prop.get('description', {}) or {}
        record['beds'] = desc.get('beds')
        record['baths'] = desc.get('baths_consolidated')
        record['sqft'] = desc.get('sqft')
        record['property_type'] = desc.get('type')
        record['year_built'] = desc.get('year_built')
        record['list_price'] = prop.get('list_price')
        record['list_date'] = prop.get('list_date')
        record['listing_id'] = prop.get('listing_id')
        record['status'] = prop.get('status')
        record['property_id'] = prop.get('property_id')
        location = prop.get('location', {}) or {}
        address = location.get('address', {}) or {}
        coordinate = address.get('coordinate', {}) or {}
        county = location.get('county', {}) or {}
        record['address_line'] = address.get('line')
        record['city'] = address.get('city')
        record['state'] = address.get('state_code')
        record['postal_code'] = address.get('postal_code')
        record['country'] = address.get('country')
        record['latitude'] = coordinate.get('lat') if coordinate else None
        record['longitude'] = coordinate.get('lon') if coordinate else None
        record['county_name'] = county.get('name') if county else None
        record['county_fips'] = county.get('fips_code') if county else None
        details = prop.get('details', []) or []

        for detail in details:
            category = detail.get('category', '').replace(' ', '_').lower()
            texts = detail.get('text', [])
            if texts:
                record[f'detail_{category}'] = ' | '.join(texts)

        other_listings = prop.get('other_listings', {})
        if other_listings:
            rdc_listings = other_listings.get('rdc', []) or []
            record['other_listings_count'] = len(rdc_listings)
            record['listing_history'] = json.dumps(rdc_listings)
        else:
            record['other_listings_count'] = 0
            record['listing_history'] = '[]'

        extracted_data.append(record)

    return extracted_data


def save_to_csv(data, filename='houston_rentals.csv'):
    """Save data to CSV file"""
    if not data: #34an law 3mlt error my3ml4 file
        print("No data to save!")
        return

    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8') #makes csv to be cleaned

    print(f"\nata saved to {filename}")
    print(f"total rows {len(df)}")
    print(f"total cols: {len(df.columns)}")


def main():
    all_properties = []
    limit = 200  #
    offset = 0
    page = 1
    max_pages = 50  #

    while page <= max_pages:
        print(f"\n---Page {page}---")#for tracking in debugging

        # Add delay between requests (except first one)
        if page > 1:
            wait_time = 2
            print(f"waitin{wait_time} seconds") # req limit :)
            time.sleep(wait_time)

        data = fetch_rental_data(limit=limit, offset=offset)

        if not data:
            print("Stopping due to API error or rate limit")
            break

        # Extract properties
        properties = data.get('properties', [])

        if not properties:
            print("No more properties found")
            break

        print(f"Got {len(properties)} properties from page {page}") #for debugging too :>
        all_properties.extend(properties) # add to the var that holds em all

        # checks for last page (m4 hnwslha)
        if len(properties) < limit:
            print("✓ Last page reached (partial results)")
            break

        offset += limit
        page += 1

    print(f"Total properties fetched: {len(all_properties)}")
    print(f"Total pages: {page}")

    if not all_properties:
        print("No properties to process")
        return

    # Extract and save
    extracted_data = extract_property_data(all_properties)

    save_to_csv(extracted_data)
    print("\n Done :>> ")


if __name__ == "__main__":
    main()