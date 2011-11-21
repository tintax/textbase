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

from datetime import datetime
import re
import string

from core import Field
import validators

class TextField(Field):
    pass
    
    
class IntField(Field):
    
    def to_python(self, value):
        return int(value)
        
        
class BoolField(Field):
    
    def to_python(self, value):
        if value in (True, False):
            return bool(value)
        if isinstance(value, basestring):
            value = value.lower()
        if value in ('true', 't', 'yes', 'y', '1'):
            return True
        if value in ('false', 'f', 'no', 'n', '0'):
            return False
        raise ValueError('"%s" cannot be converted to boolean' % value)     
        
        
class DateTimeField(Field):

    """
    A combined date and time representation of a single point in time.

    Uses a naive datetime.datetime python type to represent the
    timestamp internally. The value must have a date and optionally a
    time if converted from a string representation. If time is provided
    it must specify the hours and minutes and optionally seconds. 
    """

    date_re = re.compile('(\d{4})-(\d\d)-(\d\d)(.*)')
    time_re = re.compile('(\d\d):(\d\d)(?::(\d\d))?')

    msgs = {
        'format': '"%s" not in "YYYY-MM-DD [HH:MM[:SS]]" format',
        }

    def to_python(self, value):
        if isinstance(value, datetime):
            return value
        date = self.date_re.match(value.strip())
        if not date:
            raise ValueError(self.msgs['format'] % value)
        ints = list(int(x) for x in date.group(1,2,3))
        time_str = date.group(4).strip()
        if time_str:
            time = self.time_re.match(time_str)
            if not time:
                raise ValueError(self.msgs['format'] % value)
            ints.extend(int(x) for x in time.groups() if x)
        return datetime(*ints)
        
        
class TagField(Field):
    """
    A list of "tags" (strings containing alphanumeric, dash, or hash
    characters only).
    
    Uses a python list type internally. The tags are separated by commas
    when represented as a single string.
    """

    msgs = {
        'alnum': 'tags must contain alphanumeric or dash characters only'
        }

    valid_chars = set(string.letters + string.digits + '-')

    def to_python(self, value):
        if isinstance(value, basestring):
            tags = list(x.strip() for x in value.split(','))
        else:
            tags = list(str(x).strip() for x in value)
        for tag in tags:
            if not set(tag).issubset(self.valid_chars):
                raise ValueError(self.msgs['alnum'])
        return tags

    def to_string(self, value):
        return ', '.join(value)
        
        
class UuidField(Field):
    """
    A Universally Unique Identifier (UUID).
    
    Uses a python string internally. The text representation consists of
    32 hexadecimal digits in 5 groups separated by hyphens in the form
    8-4-4-4-12 (e.g. c3ff2d69-4146-4e98-a4ae-d8cfaa742495).
    """
    
    standard_validators = [validators.uuid]
