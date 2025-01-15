#!/bin/sh

PTY=0

# if container is run with -ti pts/0 is already taken
if [ -c /dev/pts/0 ]; then
    PTY=1
fi

qemu-system-avr -machine uno -bios /io/CommandStation-EX*.elf -serial pty -daemonize
ncat -n -k -l 2560 -o /dev/stderr </dev/pts/${PTY} >/dev/pts/${PTY}
