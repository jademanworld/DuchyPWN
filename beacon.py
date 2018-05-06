from scapy.all import Dot11,Dot11Beacon,Dot11Elt,RadioTap,sendp
import sys
import os
import gen_utils as gu
from multiprocessing import Process

class Beacon:
    def __init__(self, iface = "wlan0"):
        self.iface = iface
        self.pid = {}

    def __beacon_send(self, ssid, inter, enc):
        dot11 = Dot11(type=0, subtype=8, addr1='ff:ff:ff:ff:ff:ff', addr2=gu.rand_mac(), addr3=gu.rand_mac())
        beacon = Dot11Beacon(cap='ESS')
        beacon_enc = Dot11Beacon(cap='ESS+privacy')
        essid = Dot11Elt(ID='SSID',info=ssid, len=len(ssid))
        rsn = Dot11Elt(ID='RSNinfo', info=('\x01\x00\x00\x0f\xac\x02\x02\x00\x00\x0f\xac\x04\x00\x0f\xac\x02\x01\x00\x00\x0f\xac\x02\x00\x00'))
        if enc:
            frame = RadioTap()/dot11/beacon_enc/essid/rsn
        else:
            frame = RadioTap()/dot11/beacon/essid
        sendp(frame, iface=self.iface, inter=inter, loop=1)

    def send(self, ssid, inter = 0.2, enc = False):
        proc = Process(target=self.__beacon_send, args=(ssid, inter, enc,))
        proc.start()
        self.pid[ssid] = proc.pid
        return 0

    def list(self):
        if len(self.pid) == 0:
            print "There are no beacons currently in use!"
            return 1
        print "List of beacons: "
        for x in range(len(self.pid)):
            print str(self.pid.items()[x][0]) + " is running under PID: " + str(self.pid.items()[x][1])
        return 0

    def stop(self):
        if len(self.pid) == 0:
            print "There are no beacons currently in use!"
            return 1
        print "Select one you wish to stop (0 = none): "
        for x in range(len(self.pid)):
            print str(x+1), str(self.pid.items()[x][0]), " is running under PID: ", str(self.pid.items()[x][1])
        while 1:
            choice = raw_input("> ")
            try:
                choice = int(choice)
            except:
                print "Enter a number!"
                continue
            if choice > (len(self.pid)+1):
                print "Enter a valid number!"
                continue
            break
        if choice == 0:
            return 0
        else:
            os.kill(self.pid.items()[choice-1][1], 9)
            print "Killed "+str(self.pid.items()[choice-1][0])
            self.pid.pop(self.pid.items()[choice-1][0])
        return 0

    def stop_all(self):
        if len(self.pid) == 0:
            print "There are no beacons currently in use!"
            return 1
        for x in range(len(self.pid)):
            os.kill(self.pid.items()[x][1], 9)
        return 0
