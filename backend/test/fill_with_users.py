import requests
import random
import uuid

# The endpoint URL
url = 'http://localhost:8000/users/registration'

# List of possible roles
roles = ['Solarteur', 'Energieberatende', 'Haushalte', 'Netzbetreiber']

# Function to send a POST request
def send_post_request(request_number):
    # Randomly choose a role
    role = random.choice(roles)

    # Generate a unique email using UUID
    unique_email = f"user{request_number}-{uuid.uuid4()}@example.com"

    # Data to be sent in POST request
    data = {
        "vorname": "Max",
        "nachname": "Mustermann",
        "telefonnummer": "1",
        "email": unique_email,
        "passwort": "123",
        "rolle": role,
        "geburtsdatum": "2002-04-02",
        "adresse_id": 1,
        "titel": "dd"
    }

    # Sending the POST request
    response = requests.post(url, json=data)
    return response

# Sending 50 requests
for i in range(50):
    response = send_post_request(i)


# Note: Add error handling as needed
