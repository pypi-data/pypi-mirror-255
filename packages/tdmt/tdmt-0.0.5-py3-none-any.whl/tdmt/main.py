import argparse
import pandas as pd

def print_about():
    about_text = """tdmt 1.0
This is a simple command-line tool to process Excel files.
Developed by [Your Name or Your Organization]."""
    print(about_text)

def main(excel_file):  
    parser = argparse.ArgumentParser(description='Process an Excel file.')

    # Version argument
    parser.add_argument('--version', action='version', version='tdmt 1.0')

    # About argument
    parser.add_argument('--about', action='store_true', help='Show information about this application')

    # Positional argument for the Excel file name, making it optional to allow --version and --about
    parser.add_argument('excel_file', type=str, nargs='?', help='Excel file to process', default=None)

    args = parser.parse_args()

    # Handle the --about option
    if args.about:
        print_about()
    elif args.excel_file:
        # Call the main function with the Excel file name if provided
        data = pd.read_excel(excel_file)
        print("Excel File Content:")
        print(data)
    else:
        # If no arguments are provided, print the help message
        parser.print_help()

if __name__ == "__main__":
    main()