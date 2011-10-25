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

import unittest

from textbase.docs.core import *

class TestModule(unittest.TestCase):

    def test_set_and_get_values(self):
        """Check field values can be set and then retrieved"""
        
        class Doc(Document):
            foo = Field()
            
        doc = Doc()
        doc.foo = 'bar'
        self.assertEqual(doc.foo, 'bar')

    def test_set_fields_via_doc_constructor_by_position(self):
        """
        Check field values can be set when creating a new document
        instance by providing them as arguments to constructor in
        the same order as the fields are defined for document class.
        """
        class Doc(Document):
            one = Field()
            two = Field()
            three = Field()
            
        doc = Doc('one', 'two', 'three')
        self.assertEqual(doc.one, 'one')
        self.assertEqual(doc.two, 'two')
        self.assertEqual(doc.three, 'three')
        
    def test_set_fields_via_doc_constructor_by_keyword(self):
        """
        Check field values can be set when creating a new document
        instance by providing them as keywords to constructor.
        """
        class Doc(Document):
            one = Field()
            two = Field()
            three = Field()
            
        doc = Doc(three='three', one='one', two='two')
        self.assertEqual(doc.one, 'one')
        self.assertEqual(doc.two, 'two')
        self.assertEqual(doc.three, 'three')
        
    def test_set_fields_via_doc_constructor_by_position_and_keyword(self):
        """
        Check field values can be set when creating a new document
        instance by providing them to constructor as a mix of keywords
        and by position.
        """
        class Doc(Document):
            one = Field()
            two = Field()
            three = Field()
            
        doc = Doc('one', three='three')
        self.assertEqual(doc.one, 'one')
        self.assertEqual(doc.three, 'three')
        
    def test_set_too_many_fields_via_doc_constructor(self):
        """
        Check error is raised if you provide more arguments to document
        constructor than there are fields to set.
        """
        class Doc(Document):
            one = Field()
            two = Field()
            three = Field()
            
        with self.assertRaisesRegexp(TypeError, 'takes 3 arguments'):
            doc = Doc('one', 'two', 'three', 'four')
        
    def test_set_non_existent_field_via_doc_constructor(self):
        """
        Check error is raised if you provide a keyword argument to
        document constructor and no field has that name.
        """
        class Doc(Document):
            one = Field()
            two = Field()
            three = Field()
            
        with self.assertRaisesRegexp(TypeError, 'foo'):
            doc = Doc(foo='bar')
        
    def test_set_same_field_via_doc_constructor_by_position_and_keyword(self):
        """
        Check error is raised if you provide a value for a field by both
        position and keyword argument to the document constructor.
        """
        class Doc(Document):
            one = Field()
            two = Field()
            three = Field()
            
        with self.assertRaisesRegexp(TypeError, 'one'):
            doc = Doc('foo', one='bar')            
