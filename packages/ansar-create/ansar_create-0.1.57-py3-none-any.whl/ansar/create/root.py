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
"""Management of the ansar, async runtime.

Ensure that the support for async operation is in place when the process
needs it. Ensure the support is cleared out during process termination.
"""
__docformat__ = 'restructuredtext'

import sys
import threading
import atexit
import ansar.encode as ar
from .space import set_queue, get_queue_address
from .point import pt, Point, object_dispatch, halt, bind_point
from .point import Channel, destroy_an_object
from .lifecycle import Completed, Stop
from .log import LogAgent, log_to_nowhere, select_logs
from .timing import CountdownTimer, timer_circuit
from .test import TestRecord
#from .object import object_settings

__all__ = [
	'rt',
	'QuietChannel',
	'boot_up',
	'start_up',
	'tear_down',
	'open_channel',
	'drop_channel',
	'OpenChannel',
	'AddOn',
]

# The collection of runtime objects created. See also
# point.pt.
rt = ar.Gas(
	root=None,
	circuit_address=None,
	thread_dispatch={},
	add_ons=[],
)

class AddOn(object):
	def __init__(self, create, stop):
		cs = (create, stop)
		rt.add_ons.append(cs)

# A silent intermediary between the worlds of sync and
# async.
class QuietChannel(Channel):
	def __init__(self):
		Channel.__init__(self)

bind_point(QuietChannel, lifecycle=False, message_trail=False, execution_trace=False, user_logs=ar.USER_LOG_NONE)

root_lock = threading.RLock()

def boot_up(logs):
	"""Start the async runtime. Return the root object, bool tuple.

	This is the function that actually creates the threads and objects
	that are needed to support the SDL model of async operation. It checks
	to see if the runtime is already up, in a thread-safe way. It returns
	a 2-tuple; a root object that remains constant for the life of a
	process and a flag indicating whether the runtime actually needed
	booting or not.

	The flag is used to determine the manner in which a process has
	been started. Some callers will use the flag to implement cleanup
	on process termination, i.e. using ``atexit()``.

	:param logs: an object expecting to receive log objects
	:type logs: a callable object
	:rtype: 2-tuple
	"""
	global root_lock
	booted = False
	try:
		root_lock.acquire()
		root = rt.root
		if root is None:
			booted = True
			nowhere = Point()
			root = nowhere.create(QuietChannel)
			rt.root = root
			pt.log_address = root.create(LogAgent, logs)
			pt.timer_address = root.create(CountdownTimer)
			pt.test_address = root.create(TestRecord)
			rt.circuit_address = root.create(timer_circuit, pt.timer_address)
			bg = root.create(object_dispatch)
			set_queue(None, bg)
			for k, s in pt.thread_classes.items():
				t = root.create(object_dispatch)
				for c in s:
					set_queue(c, t)
				rt.thread_dispatch[k] = t
			for cs in rt.add_ons:
				cs[0](root)
	finally:
		root_lock.release()
	return root, booted

# TBD
#def settings_logs():
#	if object_settings.debug_level is None:
#		return None
#	return select_logs(object_settings.debug_level)

def start_up(logs):
	"""Start the async runtime. Return the root object.

	The start routine called by those who are in a position
	to perform proper shutdown during process termination. Just
	calls the lower-level ``boot_up()`` and ignores the detail
	about whether the runtime was already up.

	:param logs: an object expecting to receive log objects
	:type logs: a callable object
	:rtype: Point-based object
	"""
	#logs = logs or settings_logs() or log_to_nowhere
	logs = logs or log_to_nowhere
	root, _ = boot_up(logs)
	return root

# Shutdown the standard services and (optionally)
# terminate.
def tear_down(code=None):
	"""End the async runtime. Return nothing.

	This function cleans up everything created by boot_up().

	:param code: the desired exit status or none
	:type code: int
	:rtype: None
	"""
	global root_lock
	try:
		root_lock.acquire()
		root = rt.root
		if root:
			s = Stop()
			for cs in reversed(rt.add_ons):
				cs[1](root)
			for _, t in rt.thread_dispatch.items():
				root.send(s, t)
				root.select(Completed)
			bg = get_queue_address(None)
			root.send(s, bg)
			root.select(Completed)
			halt(rt.circuit_address)
			root.select(Completed)
			root.send(s, pt.test_address)
			root.select(Completed)
			root.send(s, pt.timer_address)
			root.select(Completed)
			root.send(s, pt.log_address)
			root.select(Completed)
			drop_channel(root)
			root = None
	finally:
		root_lock.release()

	if code is not None:
		# Exits the active, main thread. All other threads have
		# been stopped.
		sys.exit(code)

# Access to async from sync section of an
# application.
def open_channel(logs=log_to_nowhere):
	"""Start the runtime for a non-standard executable. Return a unique async object.

	Create a new async object for the purposes of initiating
	async activity, typically from within a non-async section of
	code. Registers a cleanup function with the process, to execute
	on process termination.

	:param logs: an object expecting to receive log objects
	:type logs: a callable object
	:rtype: Point-based object
	"""
	root, booted = boot_up(logs)
	if booted:
		atexit.register(tear_down)
	channel = root.create(Channel)
	return channel

def drop_channel(c):
	"""End the runtime for a non-standard executable. Return nothing.

	Tear down the runtime created by ``open_channel()``, i.e. ``boot_up()``.

	:param c: a channel returned by open_channel()
	:type c: Point-based object
	:rtype: none
	"""
	if c.__art__.lifecycle:
		c.log(ar.TAG_DESTROYED, 'Destroyed')
	destroy_an_object(c.address)

#
#
class OpenChannel:
	"""A context to automate the opening and closing of a channel.

	Typically used in a traditional, sync application to access the async
	features of ansar. May be used anywhere within an application. Each
	instance creates a unique channel. The parameter provides for control
	over the fate of logs. This only has an effect on the first use of
	the class.

	:param logs: an object expecting to receive log objects
	:type logs: a callable object
	"""
	def __init__(self, logs=log_to_nowhere):
		self.channel = open_channel(logs)

	def __enter__(self):
		return self.channel

	def __exit__(self, exc_type=None, exc_value=None, traceback=None):
		drop_channel(self.channel)

		# Handle exceptions that may have come up during execution, by
		# default any exceptions are raised to the user.
		if exc_type != None:
			return False
		return True
