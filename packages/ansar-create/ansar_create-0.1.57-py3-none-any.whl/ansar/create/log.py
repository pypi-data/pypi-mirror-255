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

"""
"""
__docformat__ = 'restructuredtext'

import sys
import os
import time
from collections import deque

import ansar.encode as ar
from .lifecycle import *
from .pending import *
from .point import *
from .machine import *

__all__ = [
	'PEAK_BEFORE_BLOCKING',
	'LogAgent',
	'log_to_stderr',
	'log_to_nowhere',
	'select_logs',
	'LogToMemory',
]

#
#
PEAK_BEFORE_BLOCKING = 1024 * 32

class LogAgent(Threaded, Stateless):
	"""
	A stateless, async object that accepts PointLog messages originating
	from calls to ``Point.`` ``debug``, ``trace``, ``console``,
	``warning`` and ``fault``, and presents them to a saved method that
	might be the default ``log_to_stderr`` or an application-defined
	method.

	The ``LogAgent`` derives from ``Queue``, i.e. it will enjoy its
	own dedicated thread. The result is that logs can originate from
	any runtime Ansar thread and will be collected/serialized at the
	sole LogAgent instance. The saved log method can enjoy the
	knowledge that all multi-threading issues are resolved and that
	logs are buffered in a reliable and robust fashion.

	A part of delivering on those promises is the custom initialization
	of the underlying Queue object. It is set to blocking of upstream
	sources and the size of the Queue is set to a generous, custom
	value.

	Note the complete disabling of all logging for ``LogAgent``. It
	doesnt make much sense for the logger to log to itself and
	certainly not during creation where at some point it exists
	but is not yet entered into Ansar tables. At such a moment
	send would fail - at best.
	"""

	def __init__(self, method):
		Threaded.__init__(self, blocking=True, maximum_size=PEAK_BEFORE_BLOCKING)
		Stateless.__init__(self)
		self.method = method
		self.tap = []

def LogAgent_Start(self, message):
	pass

def LogAgent_PointLog(self, message):
	try:
		line = self.method(message)
	except Exception as e:
		s = str(e)
		return
	t = TapLine(line)
	for a in self.tap:
		self.send(t, a)

def LogAgent_RedirectLog(self, message):
	redirect = message.redirect
	try:
		redirect.from_previous(self.method)
	except AttributeError:
		pass
	self.method = redirect

def LogAgent_OpenTap(self, message):
	self.tap.append(self.return_address)

def LogAgent_CloseTap(self, message):
	try:
		self.tap.remove(self.return_address)
	except ValueError:
		pass

def LogAgent_Enquiry(self, message):
	"""
	A query from the ``tear_down`` function to ensure that all previous
	messages have been processed.
	"""
	self.reply(Ack())

def LogAgent_Stop(self, message):
	self.complete()

LOG_AGENT_DISPATCH = (Start,
	PointLog, RedirectLog,
	OpenTap, CloseTap,
	Enquiry, Stop)

bind_stateless(LogAgent, dispatch = LOG_AGENT_DISPATCH,
	lifecycle=False, message_trail=False,
	execution_trace=False, user_logs=ar.USER_LOG_NONE)

#
#
PID = os.getpid()

def log_to_stderr(log):
	second = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(log.stamp))
	fraction = '%.3f' % (log.stamp,)
	fraction = fraction[-3:]
	mark = '%s.%s' % (second, fraction)
	name = log.name.split('.')[-1]
	state = log.state
	if state is None:
		p = '[%08d] %s %s <%08x>%s - %s\n' % (PID, mark, log.tag, log.address[-1], name, log.text)
	else:
		p = '[%08d] %s %s <%08x>%s[%s] - %s\n' % (PID, mark, log.tag, log.address[-1], name, state, log.text)
	sys.stderr.write(p)
	sys.stderr.flush()

#
#
def log_to_nowhere(log):
	pass

def select_logs(number):
	def log_by_number(log):
		n = ar.tag_to_number(log.tag)
		if number > n:
			return
		log_to_stderr(log)
	return log_by_number

#
#
class LogToMemory(object):
	"""
	"""
	def __init__(self, lines=1000):
		self.lines = lines
		self.memory = deque()

	def __call__(self, log):
		"""
		"""
		self.memory.append(log)
		while len(self.memory) > self.lines:
			self.memory.popleft()
		return None

import logging

class LogToLogger(object):
	"""
	Constructs a callable object that formats then logs via a standard
	``logging.Logger``, suitable for using as a log_routine parameter to
	``root_object``.

	Example::

	>>> mylog = ml.LogToLogger(logging.getLogger('logger.name'))
	>>> root = ml.root_object(log_routine=mylog)
	"""
	def __init__(self, log):
		if not isinstance(log, logging.Logger):
			raise ValueError("%r is not a logging.Logger or subclass" % (log,))

		self.log = log

	def __call__(self, log):
		"""
		Implement a callable so this object can be used as a function.

		Should implement the same interface as the ``log_to_stderr``
		function.
		"""
		tag = log.tag
		name = log.name.split('.')[-1]
		state = log.state
		if state is None:
			line = '[%s]<%08x>%s - %s' % (tag, log.address[-1], name, log.text)
		else:
			line = '[%s]<%08x>%s[%s] - %s' % (tag, log.address[-1], name, state, log.text)
		if tag[1] == ar.TAG_FAULT:
			self.log.critical(line)
		elif tag[1] == ar.TAG_WARNING:
			self.log.warning(line)
		elif tag[1] == ar.TAG_CONSOLE:
			self.log.info(line)
		elif tag[1] == ar.TAG_TRACE:
			self.log.info(line)
		elif tag[1] == ar.TAG_DEBUG:
			self.log.debug(line)
		else:
			self.log.info(line)
		return line
