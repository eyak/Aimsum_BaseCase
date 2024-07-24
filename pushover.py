import settings
import os
import http.client, urllib

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
    conn.getresponse()


if __name__ == '__main__':
    send_pushover("Hello, World!")