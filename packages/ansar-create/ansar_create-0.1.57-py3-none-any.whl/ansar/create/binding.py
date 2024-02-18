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
__docformat__ = 'restructuredtext'

import types

from ansar.encode import CodingProblem, bind_message, is_message_class
from .point import *
from .pending import Machine
from .machine import *

__all__ = [
	'bind_any',
]


def bind_any(object_type, *args, **kw_args):
	"""
	Forwards all arguments on to a custom bind function
	according to the type of the first argument.

	Refer to **ansar.encode** for registration of messages;

	- :func:`~.point.bind_function`
	- :func:`~.machine.bind_stateless`
	- :func:`~.machine.bind_statemachine`

	:param object_type: type of async entity
	:type object_type: message class, function or Point-based class
	:param args: arguments passed to the object instance
	:type args: positional argument tuple
	:param kw_args: named arguments passed to the object instance
	:type kw_args: named arguments dict
	"""
	# Damn line length constraint.
	cp1 = 'cannot bind %r; unknown machine type'
	if isinstance(object_type, types.FunctionType):
		bind_function(object_type, *args, **kw_args)
	elif issubclass(object_type, Point):
		if issubclass(object_type, Machine):
			if issubclass(object_type, Stateless):
				bind_stateless(object_type, *args, **kw_args)
			elif issubclass(object_type, StateMachine):
				bind_statemachine(object_type, *args, **kw_args)
			else:
				raise CodingProblem(cp1 %
						(object_type,))
		else:
			bind_point(object_type, *args, **kw_args)
	elif not is_message_class(object_type):
		bind_message(object_type, *args, **kw_args)
