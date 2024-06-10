import os
from dotenv import load_dotenv
from mouser import get_mouser_product_details, process_mouser_part_details
from digikey import get_digikey_access_token, get_digikey_product_details, process_digikey_part_details
from utils import read_part_numbers, update_dataframe
from datetime import datetime

load_dotenv()
mouser_api_key = os.getenv("MOUSER_API_KEY")
digikey_client_id = os.getenv("DIGIKEY_CLIENT_ID")
digikey_client_secret = os.getenv("DIGIKEY_CLIENT_SECRET")

if __name__ == "__main__":
    df, csv_file_name = read_part_numbers()
    error_list = []

    if df is not None:
        new_columns = {
            'Mouser - Unit Price': [],
            'Mouser - Package Type': [],
            'Mouser - Quantity Available': [],
            'Mouser - Last Updated': [],
            'DigiKey - Unit Price': [],
            'DigiKey - Package Type': [],
            'DigiKey - Quantity Available': [],
            'DigiKey - Last Updated': []
        }

        access_token = get_digikey_access_token(digikey_client_id, digikey_client_secret)

        for index, row in df.iterrows():
            part_number = row.get("MPN", "")
            reference = row.get("Reference", "")
            print(f"\nProcessing row {index+1}/{len(df)}: Reference: {reference}, Part Number: {part_number}")

            if part_number in ("", "/"):
                print(f"Part number is empty or invalid ('{part_number}'). Filling with default values.")
                unit_price = package_type = availability = quantity_available = "/"
                last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                new_columns['Mouser - Unit Price'].append(unit_price)
                new_columns['Mouser - Package Type'].append(package_type)
                new_columns['Mouser - Quantity Available'].append(availability)
                new_columns['Mouser - Last Updated'].append(last_updated)
                new_columns['DigiKey - Unit Price'].append(unit_price)
                new_columns['DigiKey - Package Type'].append(package_type)
                new_columns['DigiKey - Quantity Available'].append(quantity_available)
                new_columns['DigiKey - Last Updated'].append(last_updated)
                error_list.append((index + 1, part_number, reference, "Invalid or missing MPN"))
                continue

            # Mouser details
            mouser_error = False
            if part_number:
                mouser_details = get_mouser_product_details(part_number, mouser_api_key)
                if mouser_details:
                    try:
                        unit_price, package_type, availability, last_updated = process_mouser_part_details(part_number, mouser_details)
                    except Exception as e:
                        print(f"Error processing Mouser details for part number {part_number}: {e}")
                        unit_price, package_type, availability, last_updated = "/", "/", "/", datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        mouser_error = True
                else:
                    print(f"No details found for part number {part_number} in Mouser.")
                    unit_price, package_type, availability, last_updated = "/", "/", "/", datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    mouser_error = True
                new_columns['Mouser - Unit Price'].append(unit_price)
                new_columns['Mouser - Package Type'].append(package_type)
                new_columns['Mouser - Quantity Available'].append(availability)
                new_columns['Mouser - Last Updated'].append(last_updated)
                if mouser_error:
                    error_list.append((index + 1, part_number, reference, "Mouser"))

            # DigiKey details
            digikey_error = False
            if part_number and access_token:
                digikey_details = get_digikey_product_details(part_number, access_token, digikey_client_id)
                if digikey_details:
                    try:
                        unit_price, package_type, quantity_available, last_updated = process_digikey_part_details(digikey_details)
                    except Exception as e:
                        print(f"Error processing DigiKey details for part number {part_number}: {e}")
                        unit_price, package_type, quantity_available, last_updated = "/", "/", "/", datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        digikey_error = True
                else:
                    print(f"No details found for part number {part_number} in DigiKey.")
                    unit_price, package_type, quantity_available, last_updated = "/", "/", "/", datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    digikey_error = True
                new_columns['DigiKey - Unit Price'].append(unit_price)
                new_columns['DigiKey - Package Type'].append(package_type)
                new_columns['DigiKey - Quantity Available'].append(quantity_available)
                new_columns['DigiKey - Last Updated'].append(last_updated)
                if digikey_error:
                    error_list.append((index + 1, part_number, reference, "DigiKey"))
            else:
                if not access_token:
                    print("Failed to obtain DigiKey access token.")
                new_columns['DigiKey - Unit Price'].append("/")
                new_columns['DigiKey - Package Type'].append("/")
                new_columns['DigiKey - Quantity Available'].append("/")
                new_columns['DigiKey - Last Updated'].append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                if part_number:
                    error_list.append((index + 1, part_number, reference, "DigiKey"))

        # Check lengths before updating dataframe
        if all(len(col) == len(df) for col in new_columns.values()):
            new_file_name = csv_file_name.rstrip('.csv') + "_availability.csv"
            update_dataframe(df, new_columns, new_file_name)
        else:
            print("Error: Mismatch in the length of new columns and DataFrame rows.")
            for col_name, col_data in new_columns.items():
                print(f"{col_name} length: {len(col_data)}, DataFrame length: {len(df)}")

        # Print errors if any
        if error_list:
            print("\nItems with errors that need to be checked manually:")
            for error in error_list:
                print(f"Row {error[0]}, Reference: {error[2]}, Part Number: {error[1]}, Source: {error[3]}")
    else:
        print("Failed to read part numbers from CSV.")
