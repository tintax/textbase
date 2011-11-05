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
from tests import utils

class TestModule(utils.TestCase):

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
            
        path = self.mktemp("""
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
            
        path = self.mktemp("""
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

    def test_read_and_write_new_document(self):
        """
        Check new Document objects are created with an empty body and
        this can be replaced with a new one.
        """
        class Doc(Document):
            foo = Field()
            
        doc = Doc()
        self.assertEqual(doc.read(), '')
        doc.write('line one\nline two\n')
        self.assertEqual(doc.read(), 'line one\nline two\n')
        
    def test_read_existing_document(self):
        """
        Check body can be read from an existing document.
        """
        class Doc(Document):
            foo = Field()
            
        path = self.mktemp("""
            foo: bar
            
            This body spans
            multiple lines.
            """)
        doc = Doc.open(path)
        self.assertEqual(doc.read(), 'This body spans\nmultiple lines.\n')
        
    def test_read_existing_document_with_no_body(self):
        """
        Check an empty body is read from an existing document without
        any body text.
        """
        class Doc(Document):
            foo = Field()
            
        path = self.mktemp('foo: bar')
        doc = Doc.open(path)
        self.assertEqual(doc.read(), '')
        
    def test_save_new_document(self):
        """
        Check a new document is saved to disk with the attributes in the
        right order, attributes wrapped to lines of 72 characters, and
        the body seperated from the header by a blank line.
        """
        class Doc(Document):
            subject = Field()
            foo = Field()
            bar = Field()
            
        doc = Doc(foo='bar', bar='foo')
        doc.subject = 'This subject will be too long to write to the file'
        doc.subject = doc.subject + ' without being wrapped at the 72'
        doc.subject = doc.subject + ' character mark (without chopping words)'
        doc.subject = doc.subject + ' so this will use three lines'
        doc.write('line one\nline two\nline three\n')
        path = self.mktemp()
        doc.save(path)
        self.assertEqual(doc.path, path)
        self.assertFileContents(path, """
            subject: This subject will be too long to write to the file without
                being wrapped at the 72 character mark (without chopping words) so
                this will use three lines
            foo: bar
            bar: foo
            
            line one
            line two
            line three
            """)

    def test_save_existing_unmodified_document_to_same_file(self):
        """
        Check calling save() on an unmodified document leaves the file
        unchanged.
        """
        class Doc(Document):
            foo = Field()
            bar = Field()
            
        text = """
            foo: bar
            bar: foo
            
            Hello, World!
            """
        path = self.mktemp(text)
        doc = Doc.open(path)
        doc.save()
        self.assertEqual(doc.path, path)
        self.assertFileContents(path, text)
        
    def test_save_existing_unmodified_document_to_new_file(self):
        """
        Check an existing document can be written to a new file.
        """
        class Doc(Document):
            foo = Field()
            bar = Field()
            
        text = """
            foo: bar
            bar: foo
            
            Hello, World!
            """
        old_path = self.mktemp(text)
        doc = Doc.open(old_path)
        new_path = self.mktemp()
        doc.save(new_path)
        self.assertEqual(doc.path, new_path)
        self.assertFileContents(new_path, text)

    def test_save_document_without_body(self):
        """
        Check a document without any body can be saved and the resulting
        file ends immediately after the header.
        """
        class Doc(Document):
            foo = Field()
            
        doc = Doc(foo='bar')
        path = self.mktemp()
        doc.save(path)   
        self.assertFileContents(path, 'foo: bar')
            
    def test_unset_fields_are_ignored_when_saving_documents(self):
        """
        Check fields for which a value has not been set (including those
        with a default value) are not written out to the file when the
        document is saved.
        """
        class Doc(Document):
            foo = Field(initial_value='bar')
            bar = Field()
            
            @bar.defaulter
            def get_bar_default_value(self):
                return self.foo + '2'
                
        doc = Doc()
        self.assertEqual(doc.foo, 'bar')  # is set so should be saved
        self.assertEqual(doc.bar, 'bar2')  # is calculated so shouldn't be
        path = self.mktemp()
        doc.save(path)   
        self.assertFileContents(path, """
            foo: bar
            """)     
