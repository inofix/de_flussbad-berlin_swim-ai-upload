from base64 import b64encode
from datetime import datetime, timezone
import glob
import json
import logging
import os
import requests
import shutil

def send_data(configfilename):

    try:
        with open(configfilename, "r") as f:
            c = json.load(f)
            d = c['data']
            c = c['send']
            logging.basicConfig(filename=c["log_filename"], encoding=c["log_encoding"], level=c["log_level"])
    except FileNotFoundError:
        logging.critical("The config file was not found at: ", configfilename)
        raise SystemExit
    except json.decoder.JSONDecodeError as e:
        logging.critical("The config file ('", configfilename, "') did not contain valid json: ", e)
        raise SystemExit
    except AttributeError as e:
        logging.critical("The config file ('", configfilename, "') was not as expected: ", e)
        raise SystemExit

    now_dirs = datetime.now(timezone.utc).strftime('/%Y/%m/%d')
    storage_dir_new = d['storage_directory_new']
    storage_dir_old = d['storage_directory_archive'] + now_dirs
    storage_dir_junk = d['storage_directory_junk']
    storage_file_suffix = d['storage_file_suffix']
    try:
        try:
            os.makedirs(os.path.dirname(storage_dir_new + '/'))
        except FileExistsError:
            pass
        try:
            os.makedirs(os.path.dirname(storage_dir_old + '/'))
        except FileExistsError:
            pass
        try:
            os.makedirs(os.path.dirname(storage_dir_junk + '/'))
        except FileExistsError:
            pass
    except PermissionError:
        logging.critical("You do not have the permission to write here.\n",
                storage_dir_new, storage_dir_old, storage_dir_junk)
        raise SystemExit

    authaddress = c['authentication_address']
    brokeraddress = c['broker_address']

    try:
        basicauth = b64encode(bytes(c['basic_username'] + ":" + c['basic_password'], 'utf-8')).decode('ascii')
        data = {
            'username': c['username'],
            'password': c['password'],
            'grant_type': 'password'
        }
    except json.decoder.JSONDecodeError as e:
        logging.error("The auth data did not contain valid json: ", e)
        raise SystemExit
    except AttributeError as e:
        logging.error("The auth request could not be encoded and generated: ", e)
        raise SystemExit

    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Basic " + basicauth
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    try:
        authresponse = requests.post(authaddress, headers=headers, data=data)
    except Exception as e:
        logging.error("Failed to connect to the auth service: ", e)
        raise SystemExit

    try:
        request_headers = {
            'Content-Type': 'application/json',
            'X-Auth-Token': authresponse.json()["access_token"]
        }
    except json.decoder.JSONDecodeError as e:
        logging.error("The request headers could not be formed: ", e)
        raise SystemExit

    do_verify = True
    if c['verify_certificate'].lower() in ['false', 'no', 'n', '0']:
        do_verify = False

    for f in glob.glob(storage_dir_new + '/[0-9]*' + storage_file_suffix):
        try:
            with open(f) as t:
                j = json.load(t)
            try:
                timestamp = datetime.fromtimestamp(
                        int(j[d['timestamp_name']]) // 1000000000)
                dbtime = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                dbtimeid = d['timestamp_db_name']
                #TODO geohash ...
            except KeyError:
                logging.error("Can not continue, there was no timestamp in the file.")
                raise SystemExit

            for k, v in d['value_register_map'].items():
                try:
                    data = {
                        v["swim_id"]: {"type":v['type'], "value": j[k]},
                        dbtimeid: {"type":"string", "value": dbtime}
                    }
                    logging.debug(data)
                except KeyError:
                    continue
                jdata = json.dumps(data)
                url = brokeraddress + "urn:ngsi-ld:" + v["fiware_type"] +\
                    ":" + v["fiware_id"] + ":" + v["fiware_name"] + "/attrs"
                logging.debug(url)
                try:
                    answer = requests.patch(url, verify = False,
                        headers = request_headers, data = jdata)
                    logging.info("The connection was established fine:", answer.ok, "(" + answer.status_code + ")")
                except Exception as e:
                    logging.warning("Failed to connect to the FIWARE service: ", e)

            shutil.move(f, storage_dir_old)

        except json.decoder.JSONDecodeError:
            shutil.move(f, storage_dir_junk)
            continue

if __name__ == '__main__':
    print("These lines of code are thought to be used as a library..")

