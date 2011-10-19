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
    pass
    

class Document(object):
    """
    Represents a block of plain text and any associated properties
    (fields). Documents are defined by subclassing Document and
    attaching Field instances to represent the properties, for instance:
    
        class MyDoc(Document):
        
            my_field = Field()
    """
    pass
