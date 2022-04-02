import socket

from driver.models import DriverConfiguration


class Connector:
    def __init__(self):
        self.config = DriverConfiguration.get_solo()

    def __send_data(self, message):
        resp = b""
        # convert to binary if str is received
        if isinstance(message, str):
            message = message.encode()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.config.remote_host, self.config.remote_port))
            sock.settimeout(self.config.timeout / 1000)  # milliseconds
            sock.sendall(message)
            while True:
                try:
                    resp += sock.recv(1024)
                except socket.timeout:
                    break
        return resp

    def passthrough(self, data):
        return self.__send_data(data)

    def ops(self, address, data, function=False):
        if function:
            message = "<F {0} {1} {2}>".format(
                address, data["function"], data["state"]
            )
        else:
            message = "<t 1 {0} {1} {2}>".format(
                address, data["speed"], data["direction"]
            )
        self.__send_data(message)

    def infra(self, data):
        if "track" in data:
            track = " {}".format(data["track"].upper())
        else:
            track = ""

        if data["power"]:
            self.__send_data("<1{}>".format(track))
        else:
            self.__send_data("<0{}>".format(track))

    def emergency(self):
        self.__send_data("<!>")
