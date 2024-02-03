import requests
import random
import uuid
import numpy as np

# The endpoint URL
url = "http://132.231.36.102:8000/netzbetreiber/tarife"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo1NSwiZXhwIjoxNzA2NzgwMTgzfQ.pmY2etQt0Qrni44n5krMr_jtUD36tX9LocLdBisHcJc"
headers = {"Authorization": f"Bearer {token}"}

def send_post_request(request_number):
    # Randomly choose a role


    # Generate a unique email using UUID
    unique_name = f"Tarif {request_number}_{uuid.uuid4()}"

    # Data to be sent in POST request
    data = {
        "tarifname": unique_name,
        "preis_kwh": round(np.random.rand(),2),
        "grundgebuehr": np.random.randint(0, 10),
        "laufzeit":np.random.randint(0, 20),
        "spezielle_konditionen": "Keine"
        }

    # Sending the POST request
    response = requests.post(url, json=data, headers=headers)
    print(response.status_code)
    return response




if __name__ == "__main__":# Sending 50 requests
    for i in range(50):
        response = send_post_request(i)