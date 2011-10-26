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
            
        with self.assertRaisesRegexp(InvalidDocument, 'takes 3 arguments'):
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
            
        with self.assertRaisesRegexp(InvalidDocument, 'foo'):
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
            
        with self.assertRaisesRegexp(InvalidDocument, 'one'):
            doc = Doc('foo', one='bar')  

    def test_catch_multiple_exceptions_via_doc_constructor(self):
        """
        """
        class Doc(Document):
            one = Field()
            two = Field()
            three = Field()
            
        with self.assertRaises(InvalidDocument) as cm:
            doc = Doc('one', 'two', 'three', 'four', two='foo')
            
        self.assertEqual(len(cm.exception.args), 2)
        self.assertIsInstance(cm.exception.args[0], Error)
        self.assertIsInstance(cm.exception.args[1], Error)
            
    def test_set_field_to_initial_value_if_not_explicitly_set(self):
        """
        Check field is set to an initial value (which defaults to None)
        if no explicit value is passed to the document constructor.
        """
        class Doc(Document):
            foo = Field(initial_value='bar')
            absent = Field()
            
        doc = Doc()
        self.assertEqual(doc.foo, 'bar')
        self.assertIsNone(doc.absent)
        
    def test_calculate_default_value_for_field_with_no_value(self):
        """
        Check that a field attempts to calculate a default value when
        no value (including an initial value) has been set if the
        document has a suitable function to do so.
        """
        class Doc(Document):
            title = Field(initial_value='Untitled')
            url = Field()
            
            @url.defaulter
            def get_default_url(self):
                return self.title.lower()
                
        doc = Doc()
        self.assertEqual(doc.url, 'untitled')
        doc.title = 'FooBar'
        self.assertEqual(doc.url, 'foobar')
