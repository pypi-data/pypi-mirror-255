# Author: Scott Woods <scott.18.group@gmail.com.com>
# MIT License
#
# Copyright (c) 2022, 2023 Scott Woods
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

__all__ = [
	'main',
]

import os
import ansar.create as ar
from ansar.create.home import StartStop

#
#
class INITIAL: pass
class RUNNING: pass
class PAUSED: pass
class EXHAUSTED: pass
class CLEARING: pass
class RETURNING: pass

NO_RETRY = ar.RetryIntervals(step_limit=0)

class Group(ar.Point, ar.StateMachine):
	def __init__(self, settings):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.settings = settings
		self.group_roles = None			# Names of processes to be maintained.
		self.group_start = None			# Moment the first process was started.
		self.return_value = {}			# Most recent completion value.
		self.restart_interval = {}		# Active iterators returning seconds.
		self.auto_restart = {}			# When to restart.
		self.due = None					# Time of nearest restart.
		self.auto_resume = set()		# Processes terminated during PAUSED.
		self.restart_exhausted = set()	# Reached end of timer iterator.

	def restart(self, roles):
		hr = ar.object_role()
		hb = hr.home

		# Look for retry objects that will return a non-zero
		# length sequence of intervals.
		def eval(retry):
			if retry.step_limit == 0:
				return None
			if retry.first_steps or retry.regular_steps:
				return retry
			return None

		# Start the given list of roles. Remember any roles that
		# are no longer present.
		absentee = []
		for r in roles:
			if not hb.role_exists(r):
				absentee.append(r)
				self.trace(f'Role "{r}" not found, deleted during pause?')
				continue
			cr = hb.open_role(r, None, None)
			retry = eval(cr.properties.retry) or eval(hr.properties.retry) or NO_RETRY
			forwarding = r == self.settings.main_role and self.settings.forwarding
			a = self.create(ar.Process, cr.properties.executable,
				forwarding=forwarding,
				home_path=hb.home_path, role_name=r, subrole=False,
				group_pid=os.getpid())
			self.assign(a, [r, retry])

		# If the home/roles have changed underneath this group, there are
		# two options. Terminate immediately or acknowledge and continue.
		# This version follows the latter strategy, discarding any roles
		# that have disappeared.
		if absentee:
			self.group_roles = [r for r in self.group_roles if r not in absentee]
			if not self.group_roles:
				self.complete(ar.Failed(group_start=(None, 'all roles removed')))
			
	def returned(self, value):
		r, retry = self.debrief()
		self.return_value[r] = value

		try:
			i = self.restart_interval[r]
		except KeyError:
			i = ar.smart_intervals(retry)
			self.restart_interval[r] = i

		try:
			s = next(i)
		except StopIteration:
			self.restart_exhausted.add(r)
			self.restart_interval.pop(r, None)
			self.auto_restart.pop(r, None)
			if isinstance(value, ar.Faulted):
				self.trace(f'Role "{r}" exhausted, {value}')
			else:
				self.trace(f'Role "{r}" exhausted')
			return r, None
		
		return r, s

	def next_restart(self):
		lo = None
		for r, t in self.auto_restart:
			if lo is None or t < lo:
				lo = t
		return lo

	def end_run(self):
		hb = ar.object_role().home

		stop = ar.world_now()
		delta = stop - self.group_start
		value = ar.GroupRun(home=hb.home_path,
			role=self.group_roles,
			start=self.group_start,
			stop=stop,
			seconds=delta.total_seconds(),
			completed=self.return_value)

		self.complete(value)

def Group_INITIAL_Start(self, message):
	hr = ar.object_role()

	csv = self.settings.roles
	if not csv:
		self.complete(ar.Rejected(roles=(None, "empty list")))
	self.group_roles = csv.split(',')

	self.group_start = ar.world_now()
	self.restart(self.group_roles)
	return RUNNING

def Group_RUNNING_Completed(self, message):
	r, s = self.returned(message.value)

	if s is None:
		if r == self.settings.main_role:
			if self.working():
				self.abort()
				return RETURNING
			self.complete(message.value)
		return EXHAUSTED
	self.trace(f'Restart in {s} seconds')
	
	t = ar.clock_now() + s
	if self.due is None or t < self.due:
		self.due = t
		self.start(ar.T1, s)
	self.auto_restart[r] = t

	return RUNNING

