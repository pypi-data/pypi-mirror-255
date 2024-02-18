# Author: Scott Woods <scott.18.ansar@gmail.com.com>
# MIT License
#
# Copyright (c) 2017 Scott Woods
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

"""Definition of the fundamental async object.

Async objects are created and then send messages to each other. There are
also timers to implement, and automated logging. There is also assistance
for managing async scenarios.
"""

__docformat__ = 'restructuredtext'

import os
import inspect
from time import time, monotonic
from copy import deepcopy
import types
from collections import deque

import ansar.encode as ar
from .space import *
from .pending import PEAK_BEFORE_DROPPED, Queue, Machine, Dispatching, Buffering
from .lifecycle import *

__all__ = [
	'pt',
	'Point',
	'completed_object',
	'T1', 'T2', 'T3', 'T4',
	'StartTimer',
	'CancelTimer',
	'PointLog',
	'RedirectLog',
	'OpenTap',
	'CloseTap',
	'TapLine',
	'Threaded',
	'Channel',
	'object_dispatch',
	'bind_point',
	'bind_function',
	'halt',
	'AutoStop',
]

#
#
pt = ar.Gas(log_address=NO_SUCH_ADDRESS,
	timer_address=NO_SUCH_ADDRESS,
	test_address=NO_SUCH_ADDRESS,
	thread_classes={})

# TIMERS - point.start() and point.cancel()
# Timers for general use.
class T1(object):
	"""Predeclared timer class.

	A class suitable for passing to Point.start(). The library
	provides the T1, T2, T3 and T4 timer classes for general use.
	"""
	pass

class T2(object):
	pass

class T3(object):
	pass

class T4(object):
	pass

ar.bind_message(T1, copy_before_sending=False)
ar.bind_message(T2, copy_before_sending=False)
ar.bind_message(T3, copy_before_sending=False)
ar.bind_message(T4, copy_before_sending=False)

class StartTimer(object):
	"""Message from point to clock service, requesting a timer."""
	def __init__(self, timer=None, seconds=1, repeating=False):
		self.timer = timer
		self.seconds = seconds
		self.repeating = repeating

TIMER_SCHEMA = {
	'timer': ar.Type,
	'seconds': ar.Float8,
	'repeating': ar.Boolean,
}

class CancelTimer(object):
	"""Message from point to clock service, canceling a pending timer."""
	def __init__(self, timer=None):
		self.timer = timer

ar.bind_message(StartTimer, object_schema=TIMER_SCHEMA, copy_before_sending=False)
ar.bind_message(CancelTimer, object_schema=TIMER_SCHEMA, copy_before_sending=False)

# LOGGING - point.log(), point.console().... point.fault()
# The object that is pumped out from active async objects and needs to
# find a console/window/file/db somewhere.
class PointLog(object):
	"""Object that records a moment in time and other details.

	:param stamp: the moment the log was created
	:type stamp: epoch float
	:param tag: an enumeration of the log level
	:type tag: a single-character string
	:param address: address of the async object
	:type address: tuple of int
	:param name: name of the class or function.
	:type name: str
	:param state: name of the current FSM state or None
	:type state: str
	:param text: free format text
	:type text: str
	"""
	def __init__(self, stamp=0.0, tag=None, address=None, name=None, state=None, text=None):
		self.stamp = stamp
		self.tag = tag
		self.address = address or ar.NO_SUCH_ADDRESS
		self.name = name
		self.state = state
		self.text = text

POINT_LOG_SCHEMA = {
	'stamp': ar.Float8,	# struct_time tuple of 9 integers. UTC, [8](isdst) always 0.
	'tag': ar.String,
	'address': ar.VectorOf(ar.Integer8),	# TBD (all addresses must be lists!!!! not tuples) Prevent manipulation by endpoints.
	'name': ar.String,
	'state': ar.String,
	'text': ar.String,
}

ar.bind_message(PointLog, object_schema=POINT_LOG_SCHEMA, copy_before_sending=False,
	message_trail=False, execution_trace=False)

