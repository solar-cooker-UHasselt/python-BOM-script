import requests
import json
from datetime import datetime

def get_mouser_product_details(part_number, api_key):
    url = f"https://api.mouser.com/api/v1/search/partnumber?apiKey={api_key}"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "SearchByPartRequest": {
            "mouserPartNumber": part_number,
            "partSearchOptions": "string"
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except ValueError:
        print(f"JSON decode error: {response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None

def process_mouser_part_details(part_number, product_details):
    try:
        part_info = product_details.get("SearchResults", {}).get("Parts", [])[0]
        availability = part_info.get("AvailabilityInStock", "N/A")
        package_type = next(
            (attr['AttributeValue'] for attr in part_info.get('ProductAttributes', [])
             if attr['AttributeName'] == "Packaging"), "N/A"
        )
        unit_price = next(
            (format_price(pb['Price']) for pb in part_info.get('PriceBreaks', [])
             if pb['Quantity'] == 1), "N/A"
        )
        return unit_price, package_type, availability, datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    except (IndexError, KeyError) as e:
        print(f"Error processing product details for part number {part_number}: {e}")
        return "/", "/", "/", datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"An unexpected error occurred while processing part number {part_number}: {e}")
        return "/", "/", "/", datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def format_price(price_str):
    price_str = price_str.replace('€', '').strip()
    price_str = price_str.replace(',', '.')
    return float(price_str)
