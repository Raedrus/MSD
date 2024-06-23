from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

# Path to your service account key file
SERVICE_ACCOUNT_FILE = '/home/msd/keys.json'  # Replace with the correct path

# Scope for Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Your Google Sheets ID
SPREADSHEET_ID = '1vLEIQH3S5VCM8HBSe9u4XTnN9Pf5i-HnmZ4PGrxzfBE'  # Replace with your actual spreadsheet ID

# The name of the sheet where you want to append the data (e.g., "Sheet1")
SHEET_NAME = 'Database'

# New values to append (example values)
e_quant = 2
g_quant = 3
b_quant = 2
a_quant = 3

event = '-'  # Example event, replace with your actual event

def get_reset_counts(data):
    if not data:
        return 0, 0

    last_row = data[-1]
    last_datetime_str = last_row[0]  # Assuming the datetime is in the first column
    last_event = last_row[7]  # Assuming the event is in the eighth column
    last_hour_reset_count = int(last_row[5])  # Assuming the hour reset count is in the sixth column
    last_day_reset_count = int(last_row[6])  # Assuming the day reset count is in the seventh column

    last_datetime = datetime.datetime.strptime(last_datetime_str, "%Y-%m-%d %H:%M:%S")
    current_datetime = datetime.datetime.now()

    if last_datetime.date() == current_datetime.date():
        day_reset_count = last_day_reset_count
    else:
        day_reset_count = 0

    if last_datetime.hour == current_datetime.hour and last_datetime.date() == current_datetime.date():
        hour_reset_count = last_hour_reset_count
    else:
        hour_reset_count = 0

    return hour_reset_count, day_reset_count

def main():
    # Authenticate using the service account
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Build the service
    service = build('sheets', 'v4', credentials=credentials)

    # Fetch the existing data
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=SHEET_NAME).execute()
    data = result.get('values', [])

    # Calculate the new reset counts
    hour_reset, day_reset = get_reset_counts(data)

    # Increment the reset count if the event is "Reset"
    if event == "Reset":
        day_reset += 1
        hour_reset += 1

    # Prepare the data to append
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    values = [
        [date_str, e_quant, g_quant, b_quant, a_quant, hour_reset, day_reset, event]
    ]
    body = {
        'values': values
    }

    # Call the Sheets API to append the data
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_NAME,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    print(f"{result.get('updates').get('updatedCells')} cells appended.")

if __name__ == '__main__':
    main()