#
#
class PointTest(object):
	"""Results of a Point.test().

	Captures the details of a check on runtime values.

	:param stamp: the moment the test was performed
	:type stamp: epoch float
	:param name: name of the class or function
	:type name: str
	:param condition: pass or fail
	:type condition: bool
	:param source: name of the module containing the test
	:type source: str
	:param line: line in the module
	:type line: int
	:param text: free format text
	:type text: str
	"""
	def __init__(self, stamp=None, name=None, condition=None, source=None, line=None, text=None):
		self.stamp = stamp
		self.name = name
		self.condition = condition
		self.source = source
		self.line = line
		self.text = text

POINT_TEST_SCHEMA = {
	'stamp': ar.WorldTime,
	'name': ar.Unicode,
	'condition': ar.Boolean,
	'source': ar.Unicode,
	'line': ar.Integer8,
	'text': ar.Unicode,
}

ar.bind_message(PointTest, object_schema=POINT_TEST_SCHEMA, copy_before_sending=False,
	message_trail=False, execution_trace=False)

#
#
class RedirectLog(object):
	def __init__(self, redirect=None):
		self.redirect = redirect

ar.bind_message(RedirectLog, not_portable=True,
	message_trail=False, execution_trace=False, copy_before_sending=False)

#
#
class OpenTap(object):
	pass

class CloseTap(object):
	pass

class TapLine(object):
	def __init__(self, line=None):
		self.line = line

ar.bind_message(OpenTap, copy_before_sending=False)
ar.bind_message(CloseTap, copy_before_sending=False)
ar.bind_message(TapLine, object_schema={'line': ar.String}, copy_before_sending=False,
	message_trail=False, execution_trace=False)

#
#
def check_line():
	s = inspect.stack()[2]
	sf = s[1]	# Source file.
	ln = s[2]	# Line number.
	fn = s[3]	# Function name.
	if sf.find('tmp') == 1:
		_, sf = os.path.split(sf)
	if '<module>' in fn:
		fn = None
	return sf, ln, fn

#
#
def completed_object(value, parent, address):
	send_a_message(Completed(value), parent, address)

