# -*- coding: utf-8 -*-
"""
    src.verification
    ~~~~~~~~~~~~~~~~
    This module defines the apis required for verification

    Todo:

    :copyright: (c) 2015 by Dosepack LLC.

"""
import datetime
import logging

# get the logger for the pack from global configuration file logging.json

logger = logging.getLogger("root")


def display_date_to_datetime(display_date, max_time=False):
    """ Converts date string to datetime

        Args:
            display_date(str) : date in "%m-%d-%y" format
            max_time (bool) : to combine with max.time (default combines with min.time)

        Returns:
            datetime
    """
    display_date = datetime.datetime.strptime(display_date, "%m-%d-%y").date()
    if max_time:
        converted_datetime = datetime.datetime.combine(display_date, datetime.datetime.max.time())
    else:
        converted_datetime = datetime.datetime.combine(display_date, datetime.datetime.min.time())

    return converted_datetime
