import requests
import json
import datetime
from airbnb.random_request import RandomRequest
import os


API_URL = "https://api.airbnb.com/v2"
API_KEY = "915pw2pnf4h1aiguhph5gc5b2"


class AuthError(Exception):
    """
    Authentication error
    """
    pass


class VerificationError(AuthError):
    """
    Authentication error
    """
    pass


class Api(object):
    """ Base API class
    >>> api = Api(os.environ.get("AIRBNB_LOGIN"), os.environ.get("AIRBNB_PASSWORD")) # doctest: +ELLIPSIS
    Your access token: ...
    >>> api.get_profile() # doctest: +ELLIPSIS
    {...}
    >>> api.get_calendar(975964) # doctest: +ELLIPSIS
    {...}
    >>> api.get_reviews(975964) # doctest: +ELLIPSIS
    {...}
    >>> api = Api(access_token=os.environ.get("AIRBNB_ACCESS_TOKEN"))
    """

    def __init__(self, username=None, password=None, access_token=None, api_key=API_KEY, session_cookie=None,
                 proxy=None):
        self._session = requests.Session()

        self._session.headers = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate",
            "content-type": "application/json",
            "x-airbnb-api-key": api_key,
            "user-agent": "Airbnb/18.23 AppVersion/18.23 iPhone/12.0 Type/Phone",
            "x-airbnb-device-id": "9120210f8fb1ae837affff54a0a2f64da821d227",
            "x-airbnb-advertising-id": "16CE6BF7-90CC-41A8-8305-B7B3183A2787",
            "x-airbnb-carrier-name": "T-Mobile",
            "x-airbnb-network-type": "wifi",
            "x-airbnb-currency": "USD",
            "x-airbnb-locale": "en",
            "x-airbnb-carrier-country": "us",
            "accept-language": "en-us"
        }

        if proxy:
            self._session.proxies = {
                "http": proxy,
                "https": proxy
            }

        if access_token:
            self._access_token = access_token

            if session_cookie and "_airbed_session_id=" in session_cookie:
                self._session.headers.update({
                    "Cookie": session_cookie
                })

            self._session.headers.update({
                "x-airbnb-oauth-token": self._access_token
            })

        else:
            assert(username and password)
            login_payload = {"email": username,
                             "password": password,
                             "type": "email"}

            r = self._session.post(
                API_URL + "/logins", data=json.dumps(login_payload)
            )

            if r.status_code == 420:
                raise VerificationError
            elif r.status_code == 403:
                raise AuthError

            self._access_token = r.json()["login"]["id"]

            print("Your access token: {}".format(self._access_token))

            self._session.headers.update({
                "x-airbnb-oauth-token": self._access_token
            })

    def get_profile(self):
        assert(self._access_token)

        r = self._session.get(API_URL + "/logins/me")
        r.raise_for_status()

        return r.json()

    def get_calendar(self, listing_id, starting_month=datetime.datetime.now().month, starting_year=datetime.datetime.now().year, calendar_months=12):
        assert(self._access_token)

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
        assert(self._access_token)

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

    def get_listings(self, user_id, offset=0, limit=50):
        assert(self._access_token)

        params = {
            'has_availability': 'true',
            'format': 'v1_legacy_short',
            'user_id': str(user_id),
            '_limit': str(limit),
            '_offset': str(offset)
        }

        r = self._session.get(API_URL + "/listings", params=params)
        r.raise_for_status()

        return r.json()

    def get_listing_calendar(self, listing_id, starting_date=datetime.datetime.now(), calendar_months=6):
        assert(self._access_token)

        params = {
            '_format': 'host_calendar_detailed'
        }

        starting_date_str = starting_date.strftime("%Y-%m-%d")
        ending_date_str = (
            starting_date + datetime.timedelta(days=30)).strftime("%Y-%m-%d")

        r = self._session.get(API_URL + "/calendars/{}/{}/{}".format(
            str(listing_id), starting_date_str, ending_date_str), params=params)
        r.raise_for_status()

        return r.json()

    def get_trip_schedules(self):
        assert(self._access_token)

        params = {
            '_format': 'for_unbundled_itinerary',
            '_limit': '10',
            '_offset': '0',
            'client_version': '3',
            'exclude_free_time': 'false'
        }

        r = self._session.get(API_URL + '/trip_schedules', params=params)

        r.raise_for_status()
        return r.json()["trip_schedules"]


if __name__ == "__main__":
    import doctest
    doctest.testmod()
