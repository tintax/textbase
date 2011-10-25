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
    
    def __init__(self, initial_value=None):
        """
        initial_value -- Value to set this field to when the associated
                         Document class is instantiated
        """
        self.ordinal = Field.creation_counter = Field.creation_counter + 1
        self.initial_value = initial_value
        self._defaulter = lambda doc: None
        
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
    
    def __init__(self, *args, **kwargs):
        # are there too many arguments?
        if len(args) > len(self._fields):
            msg = '__init__() takes %d arguments at most (%d given)'
            raise TypeError(msg % (len(self._fields), len(args)))

        field_names = [field.name for field in self._fields]
            
        # have arguments been provided for non-existent fields?
        for name in kwargs:
            if name not in field_names:
                msg = "__init__() does not take keyword argument '%s'"
                raise TypeError(msg % name)
       
        # have any fields been defined as both argument and keyword argument?
        for i, name in enumerate(field_names[:len(args)]):
            if name in kwargs:
                msg = "__init__() received multiple values for '%s' argument"
                raise TypeError(msg % name)
            kwargs[name] = args[i]
            
        for field in self._fields:
            if field.name in kwargs:
                setattr(self, field.name, kwargs[field.name])
            else:
                setattr(self, field.name, field.initial_value)
