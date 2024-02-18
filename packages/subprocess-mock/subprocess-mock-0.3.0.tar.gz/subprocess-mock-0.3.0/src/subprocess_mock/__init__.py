# -*- coding: utf-8 -*-

"""

subprocess_mock

Base module


Copyright (C) 2024 Rainer Schwarzbach

This file is part of subprocess-mock.

subprocess-mock is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

subprocess-mock is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


from .parent import Popen  # noqa: F401
from .functions import (  # noqa: F401
    call,
    check_call,
    getstatusoutput,
    getoutput,
    check_output,
    run,
)


__version__ = "0.3.0"


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
