import errno
import sys
import types

import pythonwifi.flags
from pythonwifi.iwlibs import Wireless, Iwrange, getNICnames, getWNICnames

class WiFi(object):
    def __init__(self, ifname):
        self.ifname = ifname
        self.wifi = Wireless(self.ifname)

    def is_enabled(self):
        try:
            results = self.wifi.scan()
        except IOError, (error_number, error_string):
            return False
        else:
            return True

    def is_connected(self):
        if self.ifname not in getWNICnames():
           return False
        else:
           return True

    def get_ssid(self):
        return self.wifi.getEssid()

def main():
    wifi = WiFi('wlan0')
    print('Enabled: ' + str(wifi.is_enabled()))
    print('Connected: ' + str(wifi.is_connected()))
    if (wifi.is_connected()):
        print('\tSSID: ' + str(wifi.get_ssid()))

if __name__ == '__main__':
    main()
