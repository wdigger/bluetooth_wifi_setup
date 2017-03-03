from wifi import Cell, Scheme


def wifi_list():
    return Cell.all('wlan0')


def main():
    wl = wifi_list()
    print(repr(len(wl)) + ' : ' + repr(wl))


if __name__ == '__main__':
    main()
