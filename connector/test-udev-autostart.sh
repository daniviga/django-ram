#!/usr/bin/env bash
#
# Test script for DCC USB-to-Network Bridge auto-start/stop functionality
#
# This script helps verify that the service starts when the USB device
# is connected and stops when it's removed.
#
# Usage:
#   ./test-udev-autostart.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== DCC USB-to-Network Bridge Auto-Start/Stop Test ===${NC}"
echo

# Check if udev rule is installed
echo -e "${BLUE}1. Checking udev rule installation...${NC}"
if [ -f /etc/udev/rules.d/99-dcc-usb-connector.rules ]; then
    echo -e "${GREEN}✓ Udev rule is installed${NC}"
    echo "   Location: /etc/udev/rules.d/99-dcc-usb-connector.rules"
else
    echo -e "${RED}✗ Udev rule is NOT installed${NC}"
    echo "   Run: sudo cp 99-dcc-usb-connector.rules /etc/udev/rules.d/"
    exit 1
fi
echo

# Check if service is installed
echo -e "${BLUE}2. Checking systemd service installation...${NC}"
if [ -f ~/.config/systemd/user/dcc-usb-connector.service ]; then
    echo -e "${GREEN}✓ Systemd service is installed${NC}"
    echo "   Location: ~/.config/systemd/user/dcc-usb-connector.service"
else
    echo -e "${RED}✗ Systemd service is NOT installed${NC}"
    echo "   Run: cp dcc-usb-connector.service ~/.config/systemd/user/"
    exit 1
fi
echo

# Check lingering
echo -e "${BLUE}3. Checking systemd lingering...${NC}"
if loginctl show-user "$USER" | grep -q "Linger=yes"; then
    echo -e "${GREEN}✓ Lingering is enabled${NC}"
else
    echo -e "${YELLOW}⚠ Lingering is NOT enabled${NC}"
    echo "   Services may not start automatically when you're not logged in"
    echo "   Run: sudo loginctl enable-linger $USER"
fi
echo

# Check if device is connected
echo -e "${BLUE}4. Checking USB device...${NC}"
if lsusb | grep -q "1a86:7523"; then
    echo -e "${GREEN}✓ USB device 1a86:7523 is connected${NC}"
    lsusb | grep "1a86:7523"
    
    if [ -e /dev/ttyUSB0 ]; then
        echo -e "${GREEN}✓ /dev/ttyUSB0 exists${NC}"
        ls -l /dev/ttyUSB0
    else
        echo -e "${YELLOW}⚠ /dev/ttyUSB0 does NOT exist${NC}"
        echo "   The device may be on a different port"
        echo "   Available ttyUSB devices:"
        ls -l /dev/ttyUSB* 2>/dev/null || echo "   (none found)"
    fi
else
    echo -e "${YELLOW}⚠ USB device 1a86:7523 is NOT connected${NC}"
    echo "   Please plug in the device to test"
fi
echo

# Check service status
echo -e "${BLUE}5. Checking service status...${NC}"
if systemctl --user is-active --quiet dcc-usb-connector.service; then
    echo -e "${GREEN}✓ Service is RUNNING${NC}"
    systemctl --user status dcc-usb-connector.service --no-pager -l
else
    echo -e "${YELLOW}⚠ Service is NOT running${NC}"
    echo "   Status:"
    systemctl --user status dcc-usb-connector.service --no-pager -l || true
fi
echo

# Test udev rule
echo -e "${BLUE}6. Testing udev rule (if device is connected)...${NC}"
if [ -e /dev/ttyUSB0 ]; then
    echo "   Running: udevadm test /sys/class/tty/ttyUSB0"
    echo "   Looking for SYSTEMD_USER_WANTS..."
    if udevadm test /sys/class/tty/ttyUSB0 2>&1 | grep -q "SYSTEMD_USER_WANTS"; then
        echo -e "${GREEN}✓ Udev rule is triggering systemd${NC}"
        udevadm test /sys/class/tty/ttyUSB0 2>&1 | grep "SYSTEMD_USER_WANTS"
    else
        echo -e "${RED}✗ Udev rule is NOT triggering systemd${NC}"
        echo "   The rule may not be matching correctly"
    fi
else
    echo -e "${YELLOW}⚠ Cannot test udev rule - device not connected${NC}"
fi
echo

# Check network port
echo -e "${BLUE}7. Checking network port 2560...${NC}"
if netstat -tuln 2>/dev/null | grep -q ":2560" || ss -tuln 2>/dev/null | grep -q ":2560"; then
    echo -e "${GREEN}✓ Port 2560 is listening${NC}"
    netstat -tuln 2>/dev/null | grep ":2560" || ss -tuln 2>/dev/null | grep ":2560"
else
    echo -e "${YELLOW}⚠ Port 2560 is NOT listening${NC}"
    echo "   Service may not be running or ncat failed to start"
fi
echo

# Summary and instructions
echo -e "${BLUE}=== Test Summary ===${NC}"
echo
echo "To test auto-start/stop behavior:"
echo
echo "1. ${YELLOW}Monitor the service in one terminal:${NC}"
echo "   watch -n 1 'systemctl --user status dcc-usb-connector.service'"
echo
echo "2. ${YELLOW}Monitor udev events in another terminal:${NC}"
echo "   udevadm monitor --property --subsystem-match=tty"
echo
echo "3. ${YELLOW}Plug in the USB device${NC} and watch:"
echo "   - Udev should detect the device"
echo "   - Service should automatically start"
echo "   - Port 2560 should become available"
echo
echo "4. ${YELLOW}Unplug the USB device${NC} and watch:"
echo "   - Udev should detect device removal"
echo "   - Service should automatically stop (thanks to StopWhenUnneeded=yes)"
echo "   - Port 2560 should close"
echo
echo "5. ${YELLOW}Check logs:${NC}"
echo "   journalctl --user -u dcc-usb-connector.service -f"
echo
echo "Expected behavior:"
echo "  • Device connected  → Service starts → Port 2560 opens"
echo "  • Device removed    → Service stops  → Port 2560 closes"
echo
