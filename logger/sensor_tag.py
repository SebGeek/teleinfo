#!/usr/bin/python
# -*- coding: utf-8 -*-

import pexpect
import time

'''
*******************************
http://processors.wiki.ti.com/index.php/CC2650_SensorTag_User's_Guide
https://e2e.ti.com/support/wireless_connectivity/bluetooth_low_energy/f/538/t/532282
https://developer.ibm.com/recipes/tutorials/ti-sensor-tag-and-raspberry-pi/

sudo hciconfig hci0 up

sudo hcitool lescan
B0:B4:48:ED:D9:80 CC2650 SensorTag

gatttool --device=B0:B4:48:ED:D9:80 --interactive
[B0:B4:48:ED:D9:80][LE]> connect

char-write-cmd 0x0027 01
char-read-hnd 0x0024

char-write-cmd 0x002F 01
char-read-hnd 0x002C

'''

SENSORTAG_BLE_ADDRESS = "B0:B4:48:ED:D9:80"

class SensorTag:
    def __init__(self, bluetooth_adr):
        self.con = pexpect.spawn('gatttool -b ' + bluetooth_adr + ' --interactive')
        self.con.expect('\[LE\]>', timeout=600)

        #print "Preparing to connect. You might need to press the power button..."
        self.con.sendline('connect')
        self.con.expect('Connection successful.*\[LE\]>')

    def char_write_cmd(self, handle, value):
        # The 0%x for value is VERY naughty!  Fix this!
        cmd = 'char-write-cmd 0x%02x 0%x' % (handle, value)
        #print cmd
        self.con.sendline(cmd)
        return

    def char_read_hnd(self, handle):
        self.con.sendline('char-read-hnd 0x%02x' % handle)
        self.con.expect('descriptor: .*? \r')
        after = self.con.after
        return after

    def activate_temp(self, power_on):
        self.char_write_cmd(0x27, power_on)
        time.sleep(0.5)

    def read_temp(self):
        raw_temp_data = self.char_read_hnd(0x24)
        #print "raw_temp=" + raw_temp_data
        raw_temp_bytes = raw_temp_data.split()

        objT = int('0x' + raw_temp_bytes[-3] + raw_temp_bytes[-4], 16)
        objT = objT / 4.0 * 0.03125
        ambT = int('0x' + raw_temp_bytes[-1] + raw_temp_bytes[-2], 16)
        ambT = ambT / 4.0 * 0.03125

        return objT, ambT # object temperature in °C, ambient temperature in °C

    def activate_humidity(self, power_on):
        self.char_write_cmd(0x2F, power_on)
        time.sleep(0.2)

    def read_humidity(self):
        raw_temp_data = self.char_read_hnd(0x2C)
        #print "raw_humidity=" + raw_temp_data
        raw_temp_bytes = raw_temp_data.split()

        rawT = int('0x' + raw_temp_bytes[-3] + raw_temp_bytes[-4], 16)
        rawH = int('0x' + raw_temp_bytes[-1] + raw_temp_bytes[-2], 16)
        t  = (rawT / 65536.0) * 165.0 - 40.0
        rh = (rawH / 65536.0) * 100.0

        return t, rh # temperature in °C, relative humidity in %

    def activate_barometer(self, power_on):
        self.char_write_cmd(0x37, power_on)
        time.sleep(0.2)

    def read_barometer(self):
        raw_temp_data = self.char_read_hnd(0x34)
        #print "raw_humidity=" + raw_temp_data
        raw_temp_bytes = raw_temp_data.split()

        rawT = int('0x' + raw_temp_bytes[-4] + raw_temp_bytes[-5] + raw_temp_bytes[-6], 16)
        rawP = int('0x' + raw_temp_bytes[-1] + raw_temp_bytes[-2] + raw_temp_bytes[-3], 16)
        t = rawT / 100.0
        p = rawP / 100.0

        return t, p  # temperature in °C, pressure in hPa


    def read_battery_level(self):
        raw_batt_level = self.char_read_hnd(0x1E)
        #print "raw_batt_level=" + raw_batt_level
        raw_batt_bytes = raw_batt_level.split()

        batt_level = int('0x' + raw_batt_bytes[-1], 16)

        return batt_level  # battery level in %

if __name__ == "__main__":
    obj_sensor = SensorTag(SENSORTAG_BLE_ADDRESS)

    print "** Battery level"
    print "battery " + str(obj_sensor.read_battery_level())

    print "** IR temperature sensor"
    obj_sensor.activate_temp(1)
    print "temp " + str(obj_sensor.read_temp()[1])
    obj_sensor.activate_temp(0)

    print "** Hygrometry/temperature sensor"
    obj_sensor.activate_humidity(1)
    t, rh = obj_sensor.read_humidity()
    print "temp " + str(t)
    print "humidity " + str(rh)
    obj_sensor.activate_humidity(0)

    print "** Barometer/temperature sensor"
    obj_sensor.activate_barometer(1)
    t, p = obj_sensor.read_barometer()
    print "temp " + str(t)
    print "pressure " + str(p)
    obj_sensor.activate_barometer(0)
