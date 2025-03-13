#!/usr/bin/env python3

import os
import time
import json
import socket
import logging
import paho.mqtt.client as mqtt

# FIXME: create a configuration
# TCP Socket Configuration
TCP_HOST = "192.168.10.110"  # Replace with your TCP server IP
TCP_PORT = 2560              # Replace with your TCP server port

# FIXME: create a configuration
# MQTT Broker Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "telemetry/commandstation"

# Connect to MQTT Broker
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)


# Connect function with automatic reconnection
def connect_mqtt():
    while True:
        try:
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            mqtt_client.loop_start()  # Start background loop
            logging.info("Connected to MQTT broker!")
            return
        except Exception as e:
            logging.info(f"Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)  # Wait before Retrying


# Ensure connection before publishing
def safe_publish(topic, message):
    if not mqtt_client.is_connected():
        print("MQTT Disconnected! Reconnecting...")
        connect_mqtt()  # Reconnect if disconnected

    result = mqtt_client.publish(topic, message, qos=1)
    result.wait_for_publish()  # Ensure message is published
    logging.debug(f"Published: {message}")


def process_message(message):
    """Parses the '<l cab speed dir>' format and converts it to JSON."""
    if not message.startswith("<l"):
        return None

    parts = message.strip().split()  # Split by spaces
    if len(parts) != 5:
        logging.debug(f"Invalid speed command: {message}")
        return None

    _, _cab, _, _speed, _ = parts  # Ignore the first `<t`
    cab = int(_cab)
    speed = int(_speed)
    if speed > 1 and speed < 128:
        direction = "r"
        speed = speed - 1
    elif speed > 129 and speed < 256:
        direction = "f"
        speed = speed - 129
    else:
        speed = 0
        direction = "n"

    try:
        json_data = {
            "cab": cab,
            "speed": speed,
            "dir": direction
        }
        return json_data
    except ValueError as e:
        logging.error(f"Error parsing message: {e}")
        return None


def start_tcp_listener():
    """Listens for incoming TCP messages and publishes them to MQTT."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((TCP_HOST, TCP_PORT))
        logging.info(
            f"Connected to TCP server at {TCP_HOST}:{TCP_PORT}"
        )

        while True:
            data = sock.recv(1024).decode("utf-8")  # Read a chunk of data
            if not data:
                break

            lines = data.strip().split("\n")  # Handle multiple lines
            for line in lines:
                json_data = process_message(line)
                if json_data:
                    safe_publish(MQTT_TOPIC, json.dumps(json_data))


# Start the listener
if __name__ == "__main__":
    logging.basicConfig(level=os.getenv("DCC_LOGLEVEL", "INFO").upper())
    start_tcp_listener()
