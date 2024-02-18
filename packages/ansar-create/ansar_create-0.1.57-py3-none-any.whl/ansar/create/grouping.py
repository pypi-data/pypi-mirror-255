# Author: Scott Woods <scott.18.ansar@gmail.com.com>
# MIT License
#
# Copyright (c) 2017-2023 Scott Woods
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

""".

.
"""

__docformat__ = 'restructuredtext'

import ansar.encode as ar
#from .space import Completion

__all__ = [
	'GroupRun',
]

#
#
class GroupRun(object):
	def __init__(self, home=None, role=None, start=None, stop=None, seconds=None, completed=None):
		self.home = home
		self.role = role or ar.default_vector()
		self.start = start
		self.stop = stop
		self.seconds = seconds
		self.completed = completed or ar.default_map()

GROUP_RUN_SCHEMA = {
	"home": ar.Unicode(),
	"role": ar.VectorOf(ar.Unicode()),
	"start": ar.WorldTime(),
	"stop": ar.WorldTime(),
	"seconds": ar.Float8(),
	"completed": ar.MapOf(ar.Unicode(), ar.Any()),
}

ar.bind(GroupRun, object_schema=GROUP_RUN_SCHEMA)
