import logging
import serial
import asyncio
import configparser


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

    async def handle_echo(self, reader, writer):
        data = await reader.read(100)
        addr = writer.get_extra_info('peername')

        logging.info("Received {} from {}".format(data, addr[0]))

        self.ser.write(data)
        response = line = self.ser.read()
        while line.strip():
            line = self.ser.read_until()
            if not line.decode().startswith("<*"):
                response += line
        logging.info("Send: {}".format(response))
        writer.write(response)
        await writer.drain()

        logging.info("Close the connection")
        writer.close()

    async def return_board(self):
        self.ser.write(b'<s>')
        self.ser.read_until()  # we need the second line
        return(self.ser.read_until().decode().strip('\n'))


async def main():
    config = configparser.ConfigParser()
    config.read("config.ini")
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
    logging.warning(
        await sd.return_board())

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
