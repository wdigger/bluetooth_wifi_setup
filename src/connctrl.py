import pyconnman

CONNCTRL_TECH_PATH_BLUETOOTH = '/net/connman/technology/bluetooth'
CONNCTRL_TECH_PATH_WIFI = '/net/connman/technology/wifi'

def tech_enabled(path):
    tech = pyconnman.ConnTechnology(path)
    return tech.get_property('Powered')

def tech_enable(path):
    try:
        if (tech_enabled(path)):
            return True
        tech = pyconnman.ConnTechnology(path)
        tech.set_property('Powered', True)
        return True
    except Exception, e:
        print e
        return False

def tech_disable(path):
    try:
        if (not tech_enabled(path)):
            return True
        tech = pyconnman.ConnTechnology(path)
        tech.set_property('Powered', False)
        return True
    except Exception, e:
        print e
        return False

def ble_enable():
    return tech_enable(CONNCTRL_TECH_PATH_BLUETOOTH)

def ble_disable():
    return tech_disable(CONNCTRL_TECH_PATH_BLUETOOTH)

def wifi_enable():
    return tech_enable(CONNCTRL_TECH_PATH_WIFI)

def wifi_disable():
    return tech_disable(CONNCTRL_TECH_PATH_WIFI)

def wifi_enabled():
    return tech_enabled(CONNCTRL_TECH_PATH_WIFI)

def wifi_connected():
    try:
        if (not wifi_enabled()):
            return False
        tech = pyconnman.ConnTechnology(CONNCTRL_TECH_PATH_WIFI)
        return tech.get_property('Connected')
    except Exception, e:
        print e
        return False

def wifi_service_path(ssid):
    try:
        tech = pyconnman.ConnTechnology(CONNCTRL_TECH_PATH_WIFI)
        tech.scan()
        services = pyconnman.ConnManager().get_services()
        for i in services:
            (path, params) = i
            if (params['Type'] == 'wifi'):
                if (params['Name'] == ssid):
                    return path
        return None
    except Exception, e:
        print e
        return None

def wifi_connect(ssid, password):
    try:
        wifi_enable()
        path = wifi_service_path(ssid)
        if (path is None):
            return False
        print path + ' [' + ssid + ']'
        agent_path = '/bwsetup/agent'
        agent = pyconnman.SimpleWifiAgent(agent_path)
        agent.set_service_params(path, None, ssid, None, None, None, password, None)
        pyconnman.ConnManager().register_agent(agent_path)
        try:
            service = pyconnman.ConnService(path)
            service.set_property('autoconnect','yes')
            service.set_property('ipv4','dhcp')
            service.connect()
        except Exception, e:
            print e
        pyconnman.ConnManager().unregister_agent(agent_path)
        return True
    except Exception, e:
        print e
    return False
