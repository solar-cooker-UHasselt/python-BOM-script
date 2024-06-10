import requests
from datetime import datetime
import json

def get_digikey_access_token(client_id, client_secret):
    url = "https://api.digikey.com/v1/oauth2/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(url, headers=headers, data=data)

    try:
        response.raise_for_status()
        return response.json().get('access_token')
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.content.decode()}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except ValueError:
        print(f"JSON decode error: {response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None

def get_digikey_product_details(part_number, access_token, client_id):
    url = f"https://api.digikey.com/products/v4/search/{part_number}/productdetails"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'X-DIGIKEY-Client-Id': client_id,
        'X-DIGIKEY-Locale-Site': 'BE',
        'X-DIGIKEY-Locale-Language': 'en',
        'X-DIGIKEY-Locale-Currency': 'EUR'
    }
    response = requests.get(url, headers=headers)

    try:
        response.raise_for_status()
        print(f"Successful response for part number {part_number}")
        response_data = response.json()
        # with open(f"response_{part_number}.json", 'w') as f:
        #     json.dump(response_data, f, indent=2)
        return response_data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred for part number {part_number}: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred for part number {part_number}: {req_err}")
    except ValueError:
        print(f"JSON decode error for part number {part_number}: {response.text}")
    except Exception as e:
        print(f"An unexpected error occurred for part number {part_number}: {e}")

    return None

def process_digikey_part_details(product_details):
    try:
        product = product_details['Product']
        valid_variations = [v for v in product['ProductVariations'] if v['PackageType']['Id'] in [2, 3, 6]]
        if not valid_variations:
            raise ValueError("No valid product variations found with PackageType Id 2, 3, or 6.")
        
        variation = valid_variations[0]

        package_type = next(
            (v['PackageType']['Name'] for v in product['ProductVariations']
             if v['PackageType']['Id'] in [2, 3, 6]), "N/A"
        )
        unit_price = next(
            (price['UnitPrice'] for price in variation['StandardPricing']
             if price['BreakQuantity'] == 1), "N/A"
        )
        quantity_available = variation.get('QuantityAvailableforPackageType', "N/A")

        return unit_price, package_type, quantity_available, datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    except (IndexError, KeyError) as e:
        print(f"Error processing product details: {e}")
        return "/", "/", "/", datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"An unexpected error occurred while processing product details: {e}")
        return "/", "/", "/", datetime.now().strftime('%Y-%m-%d %H:%M:%S')
