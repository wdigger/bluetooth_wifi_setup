#! /bin/sh

#set -x

cd bluez

sudo apt-get -y install autoconf make automake cmake libtool libglib2.0-dev libdbus-1-dev libudev-dev libical-dev libreadline-dev

./bootstrap
./configure --prefix=/usr --mandir=/usr/share/man --sysconfdir=/etc --localstatedir=/var --enable-experimental --with-systemdsystemunitdir=/lib/systemd/system --with-systemduserunitdir=/usr/lib/systemd
make

sudo make install

oldServiceRunSting='ExecStart=/usr/libexec/bluetooth/bluetoothd'
newServiceRunSting='ExecStart=/usr/libexec/bluetooth/bluetoothd --experimental'
sudo sed -i "s~$oldServiceRunSting~$newServiceRunSting~" /lib/systemd/system/bluetooth.service
