#!/bin/sh

PTY=0

# if container is run with -ti pts/0 is already taken
if [ -c /dev/pts/0 ]; then
    PTY=1
fi

sed -i "s/ttyACM0/pts\/${PTY}/" /opt/dcc/config.ini

qemu-system-avr -machine uno -bios /io/CommandStation-EX*.elf -serial pty -daemonize
/opt/dcc/net-to-serial.py
