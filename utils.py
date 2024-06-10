import glob
import pandas as pd

def read_part_numbers(file_pattern='*_v*_BOM.csv'):
    files = glob.glob(file_pattern)

    if files:
        csv_file_name = files[0]
        try:
            df = pd.read_csv(csv_file_name)
            return df, csv_file_name
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None, None
    else:
        print(f"No files found matching the pattern: {file_pattern}")
        return None, None

def update_dataframe(df, new_columns, new_file_name):
    try:
        for col_name, col_data in new_columns.items():
            df[col_name] = col_data
        df.to_csv(new_file_name, index=False)
        print(f"\nUpdated CSV saved as {new_file_name}")
    except Exception as e:
        print(f"Error updating DataFrame: {e}")
