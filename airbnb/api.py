import requests
import json


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
    >>> api.get_room(1298200) # doctest: +ELLIPSIS
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
            "User-Agent": "Airbnb/17.31 iPhone/9.2.1 Type/Phone",
            "X-Airbnb-Device-ID": "721ea97f85b866292abd3dffaf57b87d8c0ce1ee",  # TODO: randomize
            "X-Airbnb-Advertising-ID": "30343C53-B54B-4BDD-9CAD-8DBA3B858BD4",  # TODO: randomize
            "X-Airbnb-Carrier-Name": "T-Mobile", # TODO: randomize
            "X-Airbnb-Network-Type": "wifi", # TODO: randomize
            "X-Airbnb-Currency": "USD" # TODO: randomize
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

    def get_room(self, roomid):
        assert(self._access_token and self.uid)

        r = self._session.get(API_URL + "/listings/" + str(roomid))
        r.raise_for_status()

        return r.json()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
