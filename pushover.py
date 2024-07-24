import settings
import os
import http.client, urllib
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

key = os.getenv('PUSHOVER_KEY')
token = os.getenv('PUSHOVER_TOKEN')

def send_pushover(msg):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": token,
        "user": key,
        "message": msg,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    res = conn.getresponse()

    if res.status != 200:
        print(f"Error sending pushover: {res.status}, {res.reason}")


if __name__ == '__main__':
    send_pushover("Hello, World!")