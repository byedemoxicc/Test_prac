import requests
import sys
from datetime import date, timedelta, datetime
import pandas as pd
import ast
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import warnings
warnings.filterwarnings("ignore")
from flask import Flask, request, jsonify
app = Flask(__name__)




# Replace with the path to your JSON key file
key_file_path = './testproject-399514-0d09df043363.json'

# Replace with the ID of your Google Sheets file (can be found in the URL of the open sheet)
spreadsheet_id = '1ROTMvFrKSKy_XJDT5fmeEltq_HvZNza8-aN8XYMiYw8'

# Replace with the name of the sheet you want to write data to
worksheet_name = 'Sheet1'

# Set up the connection to the Google Sheets API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file_path, scope)
client = gspread.authorize(credentials)

# Open the Google Sheets file and get the worksheet
spreadsheet = client.open_by_key(spreadsheet_id)
worksheet = spreadsheet.worksheet(worksheet_name)





@app.route('/run_script', methods=['GET'])
def run_script():



    # Clear the worksheet
    worksheet.clear()
    today=date.today()


    try:
        left_limit= datetime.strptime(request.args.get('update_from'), '%Y-%m-%d').date()
    except:
        left_limit = today


    try:
        right_limit= datetime.strptime(request.args.get('update_to'), '%Y-%m-%d').date()
    except:
        right_limit = today


    # Generate a list of dates from start_date to end_date
    dates = [left_limit + timedelta(days=i) for i in range((right_limit - left_limit).days + 1)]

    data_array=[]
    for d in dates:
        send_date=d.strftime('%Y-%m-%d')
        params = {
                "date": send_date.replace('-',''),
                "valcode": "USD",
                'json' : ''    # currency
            }

        response = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?", params=params, timeout=30)

        html_content=response.text
        data=ast.literal_eval(html_content)
        data_array.append(data[0])



    # Convert scalar values to lists and add values from data2 and data3
    data = {key: [value] for key, value in data_array[0].items()}

    for d in data_array:
        for key, value in d.items():
            data[key].append(value)   


    df=pd.DataFrame(data)
    df=df.drop([0])

    print(df)
    # Write the DataFrame to the worksheet
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    return jsonify(status="success", data=data_array)


if __name__ == '__main__':
   app.run(debug=True)