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

* Initialize API with your airbnb.com username and password::

	from airbnb import Api
	api = Api(login, password)

* Get you user profile::

	api.get_profile()

* Get information about a room::

	api.get_room(roomid)
	
.. image:: https://travis-ci.org/nderkach/airbnb-python.png
    :target: https://travis-ci.org/nderkach/airbnb-python
    
