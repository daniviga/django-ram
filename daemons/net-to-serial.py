#!/usr/bin/env python3
import re
import logging
import serial
import asyncio
import configparser

from pathlib import Path


class SerialDaemon:
    connected_clients = set()

    def __init__(self, config):
        self.ser = serial.Serial(
            config["Serial"]["Port"],
            timeout=int(config["Serial"]["Timeout"]) / 1000,
        )
        self.ser.baudrate = config["Serial"]["Baudrate"]
        self.max_clients = int(config["Daemon"]["MaxClients"])

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
        logging.info(
            "Clients already connected: {} (max: {})".format(
                len(self.connected_clients),
                self.max_clients,
            )
        )

        addr = writer.get_extra_info("peername")[0]
        if len(self.connected_clients) < self.max_clients:
            self.connected_clients.add(writer)
            while True:  # keep connection to client open
                data = await reader.read(100)
                if not data:  # client has disconnected
                    break
                logging.info("Received {} from {}".format(data, addr))
                self.__write_serial(data)
                response = self.__read_serial()
                for client in self.connected_clients:
                    client.write(response)
                    await client.drain()
                logging.info("Sent: {}".format(response))
            self.connected_clients.remove(writer)
        else:
            logging.warning(
                "TooManyClients: client {} disconnected".format(addr)
            )

        writer.close()
        await writer.wait_closed()

    async def return_board(self):
        """Return the board signature"""
        line = ""
        # drain the serial until we are ready to go
        self.__write_serial(b"<s>")
        while "DCC-EX" not in line:
            line = self.__read_serial().decode()
        board = re.findall(r"<iDCC-EX.*>", line)[0]
        return board


async def main():
    config = configparser.ConfigParser()
    config.read(
        Path(__file__).resolve().parent / "config.ini"
    )  # mimick os.path.join
    logging.basicConfig(level=config["Daemon"]["LogLevel"].upper())

    sd = SerialDaemon(config)
    server = await asyncio.start_server(
        sd.handle_echo,
        config["Daemon"]["ListeningIP"],
        config["Daemon"]["ListeningPort"],
    )
    addr = server.sockets[0].getsockname()
    logging.info("Serving on {} port {}".format(addr[0], addr[1]))
    logging.info(
        "Proxying to {} (Baudrate: {}, Timeout: {})".format(
            config["Serial"]["Port"],
            config["Serial"]["Baudrate"],
            config["Serial"]["Timeout"],
        )
    )
    logging.info("Initializing board")
    logging.info("Board {} ready".format(await sd.return_board()))

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
