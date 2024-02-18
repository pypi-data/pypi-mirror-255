"""Sanix API class."""
import requests

from .exceptions import SanixException

class Sanix:
    """Sanix API."""
    SANIX_API_HOST = "https://sanix.bitcomplex.pl"

    def __init__(self, serial_no, token) -> None:
        """Initialize the class instance."""
        self._serial_no = serial_no
        self._token = token

    def fetch_data(self):
        """Fetch the update."""
        _url = f"{self.SANIX_API_HOST}/api/measurement/read.php?serial_no={self._serial_no}&auth_token={self._token}"

        try:
            resp = requests.get(_url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as err:
            if err.response is not None:
                if err.response.status_code == 401:
                    raise SanixException("Could not authorize.") from err
        except requests.ConnectTimeout as ex:
            raise SanixException("Connection timeout while connecting to Sanix API") from ex
        except requests.ConnectionError as ex:
            raise SanixException("Connection error while connecting to Sanix API") from ex
