# Weekly Reports Generator

This project automates the process of generating and updating weekly reports.
***Its a personalised project, I don't advice cloning***

## Features

- Fetches data from GraphQL API
- Processes Excel files for raw data
- Combines data from multiple sources
- Generates a consolidated report
- Automatically updates Google Sheets

## Files

- `bd2.py`: Main script for data fetching and processing
- `send_to_sheet.py`: Script to send processed data to Google Sheets
- `.env`: Contains environment variables (e.g., API tokens)
- `.gitignore`: Specifies intentionally untracked files

## Usage

1. Ensure all dependencies are installed
2. Set up the `.env` file with the necessary API token
3. Run `send_to_sheet.py` to generate and update the report

Note: Make sure to keep sensitive information secure and not commit it to version control.
