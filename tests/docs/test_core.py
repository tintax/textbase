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

import os.path
import shutil
import tempfile
import textwrap
import unittest

from textbase.docs.core import *

class TestModule(unittest.TestCase):

    def create_temp_file(self, text):
        """
        Create temporary file with the contents of the supplied string
        and return the path. The file will be deleted when the test
        ends.
        """
        text = textwrap.dedent(text)
        if text.startswith('\n'):
            text = text.lstrip()
        if not text.endswith('\n'):
            text = text + '\n'
        temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, temp_dir)
        path = os.path.join(temp_dir, 'temp.txt')
        with open(path, 'w') as stream:
            stream.write(text)
        return path

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
        
    def test_field_validator(self):
        """
        Check we can define a validation function for a field on the
        containing document - and this is evaluated during validation.
        """
        class Doc(Document):
            title = Field()
            
            @title.validator
            def validate_title_is_at_least_six_characters(value):
                if len(value) < 6:
                    raise ValueError('not six chars')
                    
        doc = Doc(title='1234567')
        doc.validate()  # no exceptions raised
        doc.title = '123'
        with self.assertRaises(InvalidDocument) as cm:
            doc.validate()
        # exception should consist of a single ValidationError for
        # the title field
        self.assertEqual(len(cm.exception.args), 1)
        self.assertIsInstance(cm.exception.args[0], ValidationError)
        self.assertEqual(cm.exception.args[0].field, 'title')
        self.assertEqual(cm.exception.args[0].msg, 'not six chars')
        
    def test_multiple_field_validators(self):
        """
        Check we can define multiple validators - and each is evaluated
        (regardless of previous results).
        """
        class Doc(Document):
            title = Field()
            
            @title.validator
            def validate_title_is_at_least_six_characters(value):
                if len(value) < 6:
                    raise ValueError('not six chars')
                    
            @title.validator
            def validate_title_is_alphabetic(value):
                if not value.isalpha():
                    raise ValueError('not alphabetic')
                    
        doc = Doc('123')
        with self.assertRaises(InvalidDocument) as cm:
            doc.validate()
        # exception should consist of two ValidationError objects
        self.assertEqual(len(cm.exception.args), 2)
        self.assertIsInstance(cm.exception.args[0], ValidationError)
        self.assertIsInstance(cm.exception.args[1], ValidationError)
        
    def test_required_field_is_set(self):
        """
        Check a required field without a value fails validation.
        """
        class Doc(Document):
            foo = Field(required=True)
            
        doc = Doc()
        with self.assertRaises(InvalidDocument):
            doc.validate()
            
    def test_open_document_consisting_of_single_attribute(self):
        """
        Check a document can be read from a file containing a single
        attribute.
        """
        class Doc(Document):
            foo = Field()
            
        path = self.create_temp_file("""
            foo: bar
            """)
        doc = Doc.open(path)
        self.assertEqual(doc.foo, 'bar')
        
    def test_open_document_consisting_of_folded_attributes(self):
        """
        Check a document can be read from a file containing folded
        attributes (i.e. attributes whose values span more than one
        line).
        """
        class Doc(Document):
            foo = Field()
            bar = Field()
            
        path = self.create_temp_file("""
            foo: line one
                line two
                line three
            bar: line one
              line two
              line three
            """)
        doc = Doc.open(path)
        self.assertEqual(doc.foo, 'line one line two line three')
        self.assertEqual(doc.bar, 'line one line two line three')

