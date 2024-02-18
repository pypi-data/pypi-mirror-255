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

"""Support for the concept of attempts and retries.

There is an object that tries to complete a task. If it fails, subsequent
attempts may be appropriate. A clear and robust implementation of this concept
is hugely useful in the context of networking. There is also a need for
refinement - "blunt force" retries can quickly create its own problems.

Signficant events/message/results are;
* Start, Completed, Stop
* Maybe, Cannot, Interrupted, Exhausted

Normal sequence looks like;
* Start, Completed(Maybe), T1, Completed(Maybe), T1, ... Completed(*)

Failed sequence looks like;
* Start, Completed(Maybe), T1, Completed(Maybe), ... Exhausted()

Successful resume sequence looks like;;
* Start, Completed(Maybe), T1, Completed(Interrupted), T1, ... Completed(*)

Failed resume sequence looks like;;
* Start, Completed(Maybe), T1, Completed(Interrupted), T1, ... Completed(Cannot)

Successful cycles sequence looks like;;
* Start, Completed(Maybe), T1, Completed(Interrupted), T1, ... <GLARING>, T1, Completed(*)
"""
__docformat__ = 'restructuredtext'

import random
import ansar.encode as ar
from .lifecycle import Start, Completed, Stop, Aborted
from .lifecycle import Maybe, Cannot, Interrupted, Exhausted
from .point import Point, T1
from .machine import StateMachine, bind_statemachine

__all__ = [
	'RetryIntervals',
	'intervals_only',
	'smart_intervals',
	'Retry',
]

#
#
random.seed()

# All times are subject to the accuracy of the internal timer service, e.g. 0.25s
# The randomized value should be a multiple of the timer accuracy.
# Step 1 should be at least twice of randomized
# The value of first steps should increase.
# Regular steps should be bigger than the last first step.
# All attributes except first_steps, can be set to None.
# There must be at least first steps or regular steps or both.
# Regular steps without a truncated value is an expression of forever.
# The defaults are based on the retry strategy frop SIP.
# Randomization is loosely based on exponential backoff.

class RetryIntervals(object):
	def __init__(self, first_steps=None, regular_steps=None, step_limit=None, randomized=None, truncated=None):
		self.first_steps = first_steps or ar.default_vector()
		self.regular_steps = regular_steps
		self.step_limit = step_limit
		self.randomized = randomized
		self.truncated = truncated

RETRY_INTERVALS_SCHEMA = {
	'first_steps': ar.VectorOf(ar.Float8()),
	'regular_steps': ar.Float8(),
	'step_limit': ar.Integer8(),
	'randomized': ar.Float8(),
	'truncated': ar.Float8(),
}

ar.bind(RetryIntervals, object_schema=RETRY_INTERVALS_SCHEMA)

# Coroutine to generate the sequence
# implied by first_steps and regular_steps.
def intervals_only(retry):
	for i in retry.first_steps:
		yield i
	if retry.regular_steps is None:
		return
	# For ever perhaps capped by
	# limit.
	while True:
		yield retry.regular_steps

# Wrap it in another coroutine that implements
# truncations and randomization of the underlying
# sequence.
def smart_intervals(retry):
	limit = retry.step_limit
	randomized = retry.randomized
	truncated = retry.truncated
	def cooked(r):
		if randomized is None:
			return r
		if truncated is None:
			t = r
		else:
			t = r * truncated
		m = int(t / retry.randomized) + 1
		s = random.randrange(0, m)
		c = s * retry.randomized
		return r + c

	if limit is None:
		for r in intervals_only(retry):
			yield cooked(r)
		return

	for _, r in zip(range(limit), intervals_only(retry)):
		yield cooked(r)


# A machine that uses the interval machinery above to run a sequence of
# attempts - an attempt being the creation and completion of an object.
# Periods of doing nothing are injected between each attempt.

# Mostly about ATTEMPTING and PAUSING until it either succeeds or fails
# It also allows for repeats of the ATTEMPTING-PAUSING, i.e. with a longer separating pause.
# Lastly, a failed ATTEMPTING-PAUSING cycle can shift to RESUMING-RESTING to
# recover context of partial work, and complete.

class INITIAL: pass
class ATTEMPTING: pass	  # An attempt object is running.
class PAUSING: pass		 # An attempt ended with Maybe() and interval available.
class HOLDING: pass		 # An attempt ended with Interrupted() and hold time available.
class RESUMING: pass		# An attempt object (with partial work) is running.
class RESTING: pass		 # An attempt to resume ended with Maybe().
class GLARING: pass		 # Intervals exhausted for attempts or resumptions.
class CLEARING: pass		# Sent Stop() to attempt or resumption.

