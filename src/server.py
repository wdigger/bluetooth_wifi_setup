import dbus
import gatt
import array
import wifi
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject


class SetupService(gatt.Service):
    TEST_SVC_UUID = '2E2760A0-5D28-4229-8BA5-C626FB012700'

    STATE_INITIALIZED = 0
    STATE_REDY_FOR_SETUP = 1
    STATE_CONNECTED = 2
    STATE_CONNECTING = 3

    def __init__(self, index):
        gatt.Service.__init__(self, index, self.TEST_SVC_UUID, True, True)
        self.SSID = ''
        self.password = ''
        self.state = self.STATE_INITIALIZED
        self.key = '123'
        self.device = ''
        self.state_characteristic = StateCharacteristic(2, self)
        self.add_characteristic(SSIDCharacteristic(0, self))
        self.add_characteristic(PassCharacteristic(1, self))
        self.add_characteristic(self.state_characteristic)
        self.add_characteristic(KeyCharacteristic(3, self))

    def get_WiFiState(self):
        return self.STATE_REDY_FOR_SETUP

    def get_SSID(self):
        return self.SSID

    def set_SSID(self, SSID):
        self.SSID = SSID

    def set_Password(self, password):
        self.password = password

    def get_State(self):
        return str(self.state)

    def set_State(self, state, notify):
        self.state = int(state)
        if(notify):
            self.state_characteristic.notify()

    def set_Key(self, key, device):
        if((key == self.key) and (self.state == self.STATE_INITIALIZED)):
            self.set_State(self.get_WiFiState(), True)
            self.device = device

    def check_connection(self, device):
        if (device == self.device):
            return True
        self.device = ''
        self.set_State(self.STATE_INITIALIZED, True)
        return False


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
        if(not self.service.check_connection(options['device'])):
            raise NotPermittedException()
        val_str = self.service.get_SSID()
        print('SSID read: ' + str(val_str))
        return gatt.string_to_value(val_str)

    def WriteValue(self, value, options):
        if(not self.service.check_connection(options['device'])):
            raise NotPermittedException()
        val_str = gatt.value_to_string(value)
        print('SSID write: ' + str(val_str))
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
        if(not self.service.check_connection(options['device'])):
            raise NotPermittedException()
        val_str = gatt.value_to_string(value)
        print('Password write: ' + str(val_str))
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

    def ReadValue(self, options):
        self.service.check_connection(options['device'])
        val_str = self.service.get_State()
        print('State read: ' + str(val_str))
        return gatt.string_to_value(val_str)

    def WriteValue(self, value, options):
        if(not self.service.check_connection(options['device'])):
            raise NotPermittedException()
        val_str = gatt.value_to_string(value)
        print('State write: ' + str(val_str))
        self.service.set_State(val_str, False)

    def StartNotify(self):
        return

    def StopNotify(self):
        return

    def notify(self):
        val_str = self.service.get_State()
        print('State notify: ' + str(val_str))
        self.Notify(gatt.string_to_value(val_str))


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


class KeyCharacteristic(gatt.Characteristic):
    TEST_CHRC_UUID = '2E2760A0-5D28-4229-8BA5-C626FB012707'

    def __init__(self, index, service):
        gatt.Characteristic.__init__(
                self, service.bus, index,
                self.TEST_CHRC_UUID,
                ['write', 'writable-auxiliaries'],
                service)
        self.add_descriptor(KeyDescriptor(service.bus, 2, self))

    def WriteValue(self, value, options):
        val_str = gatt.value_to_string(value)
        print('Key write: ' + str(val_str))
        self.service.set_Key(val_str, options['device'])


class KeyDescriptor(gatt.Descriptor):
    TEST_DESC_UUID = '2901'

    def __init__(self, bus, index, characteristic):
        gatt.Descriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['read'],
                characteristic)

    def ReadValue(self, options):
        return gatt.string_to_value('Key')


class SetupApplication(gatt.Application):
    def __init__(self):
        gatt.Application.__init__(self)
        self.add_service(SetupService(0))


def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    app = SetupApplication()

    mainloop = GObject.MainLoop()

    app.Register()

    try:
        mainloop.run()
    except Exception, e:
        print e
    finally:
        app.Unregister()

if __name__ == '__main__':
    main()
