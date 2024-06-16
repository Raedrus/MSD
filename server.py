from flask import Flask, request, jsonify
import pandas as pd
import os
import traceback

app = Flask(__name__)

if not os.path.exists('data'):
    os.makedirs('data')

columns = ['time', 'E_device', 'General Waste', 'Battery', 'Alu_can', 'Total']
excel_file = 'data/rubbish_data.xlsx'

# Check if Excel file exists, load existing data if it does
if os.path.exists(excel_file):
    df = pd.read_excel(excel_file)
else:
    df = pd.DataFrame(columns=columns)

@app.route('/submit_data', methods=['POST'])
def submit_data():
    global df
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        time = data.get('time')
        e_device_quantity = data.get('E_device', 0)
        general_waste_quantity = data.get('General Waste', 0)
        battery_quantity = data.get('Battery', 0)
        alu_can_quantity = data.get('Alu_can', 0)
        total_rubbish = data.get('Total', 0)  # Get total from JSON data

        new_data = {
            'time': time,
            'E_device': e_device_quantity,
            'General Waste': general_waste_quantity,
            'Battery': battery_quantity,
            'Alu_can': alu_can_quantity,
            'Total': total_rubbish
        }

        # Append new data to existing DataFrame
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

        # Save DataFrame to Excel file
        df.to_excel(excel_file, index=False)

        return jsonify({"message": "Data received and saved"}), 200

    except Exception as e:
        print("Error occurred:", e)
        print(traceback.format_exc())  # Print the traceback for detailed error information
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
