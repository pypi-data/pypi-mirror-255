#!/usr/bin/env python

import requests


###############################################################################


class SimpleService(object):
    """
    A simple class to demonstrate how the code structure
    and documentation should be written.

    Please refer to 
    https://realpython.com/documenting-python-code
    for guide on how to write documentation

    and to https://realpython.com/python-pep8
    for guidelines on how to write easy to read code.

    ...

    Attributes
    ----------
    wan_ip : str
        The wan ip fetched from the wan ip service
    wan_ip_url : str
        The url to the service which will return the wan ip.
        There are many WAN IP Services like this to choose
        from, e.g:
        - ifconfig.me (default)
        - icanhazip.com
        - ipinfo.io/ip
        - api.ipify.org

    Methods
    -------
    fetch_wan_ip(wan_ip_url=None)
        Fetch the WAN IP from the wan ip service
    get_wan_ip()
        Return the already fetched wan ip.
        Note: We could return the fetched wan ip from
        fetch_wan_ip method, but for demonstration purpose
        we return the wan_ip from this method instead.
    """

    wan_ip = ""

    def __init__(self, wan_ip_url="https://ifconfig.me"):
        """
        Parameters
        ----------
        wan_ip_url : str
            The url to the service which will return the wan ip.
            (default: https://ifconfig.me)
        """

        self.wan_ip_url = wan_ip_url

    def fetch_wan_ip(self, wan_ip_url=None):
        """Fetch the wan ip from the wan ip service.

        If the argument 'wan_ip_url' is not provided, the default
        WAN IP Service URL us used.

        Parameters
        ----------
        wan_ip_url : str
            The url to the service which will return the wan ip.
            (default: https://ifconfig.me)
        """

        if not wan_ip_url:
            wan_ip_url = self.wan_ip_url
        r = requests.get(wan_ip_url)
        self.wan_ip = r.text

    def get_wan_ip(self):
        """Return the fetched wan ip."""

        return self.wan_ip

