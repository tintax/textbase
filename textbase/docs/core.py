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

from __future__ import unicode_literals

import email.parser
import io
import textwrap

import validators

class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class ValidationError(Error):
    """Raised when a validation check fails."""

    def __init__(self, field, msg):
        self.field = field
        self.msg = msg
    
    def __str__(self):
        return '[%s] %s' % (self.field, self.msg)
        
    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.field, self.msg)
    
    
class InvalidDocument(Error):
    """
    Raised when a document is (or would be created in) an invalid
    state.
    
    N.B. This should be instantiated with either a single string
    argument (a useful and human readable message about the error) or
    multiple arguments that can be stringified (e.g. other exceptions)
    if there are multiple reasons why the document is invalid.
    """
    pass
    

class Field(object):
    """
    Represents a document property. Instances should be attached to
    Document subclasses as attributes.
    """

    class Attribute(object):
        """
        Descriptor to manage assigning and retrieving field values.
        """
        
        def __init__(self, field):
            """
            field -- The field object to manage
            """
            self.field = field
            
        def __get__(self, document, owner):
            """
            Return the current value for the managed field on the
            specified Document object. Return a default value (which is
            recalculated on each access) if no value has been set.
            """
            if not document:
                # trying to access Field object rather than the value
                # of the field for a particular document
                return self.field
            value = document.__dict__.get(self.field.name, None)
            if value is None:
                value = self.field.default_value(document)
            return value
            
        def __set__(self, document, value):
            """
            Assign the specified value for the managed field on the
            specified Document object.
            """
            document.__dict__[self.field.name] = value

    # if we increment this when Field objects are created then we can
    # track the relative order they are created in: which is also the
    # order they are "declared" on (attached to) a document class
    creation_counter = 0
    
    def __init__(self, initial_value=None, required=False):
        """
        initial_value -- Value to set this field to when the associated
                         Document class is instantiated
        required -- Does this field require a value for the document to
                    be valid?
        """
        self.ordinal = Field.creation_counter = Field.creation_counter + 1
        self.initial_value = initial_value
        self.required = required
        self._defaulter = lambda doc: None
        self._validators = []
        if self.required:
            self._validators.append(validators.required)
        
    def attach_to_class(self, cls, name):
        """
        Set the name of the attribute by which this field is attached to
        a Document class.
        """
        self.name = name
        # use an Attribute to manage assigning and retrieving values
        setattr(cls, name, Field.Attribute(self))

    def defaulter(self, function):
        """
        Set the function used to generate a default value. The specified
        function will be passed the Document instance and may refer to
        other properties of that document (e.g. a "title" field which
        defaults to a modified version of a "url" field).
        
        N.B. This is intended to be used as a decorator on the attached
        Document (e.g. @name_of_field.defaulter).
        """
        self._defaulter = function
        return function
        
    def default_value(self, document):
        """
        Return the default value for this field on the specified
        Document.
        """
        return self._defaulter(document)

    def validator(self, function):
        """
        Add a function to the set used to validate fields. The specified
        function will be passed the candidate value and should raise a
        ValueError if it cannot be validated.
        """
        self._validators.append(function)
        
    def validate(self, value):
        """
        Check the specified value is valid for this field. Raise a
        ValidationError if not.
        """
        errors = []
        for validator in self._validators:
            try:
                validator(value)
            except ValueError as e:
                errors.append(ValidationError(self.name, str(e)))
        return errors
        

class DocumentType(type):
    """
    Manages the creation of Document classes to consolidate the links
    between each class and it's Field objects.
    """

    def __init__(cls, name, bases, attributes):
        """
        Add a list of the attached fields in the same order as declared
        on the class. Provide each field with the name of the attribute
        by which it is attached to the class.
        """
        cls._fields = []
        for name, attribute in attributes.items():
            if hasattr(attribute, 'attach_to_class'):
                attribute.attach_to_class(cls, name)
                cls._fields.append(attribute)
        cls._fields.sort(key=lambda field: field.ordinal)
    

class Document(object):
    """
    Represents a block of plain text and any associated properties
    (fields). Documents are defined by subclassing Document and
    attaching Field instances to represent the properties, for instance:
    
        class MyDoc(Document):
        
            my_field = Field()
    """

    __metaclass__ = DocumentType

    @classmethod
    def open(cls, path):
        """
        Create and return a Document object from the file at the
        specified path. Raise an InvalidDocument exception if the file
        cannot be parsed.
        """
        def unfold(value):
            return_value = ''
            iterator = iter(value)
            for char in iterator:
                if char == '\n':
                    while char in ' \t\n':
                        char = iterator.next()
                    return_value = return_value + ' '
                return_value = return_value + char
            return return_value
            
        with open(path, 'r') as stream:
            msg = email.parser.Parser().parse(stream)
        kwargs = dict((k, unfold(v)) for k, v in msg.items())
        document = cls(**kwargs)
        document._path = path
        document._body = None
        return document
    
    def __init__(self, *args, **kwargs):
        errors = []
    
        # are there too many arguments?
        if len(args) > len(self._fields):
            msg = '__init__() takes %d arguments at most (%d given)'
            errors.append(Error(msg % (len(self._fields), len(args))))

        field_names = [field.name for field in self._fields]
            
        # have arguments been provided for non-existent fields?
        for name in kwargs:
            if name not in field_names:
                msg = "__init__() does not take keyword argument '%s'"
                errors.append(Error(msg % name))
       
        # have any fields been defined as both argument and keyword argument?
        for i, name in enumerate(field_names[:len(args)]):
            if name in kwargs:
                msg = "__init__() received multiple values for '%s' argument"
                errors.append(Error(msg % name))
            kwargs[name] = args[i]
            
        for field in self._fields:
            if field.name in kwargs:
                setattr(self, field.name, kwargs[field.name])
            else:
                setattr(self, field.name, field.initial_value)
                
        if errors:
            raise InvalidDocument(*errors)
        
        self._path = None    
        self._body = ''

    @property
    def path(self):
        return self._path

    def read(self):
        """
        Read and return all text from the body until EOF is reached.
        """
        if not self._body is None:
            return unicode(self._body)
        with io.open(self.path, 'r') as stream:
            for line in stream:
                if line.strip() == '':
                    break
            return stream.read()
            
    def write(self, text):
        """
        Set the body to the supplied text.
        
        N.B. The body is not written to disk (if the document was
        opened from a file) until the document is saved.
        """
        self._body = text
            
    def validate(self):
        """
        Check the current state represents a valid document. This
        includes running the field validation checks.
        
        Raise an InvalidDocument error if the document cannot be
        validated.
        """
        errors = []
        for field in self._fields:
            errors.extend(field.validate(getattr(self, field.name)))
        if errors:
            raise InvalidDocument(*errors)

    def save(self, path=None):
        """
        Save the document to disk. Use the supplied path if provided or
        the existing path if not. Fields are written to the file in the
        same order as defined on the Document. Only fields with an
        explicit value are written to the file.
        
        Raise a ValueError if a path is not provided and isn't already
        set on the document.
        """
        if not path:
            path = self.path
        if not path:
            raise ValueError('path required')
        wrapper = textwrap.TextWrapper(width=72, subsequent_indent='    ')
        body = self.read()
        with io.open(path, 'w') as stream:
            for field in self._fields:
                value = self.__dict__.get(field.name)
                if value is not None:
                    line = '%s: %s' % (field.name, value)
                    stream.write(unicode(wrapper.fill(line)) + '\n')
            if body:
                stream.write('\n')
                stream.write(body)
                if not body.endswith('\n'):
                    stream.write('\n')
        self._path = path
