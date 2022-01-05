from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import (ServiceUnavailable,
                                     ServiceReturnedUnexpectedResult)

from driver.connector import Connector


class DriverHealthCheck(BaseHealthCheckBackend):
    critical_service = False

    def check_status(self):
        try:
            Connector().passthrough(b'<s>')
        except ConnectionRefusedError as e:
            self.add_error(ServiceUnavailable("IOError"), e)
        except Exception as e:
            self.add_error(ServiceReturnedUnexpectedResult("IOError"), e)

    def identifier(self):
        return "DriverDaemon"
