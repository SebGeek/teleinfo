#!/usr/bin/python
# -*- coding:utf-8 -*-

'''
import re
import time
import subprocess
from connexionSSH import connexionSSH
from testbench import return_value
from testbench_gigabit import conf_gigabit
'''

'''
toto ="[  4]  0.0- 1.0 sec  19.5 KBytes   160 Kbits/sec   0.012 ms    0/  100 (0%)"
toto2="[  3]  0.0-60.0 sec  1.14 MBytes   160 Kbits/sec   0.006 ms    0/ 6001 (0%)"
print re.findall("\-\s*([0-9]+.[0-9]+)\s*sec",toto)
print re.findall("\-\s*([0-9]+.[0-9]+)\s*sec",toto2)
'''

'''
cmd = "ls -als toto"
timeout_duration = 2
print cmd
timeout = time.time() + timeout_duration
while True:
    pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    stdout, stderr = pipe.communicate()

    if not "cannot access" in stdout:
        print stdout
        break
    if time.time() > timeout:
        print stdout
        print "ERROR: command", cmd, "reaches timeout of", timeout_duration, "s"
        break
    time.sleep(1)
'''

'''
con = connexionSSH()
ed = "192.168.53.31"
con.connect(ed)
wait_for_file = "192.168.53.31.sh"
cmd = "ls -als " + wait_for_file
timeout_duration = 2
print cmd
timeout = time.time() + timeout_duration
while True:
    stdin, stdout, stderr = con.executeCommandOnRemote(cmd)
    stdout_content = stdout.read(); stderr_content = stderr.read()
    if wait_for_file in stdout_content:
        print stdout_content
        break
    if time.time() > timeout:
        print "stdout: ", stdout_content, "stderr:", stderr_content
        print "ERROR: command", cmd, "reaches timeout of ", timeout_duration
        break
    stdin.close(); stderr.close(); stdout.close()
    time.sleep(1)
con.close()
'''

'''
ed = "192.168.100.34"
ed_ip = return_value(conf_gigabit, field_value_to_search=("IP_ecn", ed),
                     field_to_return="IP_admin")
print ed_ip
'''

if __name__ == "__main__":
    '''
    import glob
    import os

    files_to_analyze = ["/home/obens/_sauray/reports/VLAN/capture_test_multicast/**/*.pcap",]

    range_files = []
    for a_file in files_to_analyze:
        all_files = sorted(glob.glob(a_file))
        for b_file in all_files:
            range_files.append(b_file)

    #confirm = raw_input("Will change the content of python scripts, type yes to continue...")
    confirm = "yes"
    if confirm == "yes":
        for file_to_analyze in range_files:
            if os.path.getsize(file_to_analyze) < 230000:
                print file_to_analyze + ": " + str(os.path.getsize(file_to_analyze)) + " B"

    '''
    '''
    import pyshark

    print "PCAP reading"
    # "udp.port == 6000 and ip.dst == 10.20.1.100"
    cap = pyshark.FileCapture("/home/obens/_sauray/test_scripts/examples/capture_2_loss.pcapng", display_filter="udp")
    print "PCAP read"

    print "start of analysis"
    counter_prev = -1
    for packet in cap:
        counter_current = int(packet.data.data[:8], 16)
        if counter_current != counter_prev + 1:
            print "ERROR for packet " + str(packet.number) + " time=" + str(packet.sniff_time) + " timestamp=" + str(packet.sniff_timestamp) + " with iperf counter = " + str(counter_current) + "/" + hex(counter_current) +\
                  ", counter diff is " + str(counter_current - counter_prev)
        counter_prev = counter_current
    print "end of analysis"
    '''


    import matplotlib.pyplot as plt

    plt.plot([1,2,3,4])
    plt.ylabel('some numbers')
    plt.show()


    '''
    import dns.resolver

    host = 'www.freebsd.org'

    answers_IPv4 = dns.resolver.query(host, 'A')
    for rdata in answers_IPv4:
        print 'IPv4:', rdata.address
    '''