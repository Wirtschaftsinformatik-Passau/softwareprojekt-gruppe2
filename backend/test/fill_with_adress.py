import requests

adresses = [{
    "strasse": "Große Klingergasse",
    "hausnummer": 4,
    "plz": 94032,
    "stadt": "Passau",
    "land": "Deutschland"

},
    {
        "strasse": "Große Klingergasse",
        "hausnummer": 20,
        "plz": 94032,
        "stadt": "Passau",
        "land": "Deutschland"

    }
,
    {
        "strasse": "Große Klingergasse",
        "hausnummer": 16,
        "plz": 94032,
        "stadt": "Passau",
        "land": "Deutschland"

    }
,
    {
        "strasse": "Höllgasse",
        "hausnummer": 22,
        "plz": 94032,
        "stadt": "Passau",
        "land": "Deutschland"

    },
{
        "strasse": "Innstrasse",
        "hausnummer": 2,
        "plz": 94032,
        "stadt": "Passau",
        "land": "Deutschland"

    },
{
        "strasse": "Innstrasse",
        "hausnummer": 13,
        "plz": 94032,
        "stadt": "Passau",
        "land": "Deutschland"

    },
{
        "strasse": "Innstrasse",
        "hausnummer": 49,
        "plz": 94032,
        "stadt": "Passau",
        "land": "Deutschland"

    }
]

url = 'http://132.231.36.102:8000/users/adresse'
def send_post_request(request_number):


    # Data to be sent in POST request
    data = adresses[request_number]
    # Sending the POST request
    response = requests.post(url, json=data)
    print(response)
    return response




# Sending 50 requests
for i in range(len(adresses)):
    response = send_post_request(i)