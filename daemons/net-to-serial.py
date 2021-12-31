import serial
import asyncio


class SerialDaemon:
    def __init__(self):
        self.ser = serial.Serial('/dev/pts/7')  # WIP
        self.ser.baudrate = 115200

    def __del__(self):
        try:
            self.ser.close()
        except AttributeError:
            pass

    async def handle_echo(self, reader, writer):
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')

        print(f"Received {message!r} from {addr!r}")

        self.ser.write(data)
        response = self.read_until()
        print(f"Send: {response!r}")
        writer.write(response)
        await writer.drain()

        print("Close the connection")
        writer.close()


async def main():
    sd = SerialDaemon()
    server = await asyncio.start_server(
        sd.handle_echo, '127.0.0.1', 2560)  # WIP
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