class Point(object):
	"""The essential async object.

	Methods of this class are the user entry-point for SDL primitives such
	as send() and start(). There are also methods associated with logging
	and child object management.
	"""
	def __init__(self):
		self.address = ar.NO_SUCH_ADDRESS			  # Identity of this object.
		self.queue_address = ar.NO_SUCH_ADDRESS		# Where are messages processed.
		self.parent_address = ar.NO_SUCH_ADDRESS	   # Who created this object.
		self.to_address = ar.NO_SUCH_ADDRESS		   # Delivery address on current message.
		self.return_address = ar.NO_SUCH_ADDRESS	   # Who sent the current message.
		self.assigned_queue = None					 # Parent queue for non-threaded machine.
		self.object_ending = None

		self.current_state = None
		self.previous_message = None

		self.address_job = {}

	def abdicate_to(self, address):
		a = self.address
		self.address = abdicate_to_address(self.address, address)
		return a

	def discard(self, address):
		discard_address(address)

	def create(self, object_type, *args, object_ending=completed_object, **kw):
		"""Create a child instance of `object_type`. Return the address of the new object.

		:param object_type: async type to instantiate
		:type object_type: function or Point-based class
		:param args: arguments passed to the new object
		:type args: positional arguments tuple
		:param kw: arguments passed to the new object
		:type kw: name arguments dict
		:rtype: an ansar address or the actual object (e.g. Channel)
		"""
		return create_a_point(object_type, object_ending, self.address, args, kw)

	# Communications helpers.
	#
	def send(self, m, to):
		"""Transfer a message to an address.

		Message delivery is not guaranteed and non-delivery is not
		notified. There are multiple reasons delivery can fail, e.g. the
		destination address no longer exists. Unless the reason is a
		fault within the sending machinery, failure to deliver is not
		considered an error. Refer to application logs for details on
		why a particular message failed to reach its intended
		destination.

		A copy of the message is taken for every actual transfer, i.e.
		by default remote objects always receive a copy of the message
		originally presented to ``send()``. Obviously this is behaviour
		motivated by the multi-threaded runtime context but where it
		is deemed unnecessary, copying can be disabled on a per-message-type
		basis. :func:`~.bind.bind_any` for more details.

		:param m: the message to be sent
		:type m: instance of a registered message
		:param to: the intended receiver of the message
		:type to: ansar address
		"""
		pf = self.__art__   # Access starting at instance allows overlay (i.e. functions).
		mf = m.__art__	  # Could go direct to __class__.
		if pf.message_trail and mf.message_trail:
			self.log(ar.TAG_SENT, 'Sent %s to <%08x>' % (mf.name, to[-1]))
		if mf.copy_before_sending:
			c = deepcopy(m)
			send_a_message(c, to, self.address)
			return
		send_a_message(m, to, self.address)

	def reply(self, m):
		"""Send a response to the sender of the current message.

		This is a shorthand for ``self.send(m, self.return_address)``. Reduces
		keystrokes and risk of typos.

		:param m: the message to be sent
		:type m: instance of a registered message
		"""
		self.send(m, self.return_address)

	def forward(self, m, to, return_address):
		"""Send a message to an address, as if it came from a 3rd party.

		Send a message but override the return address with the address of
		another arbitrary object. To the receiver the message appears to
		have come from the arbitrary object.

		Useful when building relationships between objects. This allows objects
		to "drop out" of 3-way conversations, leaving simpler and faster 2-way
		conversations behind.

		:param m: the message to send
		:type m: instance of a registered message
		:param to: the intended receiver of the message
		:type to: ansar address
		:param return_address: the other object
		:type return_address: ansar address
		"""
		pf = self.__art__
		mf = m.__art__
		if pf.message_trail and mf.message_trail:
			self.log(ar.TAG_SENT, 'Forward %s to <%08x> (from <%08x>)' % (mf.name, to[-1], return_address[-1]))
		if mf.copy_before_sending:
			c = deepcopy(m)
			send_a_message(c, to, return_address)
			return
		send_a_message(m, to, return_address)

	def advise(self, m):
		"""Send a message to the parent of this object.

		:param m: the message to be sent
		:type m: instance of a registered message
		"""
		self.send(m, self.parent_address)

	def start(self, timer, seconds, repeating=False):
		"""Start the specified timer for this object.

		An instance of the timer class will be sent to this address after the
		given number of seconds. Any registered message can be used as a timer.
		Ansar provides the standard timers T1, T2, T3, and T4 for convenience
		and to reduce duplication.

		Timers are private to each async object and there is no limit to the
		number of pending timers an object may have. Starting a timer with the
		same class is not an error, the timeout for that timer is reset to the
		new number of seconds. It is also not an error to terminate an object
		with outstanding timers - they fall on the floor.

		It is difficult to make guarantees about the order that messages will
		arrive at an object. In the case of timers, its possible to receive
		the timeout after the sending of a cancellation. Async objects are best
		written to cope with every possible receive ordering.

		:param timer: the type of the object that will be sent back on timeout
		:type timer: a registered class
		:param seconds: time span before expiry
		:type seconds: float
		"""
		self.send(StartTimer(timer, seconds, repeating), pt.timer_address)

	def cancel(self, timer):
		"""Abort the specified timer for this object.

		Discard the pending timer. It is not an error to find that there is
		no such pending timer. The timeout can still be received after a
		cancellation.

		:param timer: the pending timer
		:type timer: a registered class
		"""
		self.send(CancelTimer(timer), pt.timer_address)

	def complete(self, value=None):
		"""Cause an immediate termination. The method never returns.

		:param value: value to be returned to parent.
		:type value: any
		"""
		raise Completion(value)

	def assign(self, address, job=True):
		"""The specified child object is working on the given job.

		:param address: the async object
		:type address: ansar address
		:param job: what the child object is doing on behalf of this object
		:type job: any
		"""
		self.address_job[address] = job

	def working(self):
		"""Check if there are child objects still active. Returns the count."""
		return len(self.address_job)

	def progress(self, address=None):
		"""Find the job for the specified address. Return the job or None.

		:param address: the async object
		:type address: ansar address
		:rtype: any or None
		"""
		a = address or self.return_address
		try:
			j = self.address_job[a]
		except KeyError:
			return None
		return j

	def running(self):
		"""Yield a sequence of job, address tuples."""
		for k, v in self.address_job.items():
			yield v, k

	def abort(self):
		"""Initiate the termination protocol for all pending jobs. Return the count of."""
		for _, a in self.running():
			self.send(Stop(), a)
		n = len(self.address_job)
		return n

	def debrief(self, address=None):
		"""Find the job associated with the address. Return the job.

		If no address is provided the current return address is used.
		If a match is found the record is removed, decrementing the
		number of active jobs.

		:param address: the async object
		:type address: ansar address
		:rtype: any or None
		"""
		a = address or self.return_address
		c = self.address_job.pop(a, None)
		return c

	def track(self, address, record, unique_key):
		""".
		"""
		c = self.address_job.pop(a, None)
		return c

	#
	# Logging helpers.
	#
	def log(self, tag, a):
		"""Generate a PointLog object at the specified level.

		This an internal function that should rarely be used directly
		by an application. Use debug(), trace(), etc instead.

		Forms a standard logging object and sends it to the logging
		service within the ansar runtime. The message to include
		is passed as either a str or a tuple of strings and objects,
		i.e. the tuple of positional arguments. Encoding and decoding
		is performed to ensure a single line log. Non ASCII characters
		are escaped with a backslash.

		:param tag: one of the logging single-character tags
		:type tag: str
		:param a: the message to log
		:type text: str or tuple
		"""
		e = PointLog()
		e.stamp = time()
		e.tag = tag
		e.address = self.address
		e.name = self.__art__.name
		# Hack-ish implementation.
		# Should be common base and derived impl's.
		if self.current_state is None:
			e.state = None
		else:
			e.state = self.current_state.__name__

		if isinstance(a, str):
			e.text = a
			send_a_message(e, pt.log_address, self.address)
			return

		b, first = bytearray(), True
		for t in a:
			if first:
				first = False
			else:
				b += b' '

			if isinstance(t, str):
				x = t.encode('utf-8')
			elif isinstance(t, (bytes, bytearray)):
				x = t
			else:
				s = str(t)
				x = s.encode('utf-8')
			b += x
		e.text = b.decode('ascii', 'backslashreplace')
		send_a_message(e, pt.log_address, self.address)

	def pass_fail(self, condition, source, line, text):
		p = PointTest()
		p.stamp = ar.world_now()
		p.name = self.__art__.name

		p.condition = condition
		p.source = source
		p.line = line

		encoded = text.encode('utf-8')
		decoded = encoded.decode('ascii', 'backslashreplace')
		p.text = decoded
		send_a_message(p, pt.test_address, self.address)

	def debug(self, *a):
		"""Generate a log at level DEBUG.

		:param a: the message to log
		:type a: tuple of positional arguments
		"""
		if self.__art__.user_logs > ar.USER_LOG_DEBUG:
			return
		self.log(ar.TAG_DEBUG, a)

	def trace(self, *a):
		"""Generate a log at level TRACE.

		:param a: the message to log
		:type a: tuple of positional arguments
		"""
		if self.__art__.user_logs > ar.USER_LOG_TRACE:
			return
		self.log(ar.TAG_TRACE, a)

	def console(self, *a):
		"""Generate a log at level CONSOLE.

		:param a: the message to log
		:type a: tuple of positional arguments
		"""
		if self.__art__.user_logs > ar.USER_LOG_CONSOLE:
			return
		self.log(ar.TAG_CONSOLE, a)

	def sample(self, **kv):
		"""Generate a log at level TRACE.

		A quick way to put runtime values in the logs. Also the basis
		for generating values for statistical analysis. Refer to
		ansar logging documentation.

		:param kv: the named arguments
		:type a: dict
		"""
		b, first = bytearray(), True
		for k, v in kv.items():
			if first:
				first = False
			else:
				b += b':'
			x = k.encode('utf-8')		# Name
			b += x
			b += b'='					# =
			if isinstance(v, str):	   # Value
				x = v.encode('utf-8')
			elif isinstance(v, (bytes, bytearray)):
				x = v
			else:
				s = str(v)
				x = s.encode('utf-8')
			b += x
		text = b.decode('ascii', 'backslashreplace')
		self.log(ar.TAG_CONSOLE, text)

	def warning(self, *a):
		"""Generate a log at level WARNING.

		:param a: the message to log
		:type a: tuple of positional arguments
		"""
		if self.__art__.user_logs > ar.USER_LOG_WARNING:
			return
		self.log(ar.TAG_WARNING, a)

	def fault(self, *a):
		"""Generate a log at level FAULT.

		:param a: the message to log
		:type a: tuple of positional arguments
		"""
		if self.__art__.user_logs > ar.USER_LOG_FAULT:
			return
		self.log(ar.TAG_FAULT, a)

	def test(self, condition, note):
		"""Generate a log at level WARNING, dependent on the condition.

		A ``PointTest`` is also sent to an internal collection point, for
		later recovery, e.g. by test applications. This is sent for both
		pass and fail.

		:param condition: pass or fail
		:type condition: bool
		:param note: a simple string of text
		:type note: str
		"""
		s, l, _ = check_line()
		b = bool(condition)
		self.pass_fail(b, s, l, note)
		if b:
			return condition
		t = '%s (%s:%d)' % (note, s, l)
		self.log(ar.TAG_CHECK, t)
		return condition

	def unsupported_version(self, condition, v):
		e = 'version "%s" not supported' % (v,)
		f = ar.Faulted(condition=condition, explanation=e)
		self.warning('%s, %s' % (condition, e))
		raise Completion(f)

