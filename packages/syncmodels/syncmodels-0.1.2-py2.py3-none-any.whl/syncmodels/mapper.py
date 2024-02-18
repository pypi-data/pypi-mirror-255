"""
Mappers transform plain dict to another dict
converting key and values.

Classes definition are inspired on pydantic

"""
import re
import sys
import traceback
from typing import Dict, Union

from datetime import timedelta
from dateutil.parser import parse

# ------------------------------------------------
# model suport
# ------------------------------------------------
from .model import *

# ------------------------------------------------
# Converter functions
# ------------------------------------------------
from .helpers import (
    BOOL,
    DATE,
    DURATION,
    FLOAT,
    I,
    INT,
    STRIP,
    TEXT,
)

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

from pycelium.tools.logs import logger

log = logger(__name__)

# =========================================================
# Mappers Support
# =========================================================


class Mapper:
    @classmethod
    def _populate(cls):
        cls.MAPPING = {}
        for key in dir(cls):
            value = getattr(cls, key)
            if isinstance(value, tuple):
                l = len(value)
                if l == 2:
                    # is an attribute
                    cls.MAPPING[key] = *value, None
                elif l == 3:
                    cls.MAPPING[key] = value

        return cls.MAPPING

    @classmethod
    def transform(cls, org: Dict, only_defined=False):
        assert isinstance(org, dict)
        result = {} if only_defined else dict(org)
        MAP = getattr(cls, 'MAPPING', None) or cls._populate()
        try:
            for k in set(org).intersection(MAP):
                v = org[k]
                t_name, t_value, t_default = MAP[k]
                if isinstance(t_name, str):
                    m = re.match(t_name, k)
                    if m:
                        name = m.group(0)
                    else:
                        name = t_name
                else:
                    name = t_name(k)
                value = t_value(v)
                result[name] = value
        except Exception as why:
            log.error(why)
            log.error("".join(traceback.format_exception(*sys.exc_info())))
            foo = 1
        return result

    @classmethod
    def pydantic(cls, org, **extra):
        """Create a pydantic object as well"""
        klass = getattr(cls, 'PYDANTIC', None)
        if klass:
            org.update(extra)
            norm = cls.transform(org)
            item = klass(**norm)
            return item
        log.warning(f"{cls} has not defined a PYDANTIC class")
        return norm
