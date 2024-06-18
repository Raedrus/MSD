### Open the server first before submitting
### Make sure the IP address is updated

import requests
from datetime import datetime

# Detect current time
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# URL of the server endpoint
url = "http://127.0.0.1:5000/submit_data"

# Rubbish quantities (example values)
e_quant = 2
g_quant = 2
b_quant = 1
a_quant = 3

# Calculate total rubbish quantity
total_rubbish = e_quant + g_quant + b_quant + a_quant

# Flag indicating if dustbin is reset (set according to your logic)
dustbin_reset = 0  # Change this as per your actual condition

event = ''

if event == '':
    if dustbin_reset == 1:
        event = "Reset"

# Prepare data to send as JSON
data = {
    'time': current_time,
    'E_device': e_quant,
    'General Waste': g_quant,
    'Battery': b_quant,
    'Alu_can': a_quant,
    'Total': total_rubbish,
    'Reset_Count_per_day': dustbin_reset,  # Include the 'Reset' field
    'Event': event
}

try:
    # Send POST request with JSON data to the server
    response = requests.post(url, json=data)

    # Check if the request was successful
    response.raise_for_status()  # Raises an error for bad status codes

    # Print response details
    print("Response status code:", response.status_code)
    print("Response content:", response.text)  # Print raw response content

    # Parse response as JSON (if applicable)
    print(response.json())  # Parse response as JSON

except requests.exceptions.RequestException as e:
    # Handle any errors that occur during the request
    print(f"An error occurred: {e}")

except ValueError as e:
    # Handle if response content is not valid JSON
    print(f"Response content is not valid JSON: {e}")
