class Connector:

    @classmethod
    def __mqtt_pub(self, message):
        # to be encoded
        print(message)
        return True

    def passthrough(self, address, data):
        self.__mqtt_pub(data)

    def ops(self, address, data, function=False):
        if function:
            message = "<F {0} {1} {2}>".format(address, data['function'],
                                               data['state'])
        else:
            message = "<t 1 {0} {1} {2}>".format(address, data['speed'],
                                                 data['direction'])
        self.__mqtt_pub(message)
        return True

    def infra(self, data):
        power = data['power']
        if "track" in data:
            track = " {}".forma(data['track'].upper())
        else:
            track = ""

        if power:
            self.__mqtt_pub('<1{}>'.format(track))
        else:
            self.__mqtt_pub('<0{}>'.format(track))

    def emergency(self):
        self.__mqtt_pub('<!>')
