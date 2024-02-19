import requests

# move thnkrSDK.py into thnkrAI root (next to client) for development
# move thnkrSDK.py back into thnkrAI/thnkrSDK/thnkrSDK (next to __init__) for PyPI

BASE_URL = 'https://api.thnkrai.com/'
#BASE_URL = 'http://localhost:8000/'

def ping():
   response = requests.get(BASE_URL)
   return response.json()


def example(model):
   response = requests.get(BASE_URL + model)
   return response.json()


def predict(model, input, username, password):
   headers = {
      'Content-Type': 'application/json',
   }

   payload = { # change input so it takes raw json (user is informed by example) rather than direct values
      "Title": input,
      "Username": username,
      "Password": password,
   }

   response = requests.post(BASE_URL + model, headers=headers, json=payload) # add error handling if anything other than response 200
   
   return round(float(response.json()['Prediction']), 2)