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

"""Temporary, thread-safe buffering of sent messages and how to get messages with reordering.

A collection of classes to be inherited by different points. Most notably
synchronous channels, and the 2 different machine types.
"""
__docformat__ = 'restructuredtext'

import queue as pyq
from collections import deque
from re import X

import ansar.encode as ar
from .lifecycle import Completed, Stop

__all__ = [
	'PEAK_BEFORE_DROPPED',
	'MAXIMUM_REPLAYS',
	'Queue',
	'SelectTimer',
	'Other',
	'Player',
	'Buffering',
	'Dispatching',
	'Machine',
]

PEAK_BEFORE_DROPPED = 1024 * 8
GRACE_PERIOD = 5
MAXIMUM_REPLAYS = 8

# The buffering between senders and receivers. Firstly this is a
# wrapper around the system queue. Then there are several flavours
# of access to that wrapper. One style about sync access and the
# other about message processing for machines. Both of them implementing
# the save-replay model from SDL.
class Queue(object):
	"""Base for any object intended to operate as a message queue.

	:param blocking: behaviour on queue full
	:type blocking: bool
	:param maximum_size: number of message to hold
	:type maximum_size: int
	"""

	def __init__(self, blocking=False, maximum_size=PEAK_BEFORE_DROPPED):
		"""Construct an instance of Queue."""
		self.blocking = blocking
		self.message_queue = pyq.Queue(maxsize=maximum_size)
		self.thread_function = None
		self.assigned_thread = None

	def put(self, mtr):
		"""Append the [message, to, return] triple to the queue."""
		try:
			self.message_queue.put(mtr, self.blocking)
		except pyq.Full:
			# Silently FOTF.
			pass

	def get(self):
		"""Return the pending [message, to, return] triplet or block."""
		mtr = self.message_queue.get()
		return mtr



class Player(object):
	"""Base for objects intending to operate message buffering with replay."""

	def __init__(self):
		"""Construct an instance of Player."""
		self.pending = deque()		  # Recently saved.
		self.replaying = deque()		# Active replay
		self.get_frame = None

	def pull(self):
		"""Get the next replay message or a fresh message from the queue."""
		if self.replaying:
			mtr = self.replaying.popleft()
		else:
			mtr = self.get()
			if len(mtr) == 3:
				mtr.append(0)
			if self.pending:
				# Only replay those pending on the same address.
				other = deque()
				for p in self.pending:
					if p[1][-1] == mtr[1][-1]:
						self.replaying.append(p)
					else:
						other.append(p)
				self.pending = other
		self.get_frame = mtr
		return mtr

	def pushback(self, m):
		"""Retain the [message, to, return] triplet for later replay."""
		mtr = self.get_frame
		if id(m) != id(mtr[0]):
			return
		mtr[3] += 1
		if mtr[3] < MAXIMUM_REPLAYS:
			self.pending.append(mtr)

	def flush(self):
		try:
			while True:
				self.message_queue.get_nowait()
		except pyq.Empty:
			pass
		self.replaying.clear()
		self.pending.clear()

# Dedicated timer for managed messaging.
class SelectTimer(object):
	"""Timer for managed input."""
	pass

class Other(object):
	"""Capture un-declared input."""
	def __init__(self, value=None):
		self.value = value

ar.bind_message(SelectTimer)
ar.bind_message(Other, object_schema={"value": ar.Any()})

class Dispatching(Player):
	"""Provides input mechanism for any machine with its own queue."""

	def __init__(self):
		Player.__init__(self)
		"""Construct an instance of Dispatching."""

	def input(self):
		"""Get a message from replay buffer or fresh from queue. Return message triplet."""
		mtr = self.pull()
		m = mtr[0]
		t = mtr[1]
		r = mtr[2]
		self.to_address = t
		self.return_address = r
		mf = m.__art__
		if self.__art__.execution_trace and mf.execution_trace:
			self.log(ar.TAG_RECEIVED, "Received %s from <%08x>" % (mf.name, self.return_address[-1]))
		return m, t, r

	def undo(self, m):
		"""Retain the [message, to, return] triplet, using values saved during input."""
		self.pushback(m)

