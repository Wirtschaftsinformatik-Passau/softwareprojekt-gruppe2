import requests
import random
import uuid

# The endpoint URL
url = 'http://132.231.36.102:8000/users/registration'

# List of possible roles
roles = ['Solarteure', 'Energieberatende', 'Haushalte', 'Netzbetreiber']

# Function to send a POST request

hh = {"vorname":"Max","nachname":"Mustermann","telefonnummer":"1","email":"h@h.de","passwort":"123","rolle":"Haushalte","geburtsdatum":"2002-04-02","adresse_id":1,"titel":"dd"}
admin = {"vorname":"Max","nachname":"Mustermann","telefonnummer":"1","email":"1@0.de","passwort":"123","rolle":"Admin","geburtsdatum":"2002-04-02","adresse_id":1,"titel":"dd"}
nb = {"vorname":"Max","nachname":"Mustermann","telefonnummer":"1","email":"n@b.de","passwort":"123","rolle":"Netzbetreiber","geburtsdatum":"2002-04-02","adresse_id":1,"titel":"dd"}
ss = {"vorname":"Max","nachname":"Mustermann","telefonnummer":"1","email":"s@s.de","passwort":"123","rolle":"Solarteure","geburtsdatum":"2002-04-02","adresse_id":1,"titel":"dd"}
eb = {"vorname":"Max","nachname":"Mustermann","telefonnummer":"1","email":"e@b.de","passwort":"123","rolle":"Energieberatende","geburtsdatum":"2002-04-02","adresse_id":1,"titel":"dd"}


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


for x in [hh, admin, nb, ss, eb]:
    response = requests.post(url, json=x)
    print(response)


# Sending 50 requests
for i in range(50):
    response = send_post_request(i)


# Note: Add error handling as needed