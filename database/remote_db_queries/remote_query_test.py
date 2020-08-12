import requests 
import json

url = r'http://localhost:8051'
data = {'query': 'SELECT * FROM fits_data;'}
data_json = json.dumps(data)
headers = {'Content/type': 'application/json'}

r = requests.get(url, data=data_json, headers=headers)

print(r.status_code)
print(r.content)