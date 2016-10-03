"""A requirement of this project is that it supports Python
3.4. This module compensates for the few differences 3.4 and
later versions.
"""

import json
import sys


VERSION = (sys.version_info.major, sys.version_info.minor)

if VERSION >= (3, 5):
    InvalidJSONError = json.decoder.JSONDecodeError
else:
    InvalidJSONError = ValueError
