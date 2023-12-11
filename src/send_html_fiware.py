import requests
import json
from datetime import datetime
from base64 import b64encode

def read_data():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    temp = 24

    return {
        'temperature': {"type":"Float", "value": temp},
        'dateObserved': {"type":"string", "value": now}
    }

def send_data(configfilename):

    try:
        with open(configfilename, "r") as f:
            c = json.load(f)
            c = c['send']
    except FileNotFoundError:
        print("The config file was not found at: ", configfilename)
        raise SystemExit
    except AttributeError as e:
        print("The config file ('", configfilename, "') was not as expected: ", e)
        raise SystemExit

    authaddress = c['authaddress']
    brokeraddress = c['brokeraddress']

    try:
        basicauth = b64encode(bytes(c['basicuser'] + ":" + c['basicpass'], 'utf-8')).decode('ascii')
        data = {
            'username': c['username'],
            'password': c['password'],
            'grant_type': 'password'
        }
    except json.decoder.JSONDecodeError as e:
        print("The config file ('", configfilename, "') did not contain valid json: ", e)
        raise SystemExit
    except AttributeError as e:
        print("The config file ('", configfilename, "') was not as expected: ", e)
        raise SystemExit

    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Basic " + basicauth
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    try:
        authresponse = requests.post(authaddress, headers=headers, data=data)
    except Exception as e:
        print("Failed to connect to the auth service: ", e)
        raise SystemExit

    body = read_data()

    try:
        answer = requests.patch(brokeraddress + "urn:ngsi-ld:WaterQualityObserved:22:Scan_Temperature/attrs", verify = False, headers = { 'Content-Type':'application/json', 'X-Auth-Token': authresponse.json()["access_token"], },data = json.dumps(body))
        print("The connection was established fine:", answer.ok)
    except Exception as e:
        print("Failed to connect to the FIWARE service: ", e)

if __name__ == '__main__':
    print("These lines of code are thought to be used as a library..")

