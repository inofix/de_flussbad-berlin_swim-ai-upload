from datetime import datetime, timezone
import gpsd
import geohash2
import json
import logging
import math
import os
from pymodbus.client import ModbusTcpClient
from pymodbus import ModbusException
from struct import *
import time

def convert_byte_registers_to_float(register_array):
    hex1 = (int(register_array[0])).to_bytes(2,byteorder='little')
    hex2 = (int(register_array[1])).to_bytes(2,byteorder='little')
    return 0 if math.isnan(float(unpack("<f",hex2 + hex1)[0])) else unpack("<f",hex2 + hex1)[0]

def geohash():
    try:
        gpsd.connect()
        packet = gpsd.get_current()
        return geohash2.encode(packet.position()[0],packet.position()[1])
    except ConnectionRefusedError:
        logging.error("Could not connect to the GPS device.")
        raise SystemExit
    except Exception as e:
        logging.error("Could not get GPS info: ", e)
        raise SystemExit

def collect_data(configfilename):
    try:
        with open(configfilename, "r") as f:
            c = json.load(f)
            d = c['data']
            c = c['collect']
        logging.basicConfig(filename=c["log_filename"], encoding=c["log_encoding"], level=c["log_level"])
    except FileNotFoundError:
        logging.critical("The config file was not found at: ", configfilename)
        raise SystemExit
    except AttributeError as e:
        logging.critical("The config file ('", configfilename, "') was not as expected: ", e)
        raise SystemExit

    sensor_hub_address = c['sensor_hub_address']
    epoch = datetime(1970,1,1,tzinfo=timezone.utc)
    # only calculate now once in order to keep the measurments related (e.g. temp+condu)
    now = datetime.now(timezone.utc)
    nano = int((now - epoch).total_seconds() * 1000000000)
    storage_dir = d['storage_directory_new']
    storage_file = storage_dir + "/" + str(nano) + d['storage_file_suffix']

    if c['use_gps'] == "true":
        gh = geohash()
    else:
        gh = 'u'

    try:
        m = {
                d['timestamp_name']: str(nano),
                d['geohash_name']: gh
            }
        client = ModbusTcpClient(sensor_hub_address)
        for k, v in d['value_register_map'].items():
            # just try a couple of times if necessary...
            r = None
            for i in range(0, 8):
                try:
                    r = client.read_input_registers(
                            int(v['modbus_address']),
                            int(v['modbus_count'])
                        )
                    break
                except ValueError:
                    logging.error("Your config file might have unvalid values for modbus at entry:", k)
                    raise SystemExit
                except ModbusException:
                    time.sleep(2)
                    continue
            try:
                m[k] = str(convert_byte_registers_to_float(r.registers))
            except (KeyError, ValueError):
                continue
    except UnboundLocalError:
        logging.error("Could not connect to Modbus-TCP...")
    except IndexError as e:
        logging.critical("Have you used in the wrong register count in the config?", e)
        raise SystemExit

    try:
        os.makedirs(os.path.dirname(storage_dir), exist_ok=True)
        with open(storage_file, 'a') as f:
            json.dump(m, f)
    except Exception as e:
        logging.critical("Unable to create the data file '" + storage_file + "'!\n", e)
        raise SystemExit

