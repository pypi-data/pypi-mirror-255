# -*- coding: utf-8 -*-
"""
    src.parse
    ~~~~~~~~~~~~~~~~

    This module covers the generic parser program which receives a file
    with a given format and parses it to generate a pandas data frame from it.

    The created data frame can be queried to filter data based on criteria
    specified by the user. The parser program is a completely  offline program.

    After the data frame is created the parser module also helps in inserting
    records into the proper database tables from the queries created on data frame.

    Example:
            $ python example_google.py


    Todo:

    :copyright: (c) 2015 by Dosepack LLC.

    SHIFTED TO SERVICE LAYER

"""
