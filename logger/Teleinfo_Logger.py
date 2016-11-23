#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Read one teleinfo frame and output the frame in CSV format on stdout
"""

import serial
import traceback
import logging.handlers
import sys
import argparse
import datetime
import threading
import time

# Device name
gDeviceName = '/dev/ttyAMA0'

duration = 365 * 24 * 3600 # durée avant d'arrêter le log: 365 days
period   = 30              # période de mesure en secondes
prix_HC  = 0.0638 * 1.2    # prix HC TTC pour 1 kWh (TVA à 20%, voir facture du 3/2/2016)
prix_HP  = 0.1043 * 1.2    # prix HP TTC


# Global variable shared with the thread
last_frame_read = {"HCHC": 0, "HCHP": 0, "PTEC": "xx", "PAPP": 0}


class Teleinfo(threading.Thread):
    """ Fetch teleinformation data from serial link
    """

    def __init__(self, device, logger, list_of_tags_to_read_values):
        """
        @param device : teleinfo modem device path
        """
        self._device = device
        self.logger  = logger
        self.list_of_tags_to_read_values = list_of_tags_to_read_values

        # Open Teleinfo modem
        self.open()

        self.RqTerminate  = False
        self.IsTerminated = False
        threading.Thread.__init__(self)

    def open(self):
        """
        open teleinfo modem device
        """
        self._ser = None
        try:
            self.logger.info("Try to open Teleinfo modem '%s'" % self._device)
            self._ser = serial.Serial(self._device, 1200, bytesize=7, parity='E', stopbits=1)
            self.logger.info("Teleinfo modem successfully opened")
        except:
            self.logger.error("Error opening Teleinfo modem '%s' : %s" % (self._device, traceback.format_exc()))
            self.terminate()

    def close(self):
        self.RqTerminate = True
        while self.IsTerminated != True:
            time.sleep(0.1)

        if self._ser != None and self._ser.isOpen():
            self._ser.close()

    def terminate(self):
        self.close()
        sys.exit(0)

    def read_serial(self):
        """ Fetch one full frame for serial port
        If some part of the frame is corrupted,
        it waits until the next one, so if you have corruption issue,
        this method can take time but it ensures that the frame returned is valid
        @return frame : list of dict {name, value, checksum}
        """
        #Get the begin of the frame, marked by \x02
        self._ser.flushInput()
        self._ser.flushOutput()
        resp = ""

        is_ok = False
        frameCsv = {}
        while not is_ok:
            while '\x02' not in resp:
                resp = self._ser.readline()

            #\x02 is in the last line of a frame, so go until the next one
            #A new frame starts
            resp = self._ser.readline()

            #\x03 is the end of the frame
            while '\x03' not in resp:
                #Don't use strip() here because the checksum can be ' '
                if len(resp.replace('\r', '').replace('\n', '').split()) == 2:
                    #The checksum char is ' '
                    name, value = resp.replace('\r', '').replace('\n', '').split()
                    checksum = ' '
                else:
                    name, value, checksum = resp.replace('\r', '').replace('\n', '').split()
                    #print "name : %s, value : %s, checksum : %s" % (name, value, checksum)
                if self._is_valid(resp, checksum):
                    if str(name) in self.list_of_tags_to_read_values:
                        frameCsv[name] = value
                else:
                    self.logger.error("** FRAME CORRUPTED !")
                    #This frame is corrupted, we need to wait until the next one
                    frameCsv = {}
                    while '\x02' not in resp:
                        resp = self._ser.readline()
                    self.logger.error("* New frame after corrupted")
                resp = self._ser.readline()

            #\x03 has been detected, that's the last line of the frame
            if len(resp.replace('\r', '').replace('\n', '').split()) == 2:
                #print "* End frame"
                #The checksum char is ' '
                resp.replace('\r', '').replace('\n', '').replace('\x02', '').replace('\x03', '').split()
                checksum = ' '
            else:
                name, value, checksum = resp.replace('\r', '').replace('\n', '').replace('\x02', '').replace('\x03', '').split()

            if self._is_valid(resp, checksum):
                # MOTDETAT : Mot d’état (autocontrôle)
                #print "* End frame, is valid : %s" % frame
                is_ok = True
            else:
                self.logger.error("** Last frame invalid")
                resp = self._ser.readline()

        return frameCsv

    @staticmethod
    def _is_valid(frame, checksum):
        """ Check if a frame is valid
        @param frame : the full frame
        @param checksum : the frame checksum
        """
        #print "Check checksum : f = %s, chk = %s" % (frame, checksum)
        datas = ' '.join(frame.split()[0:2])
        my_sum = 0
        for cks in datas:
            my_sum += ord(cks)
        computed_checksum = (my_sum & int("111111", 2)) + 0x20
        #print "computed_checksum = %s" % chr(computed_checksum)
        return chr(computed_checksum) == checksum

    def run(self):
        # Global variable modified by this thread
        global last_frame_read

        while self.RqTerminate == False:
            # Read a frame
            last_frame_read = self.read_serial()

        self.IsTerminated = True


# Override doRollover in order to write a header at the top of every file
class MyTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):

    def __init__(self, logfile, when='h', interval=1):
        super(MyTimedRotatingFileHandler, self).__init__(logfile, when, interval)
        self._header = ""
        self._log = None

    def doRollover(self):
        super(MyTimedRotatingFileHandler, self).doRollover()

        if self._log is not None and self._header != "":
            self._log.info(self._header)

    def setHeader(self, header):
        self._header = header

    def configureHeaderWriter(self, header, log):
        self._header = header
        self._log = log


if __name__ == "__main__":
    '''
    A exécuter avec: ./Teleinfo_Logger.py -o ../log/log.csv

    Pour ne pas fermer le programme en quittant la session SSH, utiliser: screen
    Pour se détacher: ctrl+a puis d
    Pour se rattacher: screen -r

    HP      :  6h30 - 22h30
    HC      : 22h30 -  6h30
    
    ADCO    : Identifiant du compteur
    OPTARIF : Option tarifaire (type d’abonnement)
    ISOUSC  : Intensité souscrite
    HCHC    : Index heures creuses si option = heures creuses (en Wh)
    HCHP    : Index heures pleines si option = heures creuses (en Wh)
    PTEC    : Période tarifaire en cours
    IINST   : Intensité instantanée (en ampères)
    IMAX    : Intensité maximale (en ampères)
    PAPP    : Puissance apparente (en Volt.ampères)
    HHPHC   : Groupe horaire si option = heures creuses ou tempo

    colonne 0: date/heure
    colonne 1: prix (€) = index HC * Prix HC + index HP * Prix HP
    colonne 2: puissance (W)
    colonne 3: HC=0, HP=1
    '''

    ####################################
    # read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True, help="append values in OUTPUT file; e.g. ./log/log.csv")
    args = parser.parse_args()

    ####################################
    # Create status log (for info or errors)
    # store in file and display to console
    log_file = logging.getLogger('teleinfo_status')
    log_file.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh_log_file = logging.FileHandler("status.log")
    fh_log_file.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh_log_file.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add to log
    log_file.addHandler(fh_log_file)
    log_file.addHandler(ch)

    log_file.info("Teleinfo values will append in %s file", args.output)

    ####################################
    # Create CSV log
    # store in file but do not display in console
    line_val = logging.getLogger('teleinfo_values')
    line_val.setLevel(logging.DEBUG)
    # create file handler which logs teleinfo values
    # Files are cut every day at midnight
    fh_csv = MyTimedRotatingFileHandler(args.output, when='midnight')

    fh_csv.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(message)s')
    fh_csv.setFormatter(formatter)

    line_val.propagate = False  # do not send to console stdout
    line_val.addHandler(fh_csv)

    ####################################
    # Start thread to read on serial link
    thread_teleinfo = Teleinfo(gDeviceName, log_file, ("HCHC", "HCHP", "PTEC", "IINST", "PAPP"))
    thread_teleinfo.start()

    ####################################
    # Fill CSV log using last_frame_read coming from the thread
    try:
        starttime = time.time()
        endtime = starttime + duration
        previoustime = starttime
        first_time = True
        index_HC_offset = 0.0
        index_HP_offset = 0.0

        # Header
        header_line = "Date/Heure;Prix (euros TTC);Puissance apparente (V.A);Periode tarifaire (HC=0, HP=1)"
        line_val.info(header_line)
        fh_csv.configureHeaderWriter(header_line, line_val)

        while time.time() <= endtime:
            if time.time() >= (previoustime + period):
                date = datetime.datetime.now()

                index_HC_current = int(last_frame_read["HCHC"])
                index_HP_current = int(last_frame_read["HCHP"])
                if first_time == True:
                    index_HC_offset = index_HC_current
                    index_HP_offset = index_HP_current
                    prix = 0
                    first_time = False
                else:
                    index_HC = index_HC_current - index_HC_offset
                    index_HP = index_HP_current - index_HP_offset
                    prix = (index_HC / 1000. * prix_HC) + (index_HP / 1000. * prix_HP)

                if last_frame_read["PTEC"][0:2] == 'HC':
                    periode_tarifaire = 0
                else:
                    periode_tarifaire = 1

                puissance_apparente = int(last_frame_read["PAPP"])

                line_val.info(str(date) + ";" + str(prix) + ";" + str(puissance_apparente) + ";" + str(periode_tarifaire))

                previoustime += period

            time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        thread_teleinfo.close()
        log_file.info("Keyboard interrupt: end of prog")
