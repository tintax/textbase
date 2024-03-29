"""
This module provides common validation routines.
"""

# Copyright 2011 Matthew David Lawson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import string

def required(value):
    if value is None:
        raise ValueError('no value for required field')
        
def uuid(value):
    if not re.match('[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}', value):
        raise ValueError('not in uuid format')
        
def tag_sequence(value):
    """
    Check value is a sequence of strings consisting solely of
    alphanumeric or dash characters.
    """
    valid_chars = set(string.letters + string.digits + '-')
    for item in value:
        if not set(item).issubset(valid_chars):
            raise ValueError('alphanumeric or dash characters only')