#
#
def bind_point(point, thread=None, lifecycle=True, message_trail=True, execution_trace=True, user_logs=ar.USER_LOG_DEBUG):
	"""Set the runtime flags for the given async object type.

	:param point: a class derived from ``Point``.
	:type point: class
	:param lifecycle: log all create() and complete() events
	:type lifecycle: bool
	:param message_trail: log all send() events
	:type message_trail: bool
	:param execution_trace: log all receive events
	:type execution_trace: bool
	:param user_logs: the logging level for this object type
	:type user_logs: enumeration
	"""
	rt = ar.Runtime(point.__name__, point.__module__, None, None,
		lifecycle=lifecycle,
		message_trail=message_trail,
		execution_trace=execution_trace,
		user_logs=user_logs)

	setattr(point, '__art__', rt)

	if thread:
		try:
			q = pt.thread_classes[thread]
		except KeyError:
			q = set()
			pt.thread_classes[thread] = q
		q.add(point)

def bind_function(routine, lifecycle=True, message_trail=True, execution_trace=True, user_logs=ar.USER_LOG_DEBUG):
	"""Set the runtime flags for the given async function.

	:param routine: an async function.
	:type routine: function
	:param lifecycle: log all create() and complete() events
	:type lifecycle: bool
	:param message_trail: log all send() events
	:type message_trail: bool
	:param execution_trace: log all receive events
	:type execution_trace: bool
	:param user_logs: the logging level for this object type
	:type user_logs: enumeration
	"""
	rt = ar.Runtime(routine.__name__, routine.__module__, None, None,
		lifecycle=lifecycle,
		message_trail=message_trail,
		execution_trace=execution_trace,
		user_logs=user_logs)

	setattr(routine, '__art__', rt)

