import serial
import logging
import socket
import asyncio
import time
import paho.mqtt.client as mqtt
from asyncio_mqtt import Client

MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1883


async def mqtt_broker(ser):
    async with Client(MQTT_HOST, port=MQTT_PORT) as client:
        await client.subscribe("dcc/commands")
        async with client.unfiltered_messages() as messages:
            async for message in messages:
                print(message.payload.decode())
                # ser.write(message.payload)


def main():
    client = mqtt.Client()
    # ser = serial.Serial('/dev/pts/7')
    # ser.baudrate = 9600
    ser = None  # remove me
    while True:
        try:
            client.connect(MQTT_HOST, MQTT_PORT)
            break
        except (socket.gaierror, ConnectionRefusedError):
            logging.warning('Broker not available')
            time.sleep(5)

    logging.info('Broker subscribed')
    client.disconnect()
    asyncio.run(mqtt_broker(ser))
    # ser.close()


if __name__ == "__main__":
    main()
