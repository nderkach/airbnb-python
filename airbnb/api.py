import requests
import json
import datetime
from dateutil.tz import tzlocal
from airbnb.random_request import RandomRequest
import os
import functools


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


class MissingParameterError(Exception):
    """
    Missing parameter error
    """
    pass


class MissingAccessTokenError(MissingParameterError):
    """
    Missing access token error
    """
    pass


def require_auth(function):
    """
    A decorator that wraps the passed in function and raises exception
    if access token is missing
    """
    @functools.wraps(function)
    def wrapper(self, *args, **kwargs):
        if not self.access_token():
            raise MissingAccessTokenError
        return function(self, *args, **kwargs)
    return wrapper


def randomizable(function):
    """
    A decorator which randomizes requests if needed
    """
    @functools.wraps(function)
    def wrapper(self, *args, **kwargs):
        if self.randomize:
            self.randomize_headers()
        return function(self, *args, **kwargs)
    return wrapper


class Api(object):
    """ Base API class
    >>> api = Api(access_token=os.environ.get("AIRBNB_ACCESS_TOKEN"))
    >>> api.get_profile() # doctest: +ELLIPSIS
    {...}
    >>> api = Api()
    >>> api.get_homes("Lisbon, Portugal") # doctest: +ELLIPSIS
    {...}
    >>> api.get_homes(gps_lat=55.6123352, gps_lng=37.7117917) # doctest: +ELLIPSIS
    {...}
    >>> api.get_calendar(975964) # doctest: +ELLIPSIS
    {...}
    >>> api.get_reviews(975964) # doctest: +ELLIPSIS
    {...}
    >>> api = Api(randomize=True)
    >>> api.get_listing_details(975964) # doctest: +ELLIPSIS
    {...}
    """

    def __init__(self, username=None, password=None, access_token=None, api_key=API_KEY, session_cookie=None,
                 proxy=None, randomize=None):
        self._session = requests.Session()
        self._access_token = None
        self.user_agent = "Airbnb/19.02 AppVersion/19.02 iPhone/12.1.2 Type/Phone"
        self.udid = "9120210f8fb1ae837affff54a0a2f64da821d227"
        self.uuid = "C326397B-3A38-474B-973B-F022E6E4E6CC"
        self.randomize = randomize

        self._session.headers = {
            "accept": "application/json",
            "accept-encoding": "br, gzip, deflate",
            "content-type": "application/json",
            "x-airbnb-api-key": api_key,
            "user-agent": self.user_agent,
            "x-airbnb-screensize": "w=375.00;h=812.00",
            "x-airbnb-carrier-name": "T-Mobile",
            "x-airbnb-network-type": "wifi",
            "x-airbnb-currency": "USD",
            "x-airbnb-locale": "en",
            "x-airbnb-carrier-country": "us",
            "accept-language": "en-us",
            "airbnb-device-id": self.udid,
            "x-airbnb-advertising-id": self.uuid
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

        elif username and password:
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
        else:
            # no auth
            pass

    def access_token(self):
        return self._access_token

    def set_user_agent(self, user_agent):
        self.user_agent = user_agent
        self._session.headers['user-agent'] = user_agent

    def set_udid(self, udid):
        self.udid = udid
        self._session.headers['airbnb-device-id'] = udid

    def set_uuid(self, uuid):
        self.uuid = uuid
        self._session.headers['x-airbnb-advertising-id'] = uuid

    def randomize_headers(self):
        self.set_user_agent(RandomRequest.get_random_user_agent())
        self.set_udid(RandomRequest.get_random_udid())
        self.set_uuid(RandomRequest.get_random_uuid())

    @require_auth
    def get_profile(self):
        """
        Get my own profile
        """
        r = self._session.get(API_URL + "/logins/me")
        r.raise_for_status()

        return r.json()

    @randomizable
    def get_calendar(self, listing_id, starting_month=datetime.datetime.now().month, starting_year=datetime.datetime.now().year, calendar_months=12):
        """
        Get availability calendar for a given listing
        """
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

    @randomizable
    def get_reviews(self, listing_id, offset=0, limit=20):
        """
        Get reviews for a given listing
        """
        params = {
            '_order': 'language_country',
            'listing_id': str(listing_id),
            '_offset': str(offset),
            'role': 'all',
            '_limit': str(limit),
            '_format': 'for_mobile_client',
        }

        print(self._session.headers)

        r = self._session.get(API_URL + "/reviews", params=params)
        r.raise_for_status()

        return r.json()


    # Host APIs

    @require_auth
    def get_listing_calendar(self, listing_id, starting_date=datetime.datetime.now(), calendar_months=6):
        """
        Get host availability calendar for a given listing
        """
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

    # User past trips and stats

    @require_auth
    def get_trip_schedules(self):
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

    @require_auth
    def get_travel_plans(self, upcoming_scheduled_plans_limit=20, past_scheduled_plans_limit=8):
        now = datetime.datetime.now(tzlocal())
        strftime_date = now.strftime('%Y-%m-%dT%H:%M:%S%z')

        params = {
            'now': '{}:{}'.format(strftime_date[:-2], strftime_date[-2:]),
            'upcoming_scheduled_plans_limit': upcoming_scheduled_plans_limit,
            'past_scheduled_plans_limit': past_scheduled_plans_limit
        }

        r = self._session.get(API_URL + "/plans", params=params)
        r.raise_for_status()

        return r.json()['plans'][0]

    @require_auth
    def get_scheduled_plan(self, identifier):
        assert(self._access_token)

        params = {
            '_format': 'for_trip_day_view'
        }

        r = self._session.get(API_URL + "/scheduled_plans/{}".format(identifier), params=params)
        r.raise_for_status()

        return r.json()['scheduled_plan']

    @require_auth
    def get_reservation(self, reservation_id):
        assert(self._access_token)

        params = {
            '_format': 'for_trip_planner'
        }

        r = self._session.get(API_URL + "/reservations/{}".format(reservation_id), params=params)
        r.raise_for_status()

        return r.json()['reservation']

    @require_auth
    def get_all_past_reservations(self):
        past_scheduled_plan_ids = self.get_travel_plans()['past_scheduled_plans']['metadata']['cache']['identifiers']

        past_reservations = []
        for plan_id in past_scheduled_plan_ids:
            scheduled_plan = self.get_scheduled_plan(plan_id)
            reservation_id = scheduled_plan['events'][0]['destination']['reservation_key']
            past_reservations.append(self.get_reservation(reservation_id))

        return past_reservations

    @require_auth
    def get_total_money_spent_in_usd(self):
        reservations = self.get_all_past_reservations()

        total_spent = 0.0
        for reservation in reservations:
            if reservation['total_price_formatted'].startswith('$'):
                dollars_spent = reservation['total_price_formatted']
                total_spent += float(dollars_spent[1:])

        return total_spent

    # Listing search

    @randomizable
    def get_homes(self, query=None, gps_lat=None, gps_lng=None, offset=0, items_per_grid=8):
        """
        Search listings with
            * Query (e.g. query="Lisbon, Portugal") or
            * Location (e.g. gps_lat=55.6123352&gps_lng=37.7117917)
        """
        params = {
            'is_guided_search': 'true',
            'version': '1.3.9',
            'section_offset': '0',
            'items_offset': str(offset),
            'adults': '0',
            'screen_size': 'small',
            'source': 'explore_tabs',
            'items_per_grid': str(items_per_grid),
            '_format': 'for_explore_search_native',
            'metadata_only': 'false',
            'refinement_paths[]': '/homes',
            'timezone': 'Europe/Lisbon',
            'satori_version': '1.0.7'
        }

        if not query and not (gps_lat and gps_lng):
            raise MissingParameterError("Missing query or gps coordinates")

        if query:
            params['query'] = query

        if gps_lat and gps_lng:
            params['gps_lat'] = gps_lat
            params['gps_lng'] = gps_lng

        r = self._session.get(API_URL + '/explore_tabs', params=params)
        r.raise_for_status()

        return r.json()

    @randomizable
    def get_listing_details(self, listing_id):
        params = {
            'adults': '0',
            '_format': 'for_native',
            'infants': '0',
            'children': '0'
        }

        r = self._session.get(API_URL + '/pdp_listing_details/' + str(listing_id), params=params)
        r.raise_for_status()

        return r.json()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
