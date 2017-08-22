airbnb-python
===================

Airbnb Python API

Disclaimer
----------

This is a unofficial python API wrapper for airbnb.com

Using this software might contradict airbnb.com terms of service

Requirements
------------

* requests

Usage:
------

	pip install airbnb-python

Initialize API with your airbnb.com username and password:

from airbnb import Api
api = Api(login, password)

Get you user profile:

api.get_profile()

Get listing availability:
    
api.get_calendar(listing_id)

Optional parameters:

- `starting_month`: first month of the calendar (can't be in the past)
- `starting_year`: first year of the calendar (can't be in the past)
- `calendar_months`: how many months ahead you want to get the calendar for

Example:

api.get_calendar(975964, starting_month=9, starting_year=2017, calendar_months=1)


	
.. image:: https://travis-ci.org/nderkach/airbnb-python.png
    :target: https://travis-ci.org/nderkach/airbnb-python
