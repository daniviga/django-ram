import socket

from driver.models import DriverConfiguration


class Connector:

    def __init__(self):
        self.config = DriverConfiguration.get_solo()

    def __send_data(self, message):
        # to be encoded
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.config.remote_host, self.config.remote_port))
            sock.sendall(message)
            resp = sock.recv(1024)

        print(resp)
        return True

    def passthrough(self, data):
        self.__send_data(data)

    def ops(self, address, data, function=False):
        if function:
            message = "<F {0} {1} {2}>".format(address, data['function'],
                                               data['state'])
        else:
            message = "<t 1 {0} {1} {2}>".format(address, data['speed'],
                                                 data['direction'])
        self.__send_data(message)
        return True

    def infra(self, data):
        power = data['power']
        if "track" in data:
            track = " {}".forma(data['track'].upper())
        else:
            track = ""

        if power:
            self.__send_data('<1{}>'.format(track))
        else:
            self.__send_data('<0{}>'.format(track))

    def emergency(self):
        self.__send_data('<!>')
