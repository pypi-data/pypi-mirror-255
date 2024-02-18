# Copyright (c) Microsoft. All rights reserved.


from typing import Optional

from pydantic import Field, field_validator

from semantic_kernel.kernel_pydantic import KernelBaseModel
from semantic_kernel.utils.validation import validate_function_param_name


class ParameterView(KernelBaseModel):
    name: str
    description: str
    default_value: str
    type_: Optional[str] = Field(default="string", alias="type")
    required: Optional[bool] = False

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str):
        validate_function_param_name(name)
        return name