def halt(address):
	"""Mark the object at the specified address as halted.

	:param address: an async object
	:type address: ansar address
	"""
	with OpenAddress(address) as c:
		if isinstance(c, Channel):
			c.halted = True

#
#
class Threaded(Queue, Point, Dispatching):
	"""Base class for async machines that require dedicated threads.

	:param blocking: block on queue full
	:type blocking: bool
	:param maximum_size: number of pending messages
	:type maximum_size: int
	"""
	def __init__(self, blocking=False, maximum_size=PEAK_BEFORE_DROPPED):
		Queue.__init__(self, blocking=blocking, maximum_size=maximum_size)
		Point.__init__(self)
		Dispatching.__init__(self)

bind_point(Threaded)

#
#
class Channel(Queue, Point, Buffering):
	"""A sync object.

	Used by sync code to access async features. An instance of a channel
	is created by ansar on behalf of each "function" object, i.e. each instance
	of a function object gets a thread and a channel. The thread accesses
	async services through it private channel object. Also used by the
	OpenChannel context object.
	"""
	def __init__(self):
		Queue.__init__(self)
		Point.__init__(self)
		Buffering.__init__(self)
		self.halted = False

bind_point(Channel)

# Standard routines for running the
# message handlers for async class instances.

def run_object(queue):
	"""The thread object silently allocated to machines with dedicated threads."""
	a = queue.address
	queue.received(queue, Start(), queue.parent_address)
	while True:
		mtr = queue.pull()
		m = mtr[0]
		t = mtr[1]
		r = mtr[2]
		if t[-1] == a[-1]:
			queue.to_address = t
			queue.return_address = r
			queue.received(queue, m, r)

	# Termination occurs by raising of Completion exception
	# from within the received() method. The exception is
	# caught by the running_in_thread() function.

