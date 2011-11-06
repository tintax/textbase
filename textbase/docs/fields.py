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

from core import Field

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
