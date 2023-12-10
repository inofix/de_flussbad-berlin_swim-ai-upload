from datetime import datetime, timezone
import gpsd
#import geohash2
from pymodbus.client import ModbusTcpClient
from struct import *
import math
import time

con_cube_ip = ''
#gpsd.connect()
epoch = datetime(1970,1,1,tzinfo=timezone.utc)
now = datetime.now(timezone.utc)
nano = int((now - epoch).total_seconds() * 1000000000)

#packet = gpsd.get_current()
#try:
#    ghash = geohash2.encode(packet.position()[0],packet.position()[1])
#except:
ghash = 'u'


def convert_bytes_to_float(int1, int2):
    hex1 = (int1).to_bytes(2,byteorder='little')
    hex2 = (int2).to_bytes(2,byteorder='little')
    return 0 if math.isnan(float(unpack("<f",hex2 + hex1)[0])) else unpack("<f",hex2 + hex1)[0]



for i in range(1,9):
    try:
        client = ModbusTcpClient(con_cube_ip)
        r = client.read_input_registers(0x0080, 116)
        line = 'data,geohash=' + ghash + ' ' + \
               'xP1Value=' + str(convert_bytes_to_float(r.registers[2], r.registers[3])) + \
               ',xP2Value=' + str(convert_bytes_to_float(r.registers[10], r.registers[11])) + \
               ',xP3Value=' + str(convert_bytes_to_float(r.registers[18], r.registers[19])) + \
               ',xP4Value=' + str(convert_bytes_to_float(r.registers[26], r.registers[27])) + \
               ',xP5Value=' + str(convert_bytes_to_float(r.registers[34], r.registers[35])) + \
               ',xP6Value=' + str(convert_bytes_to_float(r.registers[42], r.registers[43])) + \
               ',xP7Value=' + str(convert_bytes_to_float(r.registers[50], r.registers[51])) + \
               ',xP8Value=' + str(convert_bytes_to_float(r.registers[58], r.registers[59])) + \
               ',xP9Value=' + str(convert_bytes_to_float(r.registers[66], r.registers[67])) + \
               ',xP10Value=' + str(convert_bytes_to_float(r.registers[74], r.registers[75])) + \
               ',xP11Value=' + str(convert_bytes_to_float(r.registers[82], r.registers[83])) + \
               ',xP12Value=' + str(convert_bytes_to_float(r.registers[90], r.registers[91])) + \
               ',xP13Value=' + str(convert_bytes_to_float(r.registers[98], r.registers[99])) + \
               ',xP14Value=' + str(convert_bytes_to_float(r.registers[106], r.registers[107])) + \
               ',xP15Value=' + str(convert_bytes_to_float(r.registers[114], r.registers[115])) + \
               ' ' + str(nano) + '\n'
        break
    except:
        time.sleep(2)
        continue




print(line)


#with open('/home/pi/get_gps_python/new/' + str(nano), 'a') as file:
 #   file.write(line)



