import logging

class LocalParameterServer(object):

    def __init__(self, public_ip, port):
        self._public_ip = public_ip
        self._port = port

        self._log = logging.getLogger("cirrus.automate.LocalParameterServer")

    def __str__(self):
        """Return a string representation of this parameter server.

        Returns:
            str: The string representation.
        """
        return "ParameterServer@%s:%d" % (self.public_ip(), self.ps_port())


    def public_ip(self):
        """Get the public IP address of this instance.

        Returns:
            str: The IP address.
        """
        return self._public_ip

    def ps_port(self):
        return self._port

    def start(self, config):
        pass

    def stop(self):
        pass

    def wait_until_started(self):
        pass
