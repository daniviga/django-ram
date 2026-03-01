#!/usr/bin/env bash
#
# Installation script for DCC USB-to-Network Bridge auto-start
#
# This script installs the udev rule and systemd service to automatically
# start the dcc-usb-connector.service when USB device 1a86:7523 is connected.
#
# Usage:
#   ./install-udev-rule.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}DCC USB-to-Network Bridge Auto-Start Installation${NC}"
echo "=========================================================="
echo

# Check if running as root (not recommended for systemd user service)
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Warning: You are running as root.${NC}"
    echo "This script will install a user systemd service."
    echo "Please run as a regular user (not with sudo)."
    echo
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for required files
echo "Checking required files..."
if [ ! -f "$SCRIPT_DIR/99-dcc-usb-connector.rules" ]; then
    echo -e "${RED}Error: 99-dcc-usb-connector.rules not found${NC}"
    exit 1
fi
if [ ! -f "$SCRIPT_DIR/dcc-usb-connector.service" ]; then
    echo -e "${RED}Error: dcc-usb-connector.service not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ All required files found${NC}"
echo

# Install udev rule (requires sudo)
echo "Installing udev rule..."
echo "This requires sudo privileges."
sudo cp "$SCRIPT_DIR/99-dcc-usb-connector.rules" /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=tty
echo -e "${GREEN}✓ Udev rule installed${NC}"
echo

# Install systemd user service
echo "Installing systemd user service..."
mkdir -p ~/.config/systemd/user/
cp "$SCRIPT_DIR/dcc-usb-connector.service" ~/.config/systemd/user/
systemctl --user daemon-reload
echo -e "${GREEN}✓ Systemd service installed${NC}"
echo

# Enable lingering (allows user services to run without being logged in)
echo "Enabling systemd lingering for user..."
if loginctl show-user "$USER" | grep -q "Linger=yes"; then
    echo -e "${GREEN}✓ Lingering already enabled${NC}"
else
    sudo loginctl enable-linger "$USER"
    echo -e "${GREEN}✓ Lingering enabled${NC}"
fi
echo

# Check user groups
echo "Checking user permissions..."
if groups "$USER" | grep -q '\bdialout\b'; then
    echo -e "${GREEN}✓ User is in 'dialout' group${NC}"
else
    echo -e "${YELLOW}Warning: User is not in 'dialout' group${NC}"
    echo "You may need to add yourself to the dialout group:"
    echo "  sudo usermod -a -G dialout $USER"
    echo "Then log out and log back in for changes to take effect."
fi
echo

# Check for ncat
echo "Checking for required tools..."
if command -v ncat &> /dev/null; then
    echo -e "${GREEN}✓ ncat is installed${NC}"
else
    echo -e "${YELLOW}Warning: ncat is not installed${NC}"
    echo "Install it with: sudo dnf install nmap-ncat"
fi
echo

# Summary
echo "=========================================================="
echo -e "${GREEN}Installation complete!${NC}"
echo
echo "The service will automatically start when USB device 1a86:7523"
echo "is connected to /dev/ttyUSB0"
echo
echo "To test:"
echo "  1. Plug in the USB device"
echo "  2. Check service status: systemctl --user status dcc-usb-connector.service"
echo "  3. Test connection: telnet localhost 2560"
echo
echo "To manually control:"
echo "  Start:  systemctl --user start dcc-usb-connector.service"
echo "  Stop:   systemctl --user stop dcc-usb-connector.service"
echo "  Status: systemctl --user status dcc-usb-connector.service"
echo
echo "To view logs:"
echo "  journalctl --user -u dcc-usb-connector.service -f"
echo
echo "To uninstall:"
echo "  sudo rm /etc/udev/rules.d/99-dcc-usb-connector.rules"
echo "  rm ~/.config/systemd/user/dcc-usb-connector.service"
echo "  systemctl --user daemon-reload"
echo "  sudo udevadm control --reload-rules"
echo