def object_dispatch(queue):
	"""The thread object that executes transitions for one or more machines."""
	a = queue.address
	while True:
		mtr = queue.pull()
		m = mtr[0]
		t = mtr[1]
		r = mtr[2]
		if t[-1] == a[-1]:
			if isinstance(m, Stop):	 # [1]
				return True
			continue

		p = find_object(t)
		if not p:
			continue

		try:
			p.to_address = t
			p.return_address = r
			p.received(queue, m, r)	 # [2]
			continue
		# Necessary replication of exceptions in
		# running_in_thread.
		except KeyboardInterrupt:
			s = 'unexpected keyboard interrrupt'
			p.fault(s)
			value = ar.Faulted('object compromised', s)
		except SystemExit:
			s = 'unexpected system exit'
			p.fault(s)
			value = ar.Faulted('object compromised', s)
		except Completion as c:
			value = c.value
		except Exception as e:
			s = str(e)
			s = 'unhandled exception "%s" (%r)' % (s, e)
			p.fault(s)
			value = ar.Faulted('object faulted', s)
		except:
			s = 'unhandled opaque exception'
			p.fault(s)
			value = ar.Faulted('object faulted', s)

		# Convert the exception to a message.
		if p.__art__.lifecycle:
			p.log(ar.TAG_DESTROYED, 'Destroyed')
		s = p.parent_address
		ending = p.object_ending
		destroy_an_object(t)
		ending(value, s, t)

	# Termination of child objects occurs by raising of the
	# Completion exception from within the received() call [2].
	# The exception is caught and the termination protocol
	# concluded. Termination of the dispatcher [1] is the same
	# as for any object, by sending a Stop(). The running_in_thread
	# function concludes the protocol.

bind_function(run_object, lifecycle=False, message_trail=False, execution_trace=False, user_logs=ar.USER_LOG_NONE)
bind_function(object_dispatch, lifecycle=False, message_trail=False, execution_trace=False, user_logs=ar.USER_LOG_NONE)

# Object creation.
#
def create_a_point(object_type, object_ending, parent_address, args, kw):
	if isinstance(object_type, types.FunctionType):
		return custom_routine(object_type, object_ending, parent_address, args, kw)
	elif issubclass(object_type, Point):
		if issubclass(object_type, Machine):
			if issubclass(object_type, Threaded):
				return object_and_thread(object_type, object_ending, parent_address, args, kw)
			else:
				return object_only(object_type, object_ending, parent_address, args, kw)
		elif issubclass(object_type, Channel):
			return sync_object(object_type, parent_address, args, kw)
		else:
			raise ar.CodingProblem('Cannot create Point %r; not a machine or sync.' % (object_type,))
	else:
		raise ar.CodingProblem('Cannot create %r; not a function or Point.' % (object_type,))

