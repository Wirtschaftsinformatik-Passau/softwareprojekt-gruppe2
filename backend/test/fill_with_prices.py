import requests
import random
import uuid
import numpy as np

# The endpoint URL
url = "http://localhost:8000/netzbetreiber/preisstrukturen"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjozLCJleHAiOjE3MDMwOTk5MDh9.euw3-wn7WzKRWvLvk1qfK1YPOsIlO2gWOBZGnh8Lh28"
headers = {"Authorization": f"Bearer {token}"}

def send_post_request(request_number):

    # Data to be sent in POST request
    data = {
  "bezugspreis_kwh": np.random.randint(0,10),
  "einspeisung_kwh": np.random.randint(0,10)
}

    # Sending the POST request
    response = requests.post(url, json=data, headers=headers)
    return response




if __name__ == "__main__":# Sending 50 requests
    for i in range(50):
        response = send_post_request(i)


