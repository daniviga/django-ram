#!/usr/bin/env python3
import time
import logging
import serial
import asyncio
import configparser

from pathlib import Path


class SerialDaemon:
    def __init__(self, config):
        self.ser = serial.Serial(
            config["Serial"]["Port"],
            timeout=int(config["Serial"]["Timeout"])/1000)
        self.ser.baudrate = config["Serial"]["Baudrate"]

    def __del__(self):
        try:
            self.ser.close()
        except AttributeError:
            pass

    def __read_serial(self):
        """Serial reader wrapper"""
        response = b""
        while True:
            line = self.ser.read_until()
            if not line.strip():  # empty line
                break
            if line.decode().startswith("<*"):
                logging.debug("Serial debug: {}".format(line))
            else:
                response += line
        logging.debug("Serial read: {}".format(response))

        return response

    def __write_serial(self, data):
        """Serial writer wrapper"""
        self.ser.write(data)

    async def handle_echo(self, reader, writer):
        """Process a request from socket and return the response"""
        while 1:  # keep connection to client open
            data = await reader.read(100)
            if not data:  # client has disconnected
                break

            addr = writer.get_extra_info('peername')
            logging.info("Received {} from {}".format(data, addr[0]))

            self.__write_serial(data)
            response = self.__read_serial()
            writer.write(response)
            await writer.drain()
            logging.info("Sent: {}".format(response))

        writer.close()
        await writer.wait_closed()

    async def return_board(self):
        """Return the board signature"""
        self.__read_serial()  # drain the serial buffer on startup
        self.__write_serial(b"<s>")
        time.sleep(0.5)
        board = self.__read_serial().decode().split("\n")[1]  # get second line

        return(board)


async def main():
    config = configparser.ConfigParser()
    config.read(
        Path(__file__).resolve().parent / "config.ini")  # mimick os.path.join
    logging.basicConfig(level=config["Daemon"]["LogLevel"].upper())

    sd = SerialDaemon(config)
    server = await asyncio.start_server(
        sd.handle_echo,
        config["Daemon"]["ListeningIP"],
        config["Daemon"]["ListeningPort"])
    addr = server.sockets[0].getsockname()
    logging.warning("Serving on {} port {}".format(addr[0], addr[1]))
    logging.warning(
        "Proxying to {} (Baudrate: {}, Timeout: {})".format(
            config["Serial"]["Port"],
            config["Serial"]["Baudrate"],
            config["Serial"]["Timeout"]))
    logging.warning("Initializing board")
    logging.warning(
        await sd.return_board())

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