def custom_routine(routine, object_ending, parent_address, args, kw):
	"""Create an async object around the supplied function.

	:param routine: the function to run within its own thread
	:type routine: function
	:param parent_address: object that called create()
	:type parent_address: ansar address
	:param args: positional args to be forwarded to the function
	:type args: tuple
	:param kw: key-value args to be forwarded to the function
	:type kw: dict
	:rtype: ansar address
	"""
	# A rude little adjustment to force the object over
	# to the input() system intended for dispatching.
	if routine == object_dispatch:
		object_type = Threaded   # Input and save.
	else:
		object_type = Channel	 # Input, select, ask and save.
	a, q = create_an_object(object_type, object_ending, parent_address, (), {})
	# Overlay the class runtime with the function runtime, i.e. at instance level.
	q.__art__ = routine.__art__
	if q.__art__.lifecycle:
		q.log(ar.TAG_CREATED, 'Created by <%08x>' % (parent_address[-1],))
	start_a_thread(q, routine, args, kw)
	return a

def object_and_thread(object_type, object_ending, parent_address, args, kw):
	"""Create an async object and thread around the supplied type.

	:param object_type: async object expecting its own thread
	:type object_type: registered class
	:param parent_address: object that called create()
	:type parent_address: ansar address
	:param args: positional args to be forwarded to the function
	:type args: tuple
	:param kw: key-value args to be forwarded to the function
	:type kw: dict
	:rtype: ansar address
	"""
	a, q = create_an_object(object_type, object_ending, parent_address, args, kw)
	# Assume the class context, i.e. a derived application class.
	if q.__art__.lifecycle:
		q.log(ar.TAG_CREATED, 'Created by <%08x>' % (parent_address[-1],))
	start_a_thread(q, run_object, (), {})
	# The run_object routine provides the Start message.
	return a

def object_only(object_type, object_ending, parent_address, args, kw):
	"""Create an async object of the supplied type.

	:param object_type: async object
	:type object_type: registered class
	:param parent_address: object that called create()
	:type parent_address: ansar address
	:param args: positional args to be forwarded to the function
	:type args: tuple
	:param kw: key-value args to be forwarded to the function
	:type kw: dict
	:rtype: ansar address
	"""
	a, q = create_an_object(object_type, object_ending, parent_address, args, kw)
	# Assume the object context.
	if q.__art__.lifecycle:
		q.log(ar.TAG_CREATED, 'Created by <%08x>' % (parent_address[-1],))
	send_a_message(Start(), a, parent_address)
	return a

def no_ending(value, parent, address):
	pass

def sync_object(object_type, parent_address, *args, **kw):
	"""Create a synchronous object in the midst of async objects.

	:param object_type: async object
	:type object_type: registered class
	:param parent_address: object that called create()
	:type parent_address: ansar address
	:param args: positional args to be forwarded to the function
	:type args: tuple
	:param kw: key-value args to be forwarded to the function
	:type kw: dict
	:rtype: async object
	"""
	a, q = create_an_object(object_type, no_ending, parent_address, *args, **kw)
	# Assume the object context
	if q.__art__.lifecycle:
		q.log(ar.TAG_CREATED, 'Created by <%08x>' % (parent_address[-1],))
	return q

#
#
class AutoStop(object):
	"""Context to automate clearance of pending objects.

	:param point: parent of the pending objects
	:type point: async object
	:param completed: map of values returned by objects
	:type completed: dict
	"""
	def __init__(self, point, completed=None):
		self.point = point
		self.completed = completed

	def __enter__(self):
		return self.point

	def __exit__(self, exc_type=None, exc_value=None, traceback=None):
		point = self.point
		completed = self.completed

		point.abort()
		while point.working():
			c = point.select(Completed)
			k = point.debrief()
			if completed is not None:
				completed[k] = c.value

		# Handle exceptions that may have come up during execution, by
		# default any exceptions are raised to the user.
		if exc_type != None:
			return False
		return True
