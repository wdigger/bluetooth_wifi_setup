import dbus
import gatt
import array
import connctrl
import ConfigParser
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject

class SetupService(gatt.Service):
    TEST_SVC_UUID = '2E2760A0-5D28-4229-8BA5-C626FB012700'

    STATE_INITIALIZED = 0
    STATE_READY_FOR_SETUP = 1
    STATE_CONNECTING = 2
    STATE_CONNECTED = 3

    def __init__(self, index):
        gatt.Service.__init__(self, index, self.TEST_SVC_UUID, True, True)
        self.SSID = None
        self.password = None
        self.state = self.STATE_INITIALIZED
        self.key = None
        self.device = None
        self.state_characteristic = StateCharacteristic(2, self)
        self.add_characteristic(SSIDCharacteristic(0, self))
        self.add_characteristic(PassCharacteristic(1, self))
        self.add_characteristic(self.state_characteristic)
        self.add_characteristic(KeyCharacteristic(3, self))

    def get_WiFiState(self):
        if (connctrl.wifi_connected()):
            return self.STATE_CONNECTED
        else:
            return self.STATE_READY_FOR_SETUP

    def get_SSID(self):
        return self.SSID

    def connect(self):
        print('Connecting...')
        self.set_State(self.STATE_CONNECTING, True)
        if (connctrl.wifi_connect(self.SSID, self.password)):
            self.set_State(self.STATE_CONNECTED, True)
        else:
            self.set_State(self.STATE_READY_FOR_SETUP, True)
        return False

    def set_SSID(self, SSID):
        self.SSID = SSID
        if ((self.state == self.STATE_READY_FOR_SETUP) and self.SSID and self.password):
            GObject.timeout_add(1, self.connect)

    def set_Password(self, password):
        self.password = password
        if ((self.state == self.STATE_READY_FOR_SETUP) and self.SSID and self.password):
            GObject.timeout_add(1, self.connect)

    def get_State(self):
        return str(self.state)

    def set_State(self, state, notify):
        if (state == self.state):
            return
        self.state = int(state)
        if(notify):
            self.state_characteristic.notify()

    def set_Key(self, key, device):
        if((key == self.key) and (self.state == self.STATE_INITIALIZED)):
            self.set_State(self.get_WiFiState(), True)
            self.device = device

    def check_connection(self, device):
        print('CC: self.device = "' + str(self.device) + '" device = "' + str(device) + '"')
        if (self.device == None):
            self.device = device
            return True
        if (device == self.device):
            return True
        self.device = device
        self.set_State(self.STATE_INITIALIZED, False)
        return True


class SSIDCharacteristic(gatt.Characteristic):
    TEST_CHRC_UUID = '2E2760A0-5D28-4229-8BA5-C626FB012701'

    def __init__(self, index, service):
        gatt.Characteristic.__init__(
                self, service.bus, index,
                self.TEST_CHRC_UUID,
                ['read', 'write'],
                service)
        self.add_descriptor(SSIDDescriptor(service.bus, 0, self))

    def ReadValue(self, options):
        print('SSID read:')
        if(not self.service.check_connection(options['device'])):
            print('\tLocked')
            raise NotPermittedException()
        val_str = self.service.get_SSID()
        print('\tValue: : ' + str(val_str))
        return gatt.string_to_value(val_str)

    def WriteValue(self, value, options):
        print('SSID write:')
        if(not self.service.check_connection(options['device'])):
            print('\tLocked')
            raise NotPermittedException()
        val_str = gatt.value_to_string(value)
        print('\tValue: ' + str(val_str))
        self.service.set_SSID(val_str)


class SSIDDescriptor(gatt.Descriptor):
    TEST_DESC_UUID = '2901'

    def __init__(self, bus, index, characteristic):
        gatt.Descriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['read'],
                characteristic)

    def ReadValue(self, options):
        return gatt.string_to_value('SSID')


class PassCharacteristic(gatt.Characteristic):
    TEST_CHRC_UUID = '2E2760A0-5D28-4229-8BA5-C626FB012703'

    def __init__(self, index, service):
        gatt.Characteristic.__init__(
                self, service.bus, index,
                self.TEST_CHRC_UUID,
                ['write', 'writable-auxiliaries'],
                service)
        self.add_descriptor(PassDescriptor(service.bus, 1, self))

    def WriteValue(self, value, options):
        print('Password write:')
        if(not self.service.check_connection(options['device'])):
            print('\tLocked')
            raise NotPermittedException()
        val_str = gatt.value_to_string(value)
        print('\tValue: ' + str(val_str))
        self.service.set_Password(val_str)

