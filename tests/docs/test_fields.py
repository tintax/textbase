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

from textbase.docs.fields import *
from tests import utils

class FieldTests(object):

    field_class = None
    str_values = ()  # (string input, python output) tuples
    py_values = ()   # (python input, string output) tuples
    invalid_values = ()
    
    def test_valid_python_conversion(self):
        """
        Check string encodings are converted to expected python type and
        the expected types are "converted" untouched for each string /
        native type value pair.
        """
        field = self.field_class()
        for str_value, py_value in self.str_values:
            self.assertEqual(py_value, field.to_python(py_value))
            self.assertEqual(py_value, field.to_python(str_value))

    def test_invalid_python_conversion(self):
        """
        Check a ValueError is raised for each invalid test value.
        """
        field = self.field_class()
        for value in self.invalid_values:
            with self.assertRaises(ValueError):
                field.to_python(value)

    def test_valid_string_conversion(self):
        """
        Check native python types are converted to proper string
        encoding.
        """
        field = self.field_class()
        for py_value, str_value in self.py_values:
            self.assertEqual(str_value, field.to_string(py_value)) 
            
            
class TestIntField(utils.TestCase, FieldTests):

    field_class = IntField
    str_values = (
        ('123', 123),
    )
    invalid_values = ('invalid', '123.4')
    
    
class TestBoolField(utils.TestCase, FieldTests):

    field_class = BoolField
    str_values = (
        ('True', True),
        ('true', True),
        ('TRUE', True),
        ('1', True),
        ('T', True),
        ('t', True),
        ('Yes', True),
        ('yes', True),
        ('Y', True),
        ('False', False),
        ('false', False),
        ('FALSE', False),
        ('0', False),
        ('F', False),
        ('f', False),
        ('No', False),
        ('no', False),
        ('N', False),
    )
    invalid_values = ('invalid', '2')
    
    
class TestDateTimeField(utils.TestCase, FieldTests):

    field_class = DateTimeField
    str_values = (
        ('1983-01-27 07:15:00', datetime(1983, 1, 27, 7, 15, 0)),
        ('1983-01-27 07:15', datetime(1983, 1, 27, 7, 15, 0)),
        ('1983-01-27', datetime(1983, 1, 27, 0, 0, 0)),
    )
    invalid_values = (
        'invalid',
        '1983-13-27 19:45:00',  # not a valid month
        '1983-01-27 25:12:34',  # not a valid hour
        '1983-01-27 07',        # hour provided but not minutes
    )
    
    
class TestTagField(utils.TestCase, FieldTests):

    field_class = TagField
    str_values = (
        ('one', ['one']),
        ('one, two', ['one', 'two']),
        ('one, two, three', ['one', 'two', 'three']),
        ('numb3r', ['numb3r']),
        ('with-dash', ['with-dash']),
    )
    py_values = (
        (['one'], 'one'),
        (['one', 'two', 'three'], 'one, two, three'),
    )
    invalid_values = (
        'tag with spaces',
        ['valid-tag', 'invalid tag'],
    ) 
