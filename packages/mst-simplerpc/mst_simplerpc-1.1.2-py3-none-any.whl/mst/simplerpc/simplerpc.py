"""
    simplerpc

    implements the SimpleRPCClient class to manage our simplified RPC implementation
"""
import requests
import urllib.parse
import base64
import re
import getpass
from mst.core import LogAPIUsage
from mst.authsrv import AuthSRV


class SimpleRPCClient:
    """Client object to interface with our simplified RPC servers"""

    def __getattr__(self, name):
        """internal python magic method that gets called when __getattribute__ fails to find named attribute
        used to overload unnamed functions as calls to CallRPC() method

        Args:
            name (str): function name of RPC
        """

        def func(*args, **kwargs):
            return self.CallRPC(name, *args, **kwargs)

        return func

    def __init__(
        self,
        base_url,
        username=None,
        password=None,
        authenticate=False,
        allow_unsafe=False,
        version=1,
    ):
        """instantiates new SimpleRPCClient object

        Args:
            base_url (str): RPC url to be called
            username (str): Defaults to None.
            password (str): Defaults to None.
            authenticate (bool): if the base url requires authentication. Defaults to False.
            allow_unsafe (bool): Defaults to False.
            version (int): version of SimpleRPC request/response format, v2 switches to HTTP codes and native return from functions

        Raises:
            ValueError: if base url requires authentication, all_unsafe should be True.
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.allow_unsafe = allow_unsafe
        self.authenticate = authenticate
        self.version = version

        LogAPIUsage()

        if re.search(
            r"auth-cgi-bin|auth-perl-bin|auth-fcgi-bin|auth-api-bin|auth-cgi|auth-cgid",
            base_url,
        ):
            self.authenticate = True

        if self.authenticate:
            if re.search(r"^http:", base_url) and allow_unsafe is False:
                raise ValueError(
                    "will not allow authenticated request on plaintext url, override with allow_unsafe=True"
                )

            if self.username is None:
                self.username = getpass.getuser()

            if self.password is None:
                self.password = AuthSRV().fetch(user=self.username, instance="ads")

    def _headers(self):
        """internal method used to inject HTTP headers into RPC calls (specifically for basic auth when needed)

        Returns:
            dict: dictionary of header info
        """
        headers = {"User-Agent": "mst-simplerpc/SimpleRPCClient:v1.1"}
        if self.username is not None and self.password is not None:
            basic_auth = base64.b64encode(
                f"{self.username}:{self.password}".encode("utf-8")
            ).decode("utf-8")
            headers["Authorization"] = f"Basic {basic_auth}"
        return headers

    def CallRPC(self, name, *args, **kwargs):
        """worker method that implements the RPC operation

        Args:
            name (str): function name of RPC

        Raises:
            RuntimeError: error returned from RPC

        Returns:
            tuple: returned data from RPC
        """
        url = f"{self.base_url}/{name}"
        data = None

        parts = []
        parts.extend([urllib.parse.quote(a) for a in args])

        for k, v in kwargs.items():
            k_clean = urllib.parse.quote(k)
            if v is None:
                parts.append(f"{k_clean}=")
            elif type(v) in (tuple, list):
                parts.extend([f"{k_clean}={urllib.parse.quote(val)}" for val in v])
            else:
                v_clean = urllib.parse.quote(v)
                parts.append(f"{k_clean}={v_clean}")

        if len(parts) > 0:
            data = "&".join(parts).encode()

        resp = requests.post(url, headers=self._headers(), data=data)
        if resp.raise_for_status():
            return None

        json_resp = resp.json()
        if self.version > 1 or isinstance(json_resp, dict):
            if json_resp["status"] == "success":
                return json_resp["data"]
            else:
                raise RuntimeError(f"Error returned from RPC: {json_resp['error']}")
        else:
            if isinstance(json_resp, list):
                val, msg, *data = json_resp
                if val == 0:
                    return data
                else:
                    raise RuntimeError(f"Error returned from RPC: {msg}")

        raise RuntimeError("Error returned from RPC: Invalid data format of response")
