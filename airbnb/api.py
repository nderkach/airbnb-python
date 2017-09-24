import requests
import json
from datetime import datetime
from airbnb.random_request import RandomRequest


API_URL = "https://api.airbnb.com/v2"
API_KEY = "915pw2pnf4h1aiguhph5gc5b2"


class AuthError(Exception):
    """
    Authentication error
    """
    pass


class Api(object):
    """ Base API class
    >>> api = Api("airbnb@sharklasers.com", "qwerty1234")
    >>> api.uid
    144993238
    >>> api.get_profile() # doctest: +ELLIPSIS
    {...}
    >>> api.get_calendar(975964) # doctest: +ELLIPSIS
    {...}
    >>> api.get_reviews(975964) # doctest: +ELLIPSIS
    {...}
    >>> api = Api("foo", "bar") # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    AuthError
    >>> api = Api(uid=144993238, access_token="3jfmqfzmuwjaxb7wrgctyq3hs")
    >>> api = Api(uid=144993238, access_token="3jfmqfzmuwjaxb7wrgctyq3hs", session_cookie="_airbed_session_id=1aa1c70c9b0893aadd9f1343a85fd782")
    """

    def __init__(self, username=None, password=None,
                 uid=None, access_token=None, api_key=API_KEY, session_cookie=None):
        self._session = requests.Session()

        self._session.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json",
            "X-Airbnb-API-Key": api_key,
            "User-Agent": RandomRequest().get_random_user_agent(),
            "X-Airbnb-Device-ID": RandomRequest().get_random_udid(),
            "X-Airbnb-Advertising-ID": RandomRequest().get_random_uuid(),
            "X-Airbnb-Carrier-Name": "T-Mobile",  # TODO: randomize
            "X-Airbnb-Network-Type": "wifi",  # TODO: randomize
            "X-Airbnb-Currency": "USD"  # TODO: randomize
        }

        if uid and access_token:
            self.uid = uid
            self._access_token = access_token

            if session_cookie and "_airbed_session_id=" in session_cookie:
                self._session.headers.update({
                    "Cookie": session_cookie
                })

            self._session.headers.update({
                "X-Airbnb-OAuth-Token": self._access_token
            })

        else:
            assert(username and password)
            login_payload = {"email": username,
                             "password": password,
                             "type": "email"}

            r = self._session.post(
                API_URL + "/logins", data=json.dumps(login_payload)
            )

            if "login" not in r.json():
                raise AuthError
            r.raise_for_status()

            self._access_token = r.json()["login"]["id"]

            self._session.headers.update({
                "X-Airbnb-OAuth-Token": self._access_token
            })

            r = self._session.get(API_URL + "/logins/me")

            r.raise_for_status()

            self.uid = r.json()["login"]["account"]["id"]

    def get_profile(self):
        assert(self._access_token and self.uid)

        r = self._session.get(API_URL + "/logins/me")
        r.raise_for_status()

        return r.json()

    def get_calendar(self, listing_id, starting_month=datetime.now().month, starting_year=datetime.now().year, calendar_months=12):
        assert(self._access_token and self.uid)

        params = {
            'year': str(starting_year),
            'listing_id': str(listing_id),
            '_format': 'with_conditions',
            'count': str(calendar_months),
            'month': str(starting_month)
        }

        r = self._session.get(API_URL + "/calendar_months", params=params)
        r.raise_for_status()

        return r.json()

    def get_reviews(self, listing_id, offset=0, limit=20):
        assert(self._access_token and self.uid)

        params = {
            '_order': 'language_country',
            'listing_id': str(listing_id),
            '_offset': str(offset),
            'role': 'all',
            '_limit': str(limit),
            '_format': 'for_mobile_client',
        }

        r = self._session.get(API_URL + "/reviews", params=params)
        r.raise_for_status()

        return r.json()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
