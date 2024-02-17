# -*- coding: utf-8 -*-
"""
    model.model_device_manager
    ~~~~~~~~~~~~~~~~
    The module defines the model for managing the conveyor system. A conveyor system can have one or
    more robots. The robots are grouped together to form a robot unit. A conveyor also has various devices
    attached to it.The device includes mainly pack separator, robot cars, heat seal, cart. All this devices
    and robot unit grouped together makes one conveyor system. In model we represent this group by device group header.

    Todo:

    :copyright: (c) 2015 by Dosepack LLC.

"""
import datetime
import functools
import logging

from peewee import CharField, BooleanField, ForeignKeyField, DateTimeField, DateField, PrimaryKeyField, InternalError, \
    DoesNotExist, IntegrityError, FixedCharField, IntegerField, SmallIntegerField, DataError, DecimalField, fn, \
    JOIN_LEFT_OUTER
from playhouse.shortcuts import cast

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster
from src.model.model_unit_conversion import UnitConversion
from src.model.model_unit_master import UnitMaster
from src.model.model_zone_master import ZoneMaster
from src.exceptions import NoLocationExists
from src.model.model_device_master import DeviceMaster
from src.model.model_device_type_master import DeviceTypeMaster
from src.model.model_location_master import LocationMaster

# get the logger for the pack from global configuration file logging.json
from src.model.model_container_master import ContainerMaster

