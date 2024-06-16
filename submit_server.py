### Open the server first before submitting
### Make sure the IP address is updated

import requests
from datetime import datetime

# detect time
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

url = "http://127.0.0.1:5000/submit_data"

# Rubbish Quantity
e_quant = 5
g_quant = 5
b_quant = 5
a_quant = 5

total_rubbish = e_quant+g_quant+b_quant+a_quant


data = {
    'time': current_time,
    'E_device': e_quant,
    'General Waste': g_quant,
    'Battery': b_quant,
    'Alu_can': a_quant,
    'Total': total_rubbish
}

try:
    response = requests.post(url, json=data)
    response.raise_for_status()  # Raise an error for bad status codes
    print("Response status code:", response.status_code)
    print("Response content:", response.text)  # Print raw response content
    print(response.json())  # Parse response as JSON
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
except ValueError as e:
    print(f"Response content is not valid JSON: {e}")
