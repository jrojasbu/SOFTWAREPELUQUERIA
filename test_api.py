import requests

url = 'http://127.0.0.1:5000/api/service-demand?sede=Bolivia'

try:
    response = requests.get(url)
    print('Status:', response.status_code)
    if response.status_code == 200:
        data = response.json()
        print('Historical length:', len(data.get('historical', [])))
        print('Prediction length:', len(data.get('prediction', [])))
        if data['historical']:
            print('Sample historical:', data['historical'][0])
        if data['prediction']:
            print('Sample prediction:', data['prediction'][0])
    else:
        print('Response:', response.text)
except Exception as e:
    print('Error:', e)