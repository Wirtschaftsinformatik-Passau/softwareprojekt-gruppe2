import requests
import random
import uuid
import numpy as np

# The endpoint URL
url = "http://132.231.36.102:8000/netzbetreiber/preisstrukturen"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo1NSwiZXhwIjoxNzA2NzgwMTgzfQ.pmY2etQt0Qrni44n5krMr_jtUD36tX9LocLdBisHcJc"
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