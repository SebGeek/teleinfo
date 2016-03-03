#!/usr/bin/python
# -*- coding: utf-8 -*-
 
""" Read one teleinfo frame and output the frame in CSV format on stdout
"""
 
import serial
import time
import traceback
import logging
import sys
from optparse import OptionParser
import os
import datetime


# Default log level
gLogLevel = logging.ERROR
 
# Device name
gDeviceName = '/dev/ttyAMA0'
# Default output is stdout
gOutput = sys.__stdout__
 
# ----------------------------------------------------------------------------
# LOGGING
# ----------------------------------------------------------------------------
class MyLogger:
    """ Our own logger """
 
    def __init__(self):
        self._logger = logging.getLogger('teleinfo')
        hdlr = logging.FileHandler('debug.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self._logger.addHandler(hdlr)
        self._logger.setLevel(gLogLevel)
 
    #def __del__(self):
        #if self._logger != None:
            #logging.shutdown()
 
    def debug(self, text):
        try:
            self._logger.debug(text)
        except NameError:
            pass
 
    def info(self, text):
        try:
            self._logger.info(text)
        except NameError:
            pass
 
    def error(self, text):
        try:
            self._logger.error(text)
        except NameError:
            pass
 
 
# ----------------------------------------------------------------------------
# Exception
# ----------------------------------------------------------------------------
class TeleinfoException(Exception):
    """
    Teleinfo exception
    """
 
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value
 
    def __str__(self):
        return repr(self.value)
 
 
# ----------------------------------------------------------------------------
# Teleinfo core
# ----------------------------------------------------------------------------
class Teleinfo:
    """ Fetch teleinformation datas and call user callback
    each time all data are collected
    """
 
    def __init__(self, device):
        """ @param device : teleinfo modem device path
        @param log : log instance
        @param callback : method to call each time all data are collected
        The datas will be passed using a dictionnary
        """
        self._log = MyLogger()
        self._device = device
        self._ser = None

        # Open Teleinfo modem
        try:
            self.open()
        except TeleinfoException as err:
            self._log.error(err.value)
            print err.value
            self.terminate()
            return

        #self._stop = Event()
 
    def open(self):
        """ open teleinfo modem device
        """
        try:
            self._log.info("Try to open Teleinfo modem '%s'" % self._device)
            self._ser = serial.Serial(self._device, 1200, bytesize=7, parity = 'E', stopbits=1)
            self._log.info("Teleinfo modem successfully opened")
        except:
            error = "Error opening Teleinfo modem '%s' : %s" % (self._device, traceback.format_exc())
            raise TeleinfoException(error)

    def close(self):
        """ close telinfo modem
        """
        #self._stop.set()
        if self._ser != None and self._ser.isOpen():
            self._ser.close()
 
    def terminate(self):
        self.close()
        #sys.close(gOutput)
        sys.exit(0)
 
    def read_serial(self):
        """ Fetch one full frame for serial port
        If some part of the frame is corrupted,
        it waits until the next one, so if you have corruption issue,
        this method can take time but it ensures that the frame returned is valid
        @return frame : list of dict {name, value, checksum}
        """
        #Get the begin of the frame, markde by \x02
        resp = self._ser.readline()
        is_ok = False
        frame = []
        frameCsv = []
        while not is_ok:
            try:
                while '\x02' not in resp:
                    resp = self._ser.readline()
                #\x02 is in the last line of a frame, so go until the next one
                #print "* Begin frame"
                frameCsv.append(str(datetime.datetime.now()))
                resp = self._ser.readline()
                #A new frame starts
                #\x03 is the end of the frame
                while '\x03' not in resp:
                    #Don't use strip() here because the checksum can be ' '
                    if len(resp.replace('\r','').replace('\n','').split()) == 2:
                        #The checksum char is ' '
                        name, value = resp.replace('\r','').replace('\n','').split()
                        checksum = ' '
                    else:
                        name, value, checksum = resp.replace('\r','').replace('\n','').split()
                        #print "name : %s, value : %s, checksum : %s" % (name, value, checksum)
                    if self._is_valid(resp, checksum):
                        frame.append({"name" : name, "value" : value, "checksum" : checksum})
                        #frameCsv.append(value)
                        if str(name) in ("HCHC", "HCHP", "PTEC", "IINST", "PAPP"):
                            frameCsv.append(value)
                    else:
                        self._log.error("** FRAME CORRUPTED !")
                        #This frame is corrupted, we need to wait until the next one
                        frame = []
                        frameCsv = []
                        while '\x02' not in resp:
                            resp = self._ser.readline()
                        self._log.error("* New frame after corrupted")
                    resp = self._ser.readline()

                #\x03 has been detected, that's the last line of the frame
                if len(resp.replace('\r','').replace('\n','').split()) == 2:
                    #print "* End frame"
                    #The checksum char is ' '
                    name, value = resp.replace('\r','').replace('\n','').replace('\x02','').replace('\x03','').split()
                    checksum = ' '
                else:
                    name, value, checksum = resp.replace('\r','').replace('\n','').replace('\x02','').replace('\x03','').split()

                if self._is_valid(resp, checksum):
                    frame.append({"name" : name, "value" : value, "checksum" : checksum})
                    # MOTDETAT : Mot d’état (autocontrôle)
                    #frameCsv.append(str(name) + ":"+  str(value))
                    #print "* End frame, is valid : %s" % frame
                    is_ok = True
                else:
                    self._log.error("** Last frame invalid")
                    resp = self._ser.readline()

            except ValueError:
                #Badly formatted frame
                #This frame is corrupted, we need to wait until the next one
                frame = []
                frameCsv = []
                while '\x02' not in resp:
                    resp = self._ser.readline()
        return frameCsv
 
    def _is_valid(self, frame, checksum):
        """ Check if a frame is valid
        @param frame : the full frame
        @param checksum : the frame checksum
        """
        #print "Check checksum : f = %s, chk = %s" % (frame, checksum)
        datas = ' '.join(frame.split()[0:2])
        my_sum = 0
        for cks in datas:
            my_sum = my_sum + ord(cks)
        computed_checksum = ( my_sum & int("111111", 2) ) + 0x20
        #print "computed_checksum = %s" % chr(computed_checksum)
        return chr(computed_checksum) == checksum
 
    def read(self):
        """ Main function
        """

        # Read a frame
        frameCsv = self.read_serial()

        # output CSV
        frameMod = str(frameCsv).replace('\'','').replace(' ','').replace(',',';').strip('[]')
        return(frameMod)


# ----------------------------------------------------------------------------
# Teleinfo core
# ----------------------------------------------------------------------------
class LogRotate:
    """
    """

    def __init__(self, filename, max_size, header):
        self.max_size = max_size # in Bytes
        self.header = header + "\n"
        add_header = not(os.path.isfile(filename))
        try:
            self.logfile = open(filename, 'a')
        except:
            error = "Can not open file for append: %s" % filename
            raise TeleinfoException(error)
        if add_header:
            self.logfile.writelines(self.header)

    def push(self, line):
        self.logfile.writelines(line)
        if self.logfile.tell() >= self.max_size:
            # File is too big, so rename it and create a new one
            old_filename = self.logfile.name
            self.logfile.close()
            new_filename = old_filename + ".1"
            if os.path.isfile(new_filename) == True:
                os.remove(new_filename)
            os.rename(old_filename, new_filename)
            self.logfile = open(old_filename, 'a')
            self.logfile.writelines(self.header)

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------
if __name__ == "__main__":
    '''
ADCO : Identifiant du compteur
OPTARIF : Option tarifaire (type d’abonnement)
ISOUSC : Intensité souscrite
HCHC : Index heures creuses si option = heures creuses (en Wh)
HCHP : Index heures pleines si option = heures creuses (en Wh)
PTEC : Période tarifaire en cours
IINST : Intensité instantanée (en ampères)
IMAX : Intensité maximale (en ampères)
PAPP : Puissance apparente (en Volt.ampères)
HHPHC : Groupe horaire si option = heures creuses ou tempo
    '''
	
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-o", "--output", dest="filename", help="append result in FILENAME")
    (options, args) = parser.parse_args()
    print "opt: %s, arglen: %s" % (options, len(args))
    if options.filename:
        ObjLogRotate = LogRotate(options.filename, 10*1024*1024,
									"date;" +
									"HCHC: Index heures creuses en Wh;" +
									"HCHP: Index heures pleines en Wh;" +
									"PTEC: Periode tarifaire;" + 
									"IINST: Intensite instantanee en A;" +
									"PAPP: Puissance apparente en V.A")
 
    teleinfo = Teleinfo(gDeviceName)
    while(True):
        line_read = teleinfo.read()
        #print line_read
        ObjLogRotate.push(line_read + "\n")

    '''HP 6h30-22h30  '''

    print "END OF PROG"
