# DCC USB-to-Network Bridge Auto-Start Installation

This directory contains configuration files to automatically start the `dcc-usb-connector.service` when a specific USB device (CH340 USB-to-serial adapter, ID `1a86:7523`) is connected to `/dev/ttyUSB0`.

## Overview

The setup uses:
- **Udev rule** (`99-dcc-usb-connector.rules`) - Detects USB device connection/disconnection
- **Systemd user service** (`dcc-usb-connector.service`) - Bridges serial port to network port 2560
- **Installation script** (`install-udev-rule.sh`) - Automated installation helper

When the USB device is plugged in, the service automatically starts. When unplugged, it stops.

## Prerequisites

1. **Operating System**: Linux with systemd and udev
2. **Required packages**:
   ```bash
   sudo dnf install nmap-ncat systemd udev
   ```
3. **User permissions**: Your user should be in the `dialout` group:
   ```bash
   sudo usermod -a -G dialout $USER
   # Log out and log back in for changes to take effect
   ```

## Quick Installation

Run the installation script:

```bash
./install-udev-rule.sh
```

This script will:
- Install the udev rule (requires sudo)
- Install the systemd user service to `~/.config/systemd/user/`
- Enable systemd lingering for your user
- Check for required tools and permissions
- Provide testing instructions

## Manual Installation

If you prefer to install manually:

### 1. Install the udev rule

```bash
sudo cp 99-dcc-usb-connector.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=tty
```

### 2. Install the systemd service

```bash
mkdir -p ~/.config/systemd/user/
cp dcc-usb-connector.service ~/.config/systemd/user/
systemctl --user daemon-reload
```

### 3. Enable lingering (optional but recommended)

This allows your user services to run even when you're not logged in:

```bash
sudo loginctl enable-linger $USER
```

## Verification

### Test the udev rule

```bash
# Monitor udev events (plug/unplug device while this runs)
udevadm monitor --property --subsystem-match=tty

# Test udev rule (when device is connected)
udevadm test /sys/class/tty/ttyUSB0
```

### Check service status

```bash
# Check if service is running
systemctl --user status dcc-usb-connector.service

# View service logs
journalctl --user -u dcc-usb-connector.service -f
```

### Test the network bridge

```bash
# Connect to the bridge
telnet localhost 2560

# Or using netcat
nc localhost 2560
```

## Usage

### Automatic Operation

Once installed, the service will:
- **Start automatically** when USB device `1a86:7523` is connected to `/dev/ttyUSB0`
- **Stop automatically** when the device is disconnected
- Bridge serial communication to network port `2560`

### Manual Control

You can still manually control the service:

```bash
# Start the service
systemctl --user start dcc-usb-connector.service

# Stop the service
systemctl --user stop dcc-usb-connector.service

# Check status
systemctl --user status dcc-usb-connector.service

# View logs
journalctl --user -u dcc-usb-connector.service
```

## How It Works

### Component Interaction

```
USB Device Connected (1a86:7523 on /dev/ttyUSB0)
         ↓
    Udev Rule Triggered
         ↓
    Systemd User Service Started
         ↓
    stty configures serial port (115200 baud)
         ↓
    ncat bridges /dev/ttyUSB0 ↔ TCP port 2560
         ↓
    Client apps connect to localhost:2560
```

### Udev Rule Details

The udev rule (`99-dcc-usb-connector.rules`) matches:
- **Subsystem**: `tty` (TTY/serial devices)
- **Vendor ID**: `1a86` (CH340 manufacturer)
- **Product ID**: `7523` (CH340 serial adapter)
- **Kernel device**: `ttyUSB0` (specific port)

When matched, it sets `ENV{SYSTEMD_USER_WANTS}="dcc-usb-connector.service"`, telling systemd to start the service.

### Service Configuration

The service (`dcc-usb-connector.service`):
1. Runs `stty -F /dev/ttyUSB0 -echo 115200` to configure the serial port
2. Executes `ncat -n -k -l 2560 </dev/ttyUSB0 >/dev/ttyUSB0` to bridge serial ↔ network
3. Uses `KillMode=mixed` for proper process cleanup
4. Terminates within 5 seconds when stopped

