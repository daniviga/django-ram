# DCC Serial-to-Network Bridge

This directory provides two ways to bridge a serial port to a network port using `ncat` from [nmap](https://nmap.org/ncat/):

1. **Auto-Start with systemd + udev** (Recommended) - Automatically starts/stops when USB device is plugged/unplugged
2. **Container-based** - Manual control using Podman/Docker

> [!IMPORTANT]
> Other variants of `nc` or `ncat` may not work as expected.

## Option 1: Auto-Start with systemd + udev (Recommended)

Automatically start the bridge when USB device `1a86:7523` is connected to `/dev/ttyUSB0` and stop it when removed.

### Quick Install

```bash
./install-udev-rule.sh
```

### Features
- ✅ Auto-start when device connected
- ✅ Auto-stop when device removed
- ✅ User-level service (no root needed)
- ✅ Runs on boot (with lingering enabled)

See [INSTALL.md](INSTALL.md) for detailed documentation.

### Test

```bash
# Run the test script
./test-udev-autostart.sh

# Or manually check
systemctl --user status dcc-usb-connector.service
telnet localhost 2560
```

## Option 2: Container-based (Manual)

### Build and run the container

```bash
$ podman build -t dcc/bridge .
$ podman run -d --group-add keep-groups --device=/dev/ttyACM0:/dev/arduino -p 2560:2560 --name dcc-bridge dcc/bridge
```

### Test

It can be tested with `telnet`:

```bash
$ telnet localhost 2560
```
