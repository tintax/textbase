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

from datetime import timedelta
import os
import shutil
import tempfile
import textwrap
import unittest

class TestCase(unittest.TestCase):

    def dedent(self, text):
        """
        Remove common leading whitespace from every line in text, strip
        any leading newline, and add a trailing newline if neccesary.
        """
        text = textwrap.dedent(text)
        if text.startswith('\n'):
            text = text.lstrip()
        if not text.endswith('\n'):
            text = text + '\n'
        return text

    def mkdtemp(self):
        """
        Create a temporary directory and return the absolute path to the
        new directory. The directory will be deleted after the current
        test is completed.
        """
        path = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, path)
        return path

    def mktemp(self, contents=None, dedent=True, directory=None):
        """
        Create a temporary file within the specified directory and
        return the absolute path to the new file. The file will be
        deleted after the current test is completed.
        
        contents -- write contents to the new file if supplied
        dedent -- dedent contents before writing to file?
        directory -- where to create the new file (create a temporary
                     directory if None)
        """
        if not directory:
            directory = self.mkdtemp()
        fd, path = tempfile.mkstemp(dir=directory)
        if contents:
            if dedent:
                contents = self.dedent(contents)
            os.write(fd, contents)
        os.close(fd)
        self.addCleanup(os.remove, path)
        return path
        
    def assertFileContents(self, path, text):
        """
        Assert the contents of the file at the specified path is equal
        to the supplied text.
        """
        text = self.dedent(text)
        with open(path, 'r') as stream:
            self.assertEqual(stream.read(), text)
            
    def assertTimeGap(self, time1, time2, delta):
        """
        Assert the difference between time1 and time2 is within delta
        seconds.
        """
        if time1 < time2:
            self.assertLess(time2 - time1, timedelta(seconds=delta))
        else:
            self.assertLess(time1 - time2, timedelta(seconds=delta))
