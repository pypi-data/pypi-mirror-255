import argparse
import pandas as pd
import sys

excel_extension='.xlsx'

def main():
    parser = argparse.ArgumentParser(description='Process an Excel file.')
    # Make excel_file a positional argument but do not enforce as required
    parser.add_argument('excel_file', type=str, nargs='?', help='Excel file to process')

    args = parser.parse_args()

    # Check if the excel_file argument was provided
    if args.excel_file is None:
        print("An Excel file is needed to run this script.")
        # Optionally, you can also show the help message
        parser.print_help()
        # Exit the script gracefully
        sys.exit(1)

    # If an Excel file is provided, process it
    try:
        filename=args.excel_file
        has_extension=filename[-len(excel_extension):]==excel_extension
        if has_extension:
            file_to_read=filename
        else:
            file_to_read=filename+excel_extension
        data = pd.read_excel(file_to_read)
        print("Excel File Content:")
        print(data)
    except Exception as e:
        print(f"Failed to process the Excel file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
