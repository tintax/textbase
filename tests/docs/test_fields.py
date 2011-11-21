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

class FieldTests(utils.TestCase):

    # the type of field under test
    field_class = None

    # the field should be able to successfully convert these to it's
    # native type (n.b. these are only used to check type conversion
    # and not if the value is valid) -- (input, expected output) tuples
    valid_encodings = ()

    # the field should fail to convert these to it's native type
    invalid_encodings = ()

    # these values (native type) should pass validation and be
    # successfully converted to a string representation -- (input,
    # expected output) tuples
    valid_values = ()

    # these values (native type) should fail validation
    invalid_values = ()
    
    def setUp(self):
        if self.field_class:
            self.field = self.field_class()
            self.field.name = 'test'

    def test_convert_valid_encoding_to_native_type(self):
        """
        Check the field can convert valid input types (particularly
        string representations as read from file) to it's native type. 
        """
        for encoding, native_value in self.valid_encodings:
            self.assertEqual(native_value, self.field.to_python(encoding))

    def test_convert_invalid_encoding_to_native_type(self):
        """
        Check the field fails to convert invalid input types to it's
        native type.
        """
        for encoding in self.invalid_encodings:
            with self.assertRaises(ValueError):
                self.field.to_python(encoding)
    
    def test_validate_valid_values(self):
        """
        Check valid values pass the standard validation checks for the
        field.
        """
        for value, encoding in self.valid_values:
            errors = self.field.validate(value)
            self.assertFalse(errors)

    def test_validate_invalid_values(self):
        """
        Check the field fails to validate invalid values.
        """
        for value in self.invalid_values:
            errors = self.field.validate(value)
            self.assertTrue(errors)

    def test_convert_valid_native_type_to_string_encoding(self):
        """
        Check the field can convert from it's native type to a string
        representation (for writing to file).
        """
        for value, encoding in self.valid_values:
            self.assertEqual(encoding, self.field.to_string(value))

    
class TestIntField(FieldTests):

    field_class = IntField

    valid_encodings = (
        ('123', 123),
        )

    invalid_encodings = ('invalid', '123.4')


class TestBoolField(FieldTests):

    field_class = BoolField

    valid_encodings = (
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
        (True, True),
        (False, False),
        )

    invalid_encodings = ('invalid', '2')


class TestDateTimeField(FieldTests):

    field_class = DateTimeField

    valid_encodings = (
        ('1983-01-27 07:15:00', datetime(1983, 1, 27, 7, 15, 0)),
        ('1983-01-27 07:15', datetime(1983, 1, 27, 7, 15, 0)),
        ('1983-01-27', datetime(1983, 1, 27, 0, 0, 0)),
        )

    invalid_encodings = (
        'invalid',
        '1983-13-27 19:45:00',  # not a valid month
        '1983-01-27 25:12:34',  # not a valid hour
        '1983-01-27 07',        # hour provided but not minutes
        )


class TestTagField(FieldTests):

    field_class = TagField

    valid_encodings = (
        ('one', ['one']),
        ('one, two', ['one', 'two']),
        ('one, two, three', ['one', 'two', 'three']),
        ('numb3r', ['numb3r']),
        ('with-dash', ['with-dash']),
        )

    valid_values = (
        (['one'], 'one'),
        (['one', 'two', 'three'], 'one, two, three'),
        (['with-dash'], 'with-dash'),
        )

    invalid_values = (
        ['tag with spaces'],
        ['#hashtag'],
        ) 

class TestUuidField(FieldTests):

    field_class = UuidField

    valid_values = (
        ('e579dd7d-d595-4ea8-bed6-9b025130c471', 'e579dd7d-d595-4ea8-bed6-9b025130c471'),
        ('fe671f59-968e-4f7b-b1bc-d2f0e3f8569c', 'fe671f59-968e-4f7b-b1bc-d2f0e3f8569c'),
        )
    
    invalid_values = (
        'not-the-right-format',
        )