class Buffering(Player):
	"""Base for any object intending to perform sophisticated I/O, i.e. channels and routines."""

	def __init__(self):
		Player.__init__(self)
		"""Construct an instance of Buffering."""

	def save(self, m):
		"""Retain the [message, to, return] triplet, using values saved during input.

		:param m: message to be saved
		:type m: message object
		"""
		self.pushback(m)

	def input(self):
		"""Get the next message while transparently buffering.

		:rtype: message object
		"""
		mtr = self.pull()
		m = mtr[0]
		self.to_address = mtr[1]		# For convenience to caller.
		self.return_address = mtr[2]
		mf = m.__art__
		if self.__art__.execution_trace and mf.execution_trace:
			self.log(ar.TAG_RECEIVED, "Received %s from <%08x>" % (mf.name, self.return_address[-1]))
		return m

	def select(self, *matching, saving=None, seconds=0):
		"""Expect one of the listed messages, with optional saving and timeout.

		:param matching: message types to be accepted
		:type matching: the positional arguments tuple
		:param saving: message types to be deferred
		:type saving: tuple
		:param seconds: waiting period
		:type seconds: float
		:rtype: message object
		"""
		if saving is None:
			saving = ()
		elif saving == ar.Unknown:
			pass
		elif not isinstance(saving, tuple):
			saving = (saving,)

		# Not None and not zero.
		if seconds:
			matching += (SelectTimer,)
			self.start(SelectTimer, seconds)

		def c_in_matching(m, matching):
			c = type(m)
			for t in matching:
				if issubclass(c, t):
					return m
			if Other in matching:
				return Other(m)
			return None

		qf = self.__art__
		while True:
			mtr = self.pull()
			m = mtr[0]
			self.to_address = mtr[1]		# For convenience to caller.
			self.return_address = mtr[2]
			mf = m.__art__
			c = type(m)
			# Latest message is either
			# 1) matched and returned,
			# 2) saved for later,
			# 3) or dropped on the floor.
			r = c_in_matching(m, matching)
			if r is not None:
				if seconds:
					self.cancel(SelectTimer)
				if qf.execution_trace and mf.execution_trace:
					self.log(ar.TAG_RECEIVED, "Received %s from <%08x>" % (mf.name, self.return_address[-1]))
				return r
			if saving == ar.Unknown or c in saving:
				self.save(m)
				continue
			if qf.execution_trace and mf.execution_trace:
				self.log(ar.TAG_RECEIVED, "Dropped %s from <%08x>" % (mf.name, self.return_address[-1]))

	def ask(self, q, r, a, saving=None, seconds=None):
		"""Query for a response while allowing reordering, with optional timer.


		:param q: query to be sent
		:type q: registered message
		:param r: response types to be detected and returned
		:type r: tuple
		:param a: async object to be queried
		:type a: ansar address
		:param saving: response types to be detected and buffered
		:type saving: tuple
		:param seconds: waiting period
		:type seconds: float
		:rtype: message object
		"""
		self.send(q, a)
		if not isinstance(r, tuple):
			return self.select(r, saving=saving, seconds=seconds)
		return self.select(*r, saving=saving, seconds=seconds)

	def stop(self, a, r=(Completed,), saving=None, seconds=None):
		"""Request the termination of an object.

		:param a: async object to be queried
		:type a: ansar address
		:param r: response types to be detected and returned
		:type r: tuple
		:param saving: response types to be detected and buffered
		:type saving: tuple
		:param seconds: waiting period
		:type seconds: float
		:rtype: message object
		"""
		return self.ask(Stop(), r, a, saving=saving, seconds=seconds)

class Machine(object):
	"""Base for machines, providing for presentation of messages and save."""

	def __init__(self):
		"""Construct an instance of Machine."""

	def save(self, m):
		"""Retain the [message, to, return] triplet, i.e. call the parent queue."""
		self.assigned_queue.undo(m)

	def received(self, queue, message, return_address):
		"""A placeholder for erroneous use.Raises a ``CodingProblem`` exception."""
		raise ar.CodingProblem('Message received by virtual base. Use Stateless or StateMachine.')
