from datetime import datetime, timezone
import gpsd
import geohash2
import json
import math
import os
from pymodbus.client import ModbusTcpClient
from pymodbus import ModbusException
from struct import *
import time

def convert_bytes_to_float(int1, int2):
    hex1 = (int1).to_bytes(2,byteorder='little')
    hex2 = (int2).to_bytes(2,byteorder='little')
    return 0 if math.isnan(float(unpack("<f",hex2 + hex1)[0])) else unpack("<f",hex2 + hex1)[0]

def geohash():
    try:
        gpsd.connect()
        packet = gpsd.get_current()
        return geohash2.encode(packet.position()[0],packet.position()[1])
    except ConnectionRefusedError:
        print("Could not connect to the GPS device.")
        raise SystemExit
    except Exception as e:
        print("Could not get GPS info: ", e)
        raise SystemExit

def collect_data(configfilename):
    try:
        with open(configfilename, "r") as f:
            c = json.load(f)
            d = c['data']
            c = c['collect']
    except FileNotFoundError:
        print("The config file was not found at: ", configfilename)
        raise SystemExit
    except AttributeError as e:
        print("The config file ('", configfilename, "') was not as expected: ", e)
        raise SystemExit

    sensor_hub_address = c['sensor_hub_address']
    epoch = datetime(1970,1,1,tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    nano = int((now - epoch).total_seconds() * 1000000000)
    storage_dir = d['storage_directory_new']
    storage_file = storage_dir + "/" + str(nano) + d['storage_file_suffix']

    if c['use_gps'] == "true":
        gh = geohash()
    else:
        gh = 'u'

    client = ModbusTcpClient(sensor_hub_address)
    # just try a couple of times if necessary...
    for i in range(0, 15):
        try:
            r = client.read_input_registers(
                    int(c['modbus_input_register_address']),
                    int(c['modbus_input_register_count'])
                )
            break
        except ModbusException:
            time.sleep(2)
            continue

    try:
        m = {
                d['timestamp_name']: str(nano),
                d['geohash_name']: gh
            }
        for k, v in d['value_register_map'].items():
            try:
                m[k] = str(convert_bytes_to_float(
                            r.registers[int(v['modbus_reg0'])],
                            r.registers[int(v['modbus_reg1'])]
                        ))
            except (KeyError, ValueError):
                continue
    except UnboundLocalError:
        print("Could not connect to Modbus-TCP...")
        raise SystemExit
    except IndexError as e:
        print("Have you used in the wrong register count in the config?", e)
        raise SystemExit

    try:
        os.makedirs(os.path.dirname(storage_dir), exist_ok=True)
        with open(storage_file, 'a') as f:
            json.dump(m, f)
    except Exception as e:
        print("Unable to create the data file '" + storage_file + "'!\n", e)
        raise SystemExit

