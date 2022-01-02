#!/bin/sh

PTY=0

if [ -c /dev/pts/0 ]; then
    PTY=1
fi

sed -i "s/ttyACM0/pts\/${PTY}/" /opt/dcc/config.ini

qemu-system-avr -machine uno -bios /io/CommandStation-EX-uno-*.elf -serial pty -daemonize
/opt/dcc/net-to-serial.py
