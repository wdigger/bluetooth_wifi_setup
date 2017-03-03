import dbus
import gatt
import array
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject


class TestService(gatt.Service):
    """
    Dummy test service that provides characteristics and descriptors that
    exercise various API functionality.

    """
    TEST_SVC_UUID = '2E2760A0-5D28-4229-8BA5-C626FB012700'

    def __init__(self, bus, index):
        gatt.Service.__init__(self, bus, index, self.TEST_SVC_UUID, True)
        self.add_characteristic(TestCharacteristic(bus, 0, self))
        self.add_characteristic(TestEncryptCharacteristic(bus, 1, self))
        self.add_characteristic(TestSecureCharacteristic(bus, 2, self))

class TestCharacteristic(gatt.Characteristic):
    """
    Dummy test characteristic. Allows writing arbitrary bytes to its value, and
    contains "extended properties", as well as a test descriptor.

    """
    TEST_CHRC_UUID = '2E2760A0-5D28-4229-8BA5-C626FB012701'

    def __init__(self, bus, index, service):
        gatt.Characteristic.__init__(
                self, bus, index,
                self.TEST_CHRC_UUID,
                ['read', 'write', 'writable-auxiliaries'],
                service)
        self.value = []
        self.add_descriptor(TestDescriptor(bus, 0, self))
        self.add_descriptor(
                CharacteristicUserDescriptionDescriptor(bus, 1, self))

    def ReadValue(self, options):
        print('TestCharacteristic Read: ' + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print('TestCharacteristic Write: ' + repr(value))
        self.value = value


class TestDescriptor(gatt.Descriptor):
    """
    Dummy test descriptor. Returns a static value.

    """
    TEST_DESC_UUID = '2E2760A0-5D28-4229-8BA5-C626FB012702'

    def __init__(self, bus, index, characteristic):
        gatt.Descriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['read', 'write'],
                characteristic)

    def ReadValue(self, options):
        return [
                dbus.Byte('T'), dbus.Byte('e'), dbus.Byte('s'), dbus.Byte('t')
        ]


class CharacteristicUserDescriptionDescriptor(gatt.Descriptor):
    """
    Writable CUD descriptor.

    """
    CUD_UUID = '2901'

    def __init__(self, bus, index, characteristic):
        self.writable = 'writable-auxiliaries' in characteristic.flags
        self.value = array.array('B', b'This is a characteristic for testing')
        self.value = self.value.tolist()
        gatt.Descriptor.__init__(
                self, bus, index,
                self.CUD_UUID,
                ['read', 'write'],
                characteristic)

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        if not self.writable:
            raise NotPermittedException()
        self.value = value

class TestEncryptCharacteristic(gatt.Characteristic):
    """
    Dummy test characteristic requiring encryption.

    """
    TEST_CHRC_UUID = '2E2760A0-5D28-4229-8BA5-C626FB012703'

    def __init__(self, bus, index, service):
        gatt.Characteristic.__init__(
                self, bus, index,
                self.TEST_CHRC_UUID,
                ['encrypt-read', 'encrypt-write'],
                service)
        self.value = []
        self.add_descriptor(TestEncryptDescriptor(bus, 2, self))
        self.add_descriptor(
                CharacteristicUserDescriptionDescriptor(bus, 3, self))

    def ReadValue(self, options):
        print('TestEncryptCharacteristic Read: ' + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print('TestEncryptCharacteristic Write: ' + repr(value))
        self.value = value

class TestEncryptDescriptor(gatt.Descriptor):
    """
    Dummy test descriptor requiring encryption. Returns a static value.

    """
    TEST_DESC_UUID = '2E2760A0-5D28-4229-8BA5-C626FB012704'

    def __init__(self, bus, index, characteristic):
        gatt.Descriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['encrypt-read', 'encrypt-write'],
                characteristic)

    def ReadValue(self, options):
        return [
                dbus.Byte('T'), dbus.Byte('e'), dbus.Byte('s'), dbus.Byte('t')
        ]


class TestSecureCharacteristic(gatt.Characteristic):
    """
    Dummy test characteristic requiring secure connection.

    """
    TEST_CHRC_UUID = '2E2760A0-5D28-4229-8BA5-C626FB012705'

    def __init__(self, bus, index, service):
        gatt.Characteristic.__init__(
                self, bus, index,
                self.TEST_CHRC_UUID,
                ['secure-read', 'secure-write'],
                service)
        self.value = []
        self.add_descriptor(TestSecureDescriptor(bus, 2, self))
        self.add_descriptor(
                CharacteristicUserDescriptionDescriptor(bus, 3, self))

    def ReadValue(self, options):
        print('TestSecureCharacteristic Read: ' + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print('TestSecureCharacteristic Write: ' + repr(value))
        self.value = value


class TestSecureDescriptor(gatt.Descriptor):
    """
    Dummy test descriptor requiring secure connection. Returns a static value.

    """
    TEST_DESC_UUID = '2E2760A0-5D28-4229-8BA5-C626FB012706'

    def __init__(self, bus, index, characteristic):
        gatt.Descriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['secure-read', 'secure-write'],
                characteristic)

    def ReadValue(self, options):
        return [
                dbus.Byte('T'), dbus.Byte('e'), dbus.Byte('s'), dbus.Byte('t')
        ]


class TestAdvertisement(gatt.Advertisement):
    def __init__(self, bus, index):
        gatt.Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid('2E2760A0-5D28-4229-8BA5-C626FB012700')
        self.include_tx_power = True


class TestApplication(gatt.Application):
    def __init__(self, bus):
        gatt.Application.__init__(self, bus)
        self.add_service(TestService(bus, 0))


def register_app_cb():
    print('GATT application registered')
    bus = dbus.SystemBus()
    ad = TestAdvertisement(bus, 0)
    gatt.register_advertisement(ad, register_ad_cb, register_ad_error_cb)


def register_app_error_cb(error):
    print('Failed to register application: ' + str(error))
    mainloop.quit()


def register_ad_cb():
    print 'Advertisement registered'


def register_ad_error_cb(error):
    print 'Failed to register advertisement: ' + str(error)
    mainloop.quit()


def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    app = TestApplication(bus)

    mainloop = GObject.MainLoop()

    gatt.register_application(app, register_app_cb, register_app_error_cb)

    try:
        mainloop.run()
    except Exception, e:
        print e
    finally:
        gatt.unregister_application(app)

if __name__ == '__main__':
    main()