class Retry(Point, StateMachine):
	def __init__(self, attempt, intervals, hold=None, repeats=None):
		Point.__init__(self)
		StateMachine.__init__(self, INITIAL)
		self.attempt = attempt				  # Function that creates an attempt.
		self.intervals = intervals			  # Description of intervals between attempts.
		self.a = None						   # Address of the current attempt.
		self.sequence = None					# Intervals iterator.
		self.hold = hold
		self.work = None
		self.repeats = repeats	  # Are there any cycles.
		self.repeating = None	   # Cycles iterator.

def Retry_INITIAL_Start(self, message):
	self.a = self.attempt(self, None)
	self.sequence = iter(smart_intervals(self.intervals))
	return ATTEMPTING

def Retry_ATTEMPTING_Completed(self, message):
	v = message.value
	if isinstance(v, Maybe):
		pass
	elif isinstance(v, Cannot):
		self.complete(v)
	elif isinstance(v, Interrupted):
		hold = self.hold
		if hold is None:
			f = ar.Faulted('no hold time specified', 'unexpected interruption')
			self.warning(str(f))
			self.complete(f)
		self.work = v.work
		self.trace('Holding for %f seconds' % (hold,))
		self.start(T1, hold)
		return HOLDING
	else:				   # Standard completion.
		self.complete(v)	# Something other than control messages.

	# An attempt failed but there is a chance that a retry
	# is worthwhile.
	try:
		s = next(self.sequence)
	except StopIteration:
		# No retry remaining. Check for
		# cycle handling.
		repeats = self.repeats
		if repeats is None:
			self.complete(Exhausted())

		# There is a pattern of attempts, long rest, attempts, ...
		if self.repeating is None:
			self.repeating = iter(smart_intervals(repeats))
		try:
			s = next(self.repeating)
		except StopIteration:
			self.complete(Exhausted())

		self.trace('Glaring for %f seconds' % (s,))
		self.start(T1, s)
		return GLARING

	# Standard intra-attempt stand down...
	self.trace('Pausing for %f seconds' % (s,))
	self.start(T1, s)
	return PAUSING

def Retry_ATTEMPTING_Stop(self, message):
	self.send(message, self.a)
	return CLEARING

def Retry_PAUSING_T1(self, message):
	self.a = self.attempt(self, None)
	return ATTEMPTING

def Retry_PAUSING_Stop(self, message):
	self.complete(Aborted())

def Retry_HOLDING_T1(self, message):
	self.a = self.attempt(self, self.work)
	self.sequence = iter(smart_intervals(self.intervals))
	return RESUMING

def Retry_HOLDING_Stop(self, message):
	self.complete(Aborted())

def Retry_RESUMING_Completed(self, message):
	v = message.value
	if isinstance(v, Maybe):
		pass
	elif isinstance(v, Cannot):
		self.complete(v)
	elif isinstance(v, Interrupted):
		hold = self.hold
		self.work = v.work
		self.trace('Holding for %f seconds' % (hold,))
		self.start(T1, hold)
		return HOLDING
	else:				   # Standard completion.
		self.complete(v)	# Something other than control messages.

	# An attempt failed but there is a chance that a retry
	# is worthwhile.
	try:
		s = next(self.sequence)
	except StopIteration:
		# No retries remaining - resumption failed.
		# If cycles are active we need to get back to
		# normal attempts.
		repeats = self.repeats
		if repeats is None:
			self.complete(Exhausted())

		# There is a pattern of attempts, rest, attempts, ...
		if self.repeating is None:
			self.repeating = iter(smart_intervals(repeats))
		try:
			s = next(self.repeating)
		except StopIteration:
			self.complete(Exhausted())

		self.trace('Glaring for %f seconds' % (s,))
		self.start(T1, s)
		return GLARING

	# Standard intra-resumption stand down...
	self.trace('Resting for %f seconds' % (s,))
	self.start(T1, s)
	return RESTING

def Retry_RESUMING_Stop(self, message):
	self.send(message, self.a)
	return CLEARING

def Retry_RESTING_T1(self, message):
	self.a = self.attempt(self, self.work)
	return RESUMING

def Retry_RESTING_Stop(self, message):
	self.complete(Aborted())

def Retry_GLARING_T1(self, message):
	self.a = self.attempt(self, None)
	self.sequence = iter(smart_intervals(self.intervals))
	return ATTEMPTING

def Retry_GLARING_Stop(self, message):
	self.complete(Aborted())

def Retry_CLEARING_Completed(self, message):
	self.complete(Aborted())

RETRY_DISPATCH = {
	INITIAL: (
		(Start,),
		()
	),
	ATTEMPTING: (
		(Completed, Stop),
		()
	),
	PAUSING: (
		(T1, Stop),
		()
	),
	HOLDING: (
		(T1, Stop),
		()
	),
	RESUMING: (
		(Completed, Stop),
		()
	),
	RESTING: (
		(T1, Stop),
		()
	),
	GLARING: (
		(T1, Stop),
		()
	),
	CLEARING: (
		(Completed,),
		()
	),
}

bind_statemachine(Retry, dispatch=RETRY_DISPATCH, thread='retries')
