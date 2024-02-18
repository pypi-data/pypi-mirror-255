"""This module contains the base model support.
"""
from typing import List, Optional, Union
from datetime import datetime

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from pydantic.dataclasses import dataclass
from pydantic import validator


class SyncConfig:
    # anystr_lower = True
    allow_population_by_field_name = True
    arbitrary_types_allowed = True

    # min_anystr_length = 2
    # max_anystr_length = 10
    ## validate_all = True
    ## validate_assignment = True
    # error_msg_templates = {
    #'value_error.any_str.max_length': 'max_length:{limit_value}',
    # }
    # smart_union = True
    pass


# @dataclass(config=SyncConfig)
class BaseModel(PydanticBaseModel):
    pass
