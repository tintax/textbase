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

from textbase.docs.fields import *
from tests import utils

class FieldTests(object):

    field_class = None
    values = ()  # (string, python) tuples
    invalid_values = ()
    
    def test_valid_python_conversion(self):
        """
        Check string encodings are converted to expected python type and
        the expected types are "converted" untouched for each string /
        native type value pair.
        """
        field = self.field_class()
        for str_value, py_value in self.values:
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
            
            
class TestIntField(utils.TestCase, FieldTests):

    field_class = IntField
    values = (
        ('123', 123),
    )
    invalid_values = ('invalid', '123.4')
    
    
class TestBoolField(utils.TestCase, FieldTests):

    field_class = BoolField
    values = (
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