## Troubleshooting

### Service doesn't start automatically

1. **Check udev rule is loaded**:
   ```bash
   udevadm test /sys/class/tty/ttyUSB0 | grep SYSTEMD_USER_WANTS
   ```
   Should show: `ENV{SYSTEMD_USER_WANTS}='dcc-usb-connector.service'`

2. **Check device is recognized**:
   ```bash
   lsusb | grep 1a86:7523
   ls -l /dev/ttyUSB0
   ```

3. **Verify systemd user instance is running**:
   ```bash
   systemctl --user status
   loginctl show-user $USER | grep Linger
   ```

### Permission denied on /dev/ttyUSB0

Add your user to the `dialout` group:
```bash
sudo usermod -a -G dialout $USER
# Log out and log back in
groups  # Verify 'dialout' appears
```

### Device appears as /dev/ttyUSB1 instead of /dev/ttyUSB0

The udev rule specifically matches `ttyUSB0`. To make it flexible:

Edit `99-dcc-usb-connector.rules` and change:
```
KERNEL=="ttyUSB0"
```
to:
```
KERNEL=="ttyUSB[0-9]*"
```

Then reload:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=tty
```

### Service starts but ncat fails

1. **Check ncat is installed**:
   ```bash
   which ncat
   ncat --version
   ```

2. **Verify serial port works**:
   ```bash
   stty -F /dev/ttyUSB0
   cat /dev/ttyUSB0  # Should not error
   ```

3. **Check port 2560 is available**:
   ```bash
   netstat -tuln | grep 2560
   # Should be empty if nothing is listening
   ```

### View detailed logs

```bash
# Follow service logs in real-time
journalctl --user -u dcc-usb-connector.service -f

# View all logs for the service
journalctl --user -u dcc-usb-connector.service

# View with timestamps
journalctl --user -u dcc-usb-connector.service -o short-iso
```

## Uninstallation

To remove the auto-start feature:

```bash
# Remove udev rule
sudo rm /etc/udev/rules.d/99-dcc-usb-connector.rules
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=tty

# Remove systemd service
systemctl --user stop dcc-usb-connector.service
rm ~/.config/systemd/user/dcc-usb-connector.service
systemctl --user daemon-reload

# (Optional) Disable lingering
sudo loginctl disable-linger $USER
```

## Advanced Configuration

### Customize for different USB device

Edit `99-dcc-usb-connector.rules` and change:
- `ATTRS{idVendor}=="1a86"` - USB vendor ID
- `ATTRS{idProduct}=="7523"` - USB product ID

Find your device IDs with:
```bash
lsusb
# Output: Bus 001 Device 003: ID 1a86:7523 QinHeng Electronics ...
#                                   ^^^^:^^^^
#                                   VID   PID
```

### Change network port

Edit `dcc-usb-connector.service` and change:
```
ExecStart=/usr/bin/bash -c "/usr/bin/ncat -n -k -l 2560 ...
```
Replace `2560` with your desired port number.

### Enable auto-restart on failure

Edit `dcc-usb-connector.service` and add under `[Service]`:
```
Restart=on-failure
RestartSec=5
```

Then reload:
```bash
systemctl --user daemon-reload
```

## Testing Without Physical Device

For development/testing without the actual USB device:

```bash
# Create a virtual serial port pair
socat -d -d pty,raw,echo=0 pty,raw,echo=0

# This creates two linked devices, e.g., /dev/pts/3 and /dev/pts/4
# Update the service to use one of these instead of /dev/ttyUSB0
```

## References

- [systemd user services](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [udev rules writing](https://www.reactivated.net/writing_udev_rules.html)
- [ncat documentation](https://nmap.org/ncat/)
- [DCC++ EX](https://dcc-ex.com/) - The DCC command station software

## License

See the main project LICENSE file.

## Support

For issues specific to the auto-start feature:
1. Check the troubleshooting section above
2. Review logs: `journalctl --user -u dcc-usb-connector.service`
3. Test udev rules: `udevadm test /sys/class/tty/ttyUSB0`

For DCC++ EX or django-ram issues, see the main project documentation.
