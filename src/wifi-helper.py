from wireless import Wireless

class WiFi(object):
    def __init__(self, ifname):
        self.ifname = ifname
        self.wifi = Wireless()
        self.wifi.interface(ifname)

    def is_enabled(self):
        return self.wifi.power()

    def enable(self):
        self.wifi.power(True)

    def disable(self):
        self.wifi.power(False)

    def is_connected(self):
        return (self.wifi.current() != None)

    def connect(self, ssid, password):
        self.wifi.connect(ssid, password)

    def disconnect(self):
        return

    def get_ssid(self):
        return self.wifi.current()

def main():
    wifi = WiFi('wlan0')
    wifi.enable()
    print('Enabled: ' + str(wifi.is_enabled()))

    print('Connected: ' + str(wifi.is_connected()))
    if (wifi.is_connected()):
        print('\tSSID: ' + str(wifi.get_ssid()))
    else:
        wifi.connect('SJ3', 'ZwuonJ%ph8')

if __name__ == '__main__':
    main()
