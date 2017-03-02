#! /bin/sh

cd bluez

apt-get install autoconf make automake cmake libtool libglib2.0 libdbus-1-dev libudev-dev libical-dev libreadline-dev libtoolize --force

aclocal 
autoheader 
automake --force-missing --add-missing 
autoconf
./configure --prefix=/usr --mandir=/usr/share/man --sysconfdir=/etc --localstatedir=/var --enable-experimental --with-systemdsystemunitdir=/lib/systemd/system --with-systemduserunitdir=/usr/lib/systemd
make

make install

sed -ie 's/ExecStart=//usr//local//libexec//bluetooth//bluetoothd/ExecStart=//usr//local//libexec//bluetooth//bluetoothd --experimental/g' /lib/systemd/system/bluetooth.service