def Group_RUNNING_T1(self, message):
	hb = ar.object_role().home
	c = ar.clock_now() + 0.25
	
	expired = [r for r, p in self.auto_restart.items() if p < c]
	self.restart(expired)
	for r in expired:
		self.auto_restart.pop(r, None)

	t = self.next_restart()
	if t is None:
		self.due = None
	else:
		self.due = t
		s = t - ar.clock_now()
		self.start(ar.T1, s)

	return RUNNING

def Group_RUNNING_Pause(self, message):
	# Move pending retries to paused for a restart
	# when the pause is lifted. 
	self.auto_resume = set(self.auto_restart.keys())

	# Forget all outstanding retries.
	self.cancel(ar.T1)
	self.restart_interval = {}
	self.auto_restart = {}
	self.due = None
	return PAUSED

def Group_RUNNING_Stop(self, message):
	if self.abort():
		return CLEARING

	self.end_run()

def Group_PAUSED_Completed(self, message):
	r, retry = self.debrief()
	self.return_value[r] = message.value
	self.auto_resume.add(r)

	if r == self.settings.main_role:
		if self.working():
			self.abort()
			return RETURNING
		self.complete(message.value)
	return PAUSED

def Group_PAUSED_Resume(self, message):
	hb = ar.object_role().home

	self.restart(self.auto_resume)
	self.auto_resume = set()
	if self.restart_exhausted:
		return EXHAUSTED
	return RUNNING

def Group_PAUSED_Stop(self, message):
	if self.abort():
		return CLEARING

	self.end_run()

def Group_EXHAUSTED_Completed(self, message):
	r, s = self.returned(message.value)

	if s is None:
		if r == self.settings.main_role:
			if self.working():
				self.abort()
				return RETURNING
			self.complete(message.value)
	else:
		t = ar.clock_now() + s
		if self.due is None or t < self.due:
			self.due = t
			self.start(ar.T1, s)
		self.auto_restart[r] = t

	return EXHAUSTED

def Group_EXHAUSTED_T1(self, message):
	hb = ar.object_role().home
	c = ar.clock_now() + 0.25
	
	expired = [r for r, p in self.auto_restart.items() if p < c]
	self.restart(expired)
	for r in expired:
		self.auto_restart.pop(r, None)

	t = self.next_restart()
	if t is None:
		self.due = None
	else:
		self.due = t
		s = t - ar.clock_now()
		self.start(ar.T1, s)

	return EXHAUSTED

def Group_EXHAUSTED_Resume(self, message):
	# Move pending retries to paused for a restart
	# when the pause is lifted. 
	self.restart(self.restart_exhausted)
	self.restart_exhausted = set()

	return RUNNING

def Group_EXHAUSTED_Stop(self, message):
	if self.abort():
		return CLEARING

	self.end_run()

def Group_CLEARING_Completed(self, message):
	r, retry = self.debrief()
	self.return_value[r] = message.value
	if self.working():
		return CLEARING

	self.end_run()

def Group_RETURNING_Completed(self, message):
	r, retry = self.debrief()
	self.return_value[r] = message.value
	if self.working():
		return RETURNING

	value = self.return_value[self.settings.main_role]
	self.complete(value)

	self.end_run()

GROUP_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	RUNNING: (
		(ar.Completed, ar.T1, ar.Pause, ar.Stop), ()
	),
	PAUSED: (
		(ar.Completed, ar.Resume, ar.Stop), ()
	),
	EXHAUSTED: (
		(ar.Completed, ar.T1, ar.Resume, ar.Stop), ()
	),
	RETURNING: (
		(ar.Completed,), ()
	),
	CLEARING: (
		(ar.Completed,), ()
	),
}

ar.bind(Group, GROUP_DISPATCH)

class Settings(object):
	def __init__(self, roles=None, main_role=None, forwarding=False):
		self.roles = roles
		self.main_role = main_role
		self.forwarding = forwarding

SETTINGS_SCHEMA = {
	'roles': ar.Unicode(),
	'main_role': ar.Unicode(),
	'forwarding': ar.Boolean(),
}

ar.bind(Settings, object_schema=SETTINGS_SCHEMA)

factory_settings = Settings()

# Entry point for packaging. The
# $ group command starts here.
def main():
	ar.create_object(Group, factory_settings=factory_settings)

# The standard entry point. Needed for IDEs
# and debugger sessions.
if __name__ == '__main__':
	main()
