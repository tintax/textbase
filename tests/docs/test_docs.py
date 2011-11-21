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
import unittest

from textbase.docs import *
from tests import utils

class TestIntegration(utils.TestCase):

    class Person(Document):
        name = TextField()
        age = IntField()
        employed = BoolField()
        married_at = DateTimeField()
        
    def test_new_document(self):
        """
        Create a new document and save to disk.
        """
        person = TestIntegration.Person(name='John Smith')
        person.age = 32
        person.employed = False
        person.married_at = datetime(2011, 11, 13, 13, 30)
        person.write('Hello, John!')
        path = self.mktemp()
        person.save(path)
        self.assertFileContents(path, """
            name: John Smith
            age: 32
            employed: False
            married_at: 2011-11-13 13:30:00
            
            Hello, John!
            """)
        
    def test_existing_document(self):
        """
        Read an existing document from disk.
        """
        path = self.mktemp("""
            name: Jane Doe
            age: 28
            employed: True
            married_at: 2000-01-02 07:10:59
            
            Hello, Jane!
            """)
        person = TestIntegration.Person.open(path)
        self.assertEqual(person.name, 'Jane Doe')
        self.assertEqual(person.age, 28)
        self.assertIs(person.employed, True)
        self.assertEqual(person.married_at, datetime(2000, 1, 2, 7, 10, 59))
        self.assertEqual(person.read(), 'Hello, Jane!\n')
