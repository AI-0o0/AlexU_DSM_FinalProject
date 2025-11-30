import requests
import time
import csv
import json


class RealtorAPI:
    # class 34an yb2a clean code w kda
    #constructor
    def __init__(self, api_key):
        self.api_key = api_key # the website locks the api after 30 req for free plan :')
        self.base_url = "https://realtor16.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": api_key, # to access the api
            "X-RapidAPI-Host": "realtor16.p.rapidapi.com"
        }

    #function to get properties from 1 loc
    def search_properties(self, location, limit=200, offset=0):
        url = f"{self.base_url}/search/forsale"
        #parameters to specify the url / 34an GET Req
        params = {
            "location": location,
            "limit": limit,
            "offset": offset
        }

        try: # error handling bcuz it returns error sometimes (el qouta 5lst)
            response = requests.get(url, headers=self.headers, params=params)
            # raise err when statues code isn't 2XX ish
            response.raise_for_status()
            return response.json() # returns json
        except Exception as e:
            print(f"API error: {e}")
            return None

# filters the unneede columns
def extract_minimal_properties(api_response):
    """Returns minimal required fields."""
    if not api_response:
        return []

    listings = api_response.get("properties", [])
    cleaned = []

    for listing in listings:
        cleaned.append({
            "property_id": listing.get("property_id"),
            "status": listing.get("status"),
            "description": json.dumps(listing.get("description", {})),# json.dumps make the object a json format :>
            "location": json.dumps(listing.get("location", {})),
            "branding": json.dumps(listing.get("branding", {})),
        })

    return cleaned


def fetch_all_properties(api, location, max_pages=20):
    """Fetch ALL pages until no more results. or the website blocks us lol """
    all_props = []
    offset = 0
    limit = 200
    #loop to fetch
    for page in range(1, max_pages + 1):
        print(f"Fetching page {page} ...")
        #gets all props to certain area
        response = api.search_properties(location, limit=limit, offset=offset)

        if not response:
            print("Stopping (no response).")
            break
        # gets alll needed props only
        cleaned = extract_minimal_properties(response)

        if not cleaned:
            print("Stopping (no more results).")
            break
        #add new props to the list of props :)
        all_props.extend(cleaned)

        if len(cleaned) < limit:
            print("Reached last page.")
            break
        # ignores first ... prop
        offset += limit
        time.sleep(0.5) #34an el server my4tm4

    return all_props


def save_to_csv(data, filename):
    """Save cleaned properties to CSV."""
    if not data:
        print("No data to save.")
        return

    keys = data[0].keys() #gets props names
    #opens file with write privielage  // encoding 34an law fi rmoz // newline makes csv lib doesnt make new lines by default
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys) #writer to write data
        writer.writeheader() # write heads of the data
        writer.writerows(data) # writes the data 45sian

    print(f"CSV saved: {filename}")


if __name__ == "__main__":
    API_KEY = "cbdf40edd0msh5a39d0513d5f8e6p1bb8cejsnc3dea2758dd2"
    api = RealtorAPI(API_KEY)

    location = "Houston, TX" # mn el website
    filename = f"{location.replace(',', '').replace(' ', '_')}_minimal.csv"

    properties = fetch_all_properties(api, location)

    print(f"Fetched {len(properties)} properties.")

    save_to_csv(properties, filename)

    print("Done.")