class PassDescriptor(gatt.Descriptor):
    TEST_DESC_UUID = '2901'

    def __init__(self, bus, index, characteristic):
        gatt.Descriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['read'],
                characteristic)

    def ReadValue(self, options):
        return gatt.string_to_value('Password')

class StateCharacteristic(gatt.Characteristic):
    TEST_CHRC_UUID = '2E2760A0-5D28-4229-8BA5-C626FB012705'

    def __init__(self, index, service):
        gatt.Characteristic.__init__(
                self, service.bus, index,
                self.TEST_CHRC_UUID,
                ['read', 'write', 'notify'],
                service)
        self.add_descriptor(StateDescriptor(service.bus, 2, self))
        self.add_descriptor(StatePresentation(service.bus, 3, self))

    def ReadValue(self, options):
        self.service.check_connection(options['device'])
        val = self.service.get_State()
        print('State read: ' + str(val))
        return gatt.int_to_value(val)

    def WriteValue(self, value, options):
        print('State write:')
        if(not self.service.check_connection(options['device'])):
            print('\tLocked')
            raise NotPermittedException()
        val_str = gatt.value_to_string(value)
        print('\tValue: ' + str(val_str))
        self.service.set_State(val_str, False)

    def StartNotify(self):
        return

    def StopNotify(self):
        return

    def notify(self):
        val = self.service.get_State()
        print('State notify: ' + str(val))
        self.Notify(gatt.int_to_value(val))


class StateDescriptor(gatt.Descriptor):
    TEST_DESC_UUID = '2901'

    def __init__(self, bus, index, characteristic):
        gatt.Descriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['read'],
                characteristic)

    def ReadValue(self, options):
        return gatt.string_to_value('State')

class StatePresentation(gatt.Descriptor):
    TEST_DESC_UUID = '2904'

    def __init__(self, bus, index, characteristic):
        gatt.Descriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['read'],
                characteristic)

    def ReadValue(self, options):
        return gatt.string_to_value('\x04\x00\xA0\x0F\x01\xA0\x0F')

class KeyCharacteristic(gatt.Characteristic):
    KEY_CHRC_UUID = '2E2760A0-5D28-4229-8BA5-C626FB012707'

    def __init__(self, index, service):
        gatt.Characteristic.__init__(
                self, service.bus, index,
                self.KEY_CHRC_UUID,
                ['write', 'writable-auxiliaries'],
                service)
        self.add_descriptor(KeyDescriptor(service.bus, 4, self))

    def WriteValue(self, value, options):
        val_str = gatt.value_to_string(value)
        print('Key write: ' + str(val_str))
        self.service.set_Key(val_str, options['device'])


class KeyDescriptor(gatt.Descriptor):
    KEY_DESC_UUID = '2901'

    def __init__(self, bus, index, characteristic):
        gatt.Descriptor.__init__(
                self, bus, index,
                self.KEY_DESC_UUID,
                ['read'],
                characteristic)

    def ReadValue(self, options):
        return gatt.string_to_value('Key')


class SetupApplication(gatt.Application):
    def __init__(self):
        gatt.Application.__init__(self)
        service = SetupService(0)
        self.add_service(service)

        version = 1
        print('Version: ' + str(version))

        # Read config and format advertising data
        config = ConfigParser.RawConfigParser()
        config.read('/etc/bwsetup.conf')

        service.key = config.get('device', 'key')
        print('Key: ' + str(service.key))

        dev_id = int(config.get('device', 'id'))
        dev_count = int(config.get('device', 'count'))
        dev_number = int(config.get('device', 'number'))
        print('Device #{} ({}/{})'.format(dev_id, dev_number, dev_count))

        data = []
        data.append(version)
        while dev_id:
            data.append(int(dev_id & 0xFF))
            dev_id >>= 8
        data.reverse()
        data.append((dev_number << 4) + dev_count)
        self.set_manufacturer_data(data)


def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    app = SetupApplication()

    mainloop = GObject.MainLoop()

    connctrl.ble_enable()

    app.Register()

    try:
        mainloop.run()
    except Exception, e:
        print e
    finally:
        app.Unregister()
        connctrl.ble_disable()

if __name__ == '__main__':
    main()
