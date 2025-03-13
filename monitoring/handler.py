#!/usr/bin/env python3

import os
import json
import logging
import datetime
import psycopg2
import paho.mqtt.client as mqtt

# MQTT Broker Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "telemetry/commandstation"

# TimescaleDB Configuration
DB_HOST = "localhost"
DB_NAME = "dccmonitor"
DB_USER = "dccmonitor"
DB_PASSWORD = "dccmonitor"


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    logging.info(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC)


# MQTT Callback: When a new message arrives
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        cab = payload["cab"]
        speed = payload["speed"]
        direction = payload["dir"]
        timestamp = datetime.datetime.now(datetime.UTC)

        # Insert into TimescaleDB
        cur.execute(
            "INSERT INTO telemetry (timestamp, cab, speed, dir) VALUES (%s, %s, %s, %s)",  # noqa: E501
            (timestamp, cab, speed, direction),
        )
        conn.commit()
        logging.debug(
            f"Inserted: {timestamp} | Cab: {cab} | Speed: {speed} | Dir: {direction}"  # noqa: E501
        )

    except Exception as e:
        logging.error(f"Error processing message: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=os.getenv("DCC_LOGLEVEL", "INFO").upper())

    # Connect to TimescaleDB
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST
    )
    cur = conn.cursor()

    # Ensure hypertable exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
            cab INT NOT NULL,
            speed DOUBLE PRECISION NOT NULL,
            dir TEXT NOT NULL
        );
    """)
    conn.commit()

    # Convert table to hypertable if not already
    cur.execute("SELECT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'telemetry');")  # noqa: E501
    if not cur.fetchone()[0]:
        cur.execute("SELECT create_hypertable('telemetry', 'timestamp');")
        conn.commit()

    # Setup MQTT Client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)

    # Start listening for messages
    logging.info(f"Listening for MQTT messages on {MQTT_TOPIC}...")
    client.loop_forever()
