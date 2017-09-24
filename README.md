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

### Initialize API with your airbnb.com username and password:

```python
from airbnb import Api
api = Api(login, password)
```

### Get you user profile

```python
api.get_profile()
```

### Get listing availability

```python
api.get_calendar(listing_id)
```

Optional parameters:

- `starting_month`: first month of the calendar (can't be in the past)
- `starting_year`: first year of the calendar (can't be in the past)
- `calendar_months`: how many months ahead you want to get the calendar for

Example:

```python
api.get_calendar(975964, starting_month=9, starting_year=2017, calendar_months=1)
```

### Get listing reviews
 
```python
api.get_reviews(listing_id)
```

Optional parameters:

- `offset`: paging offset
- `limit`: number of results per page

Example:

```python
api.get_reviews(975964, offset=20, limit=20)
```


[![Build Status](https://travis-ci.org/nderkach/airbnb-python.svg)](https://travis-ci.org/nderkach/airbnb-python)
