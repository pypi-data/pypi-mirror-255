# Author: Scott Woods <scott.18.ansar@gmail.com.com>
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
	'CreateSettings',
	'AddSettings',
	'UpdateSettings',
	'DeleteSettings',
	'DestroySettings',
	'ListSettings',
	'StartSettings',
	'RunSettings',
	'PauseSettings',
	'ResumeSettings',
	'StopSettings',
	'LogSettings',
	'InputSettings',
	'SettingsSettings',
	'SetSettings',
	'EditSettings',
	'DeploySettings',
	'ReturnedSettings',
	'procedure_create',
	'procedure_add',
	'procedure_update',
	'procedure_delete',
	'list_home',
	'procedure_destroy',
	'procedure_run',
	'procedure_start',
	'procedure_pause',
	'procedure_resume',
	'procedure_stop',
	'procedure_status',
	'procedure_history',
	'procedure_returned',
	'procedure_log',
	'procedure_folder',
	'procedure_input',
	'procedure_settings',
	'procedure_get',
	'procedure_set',
	'procedure_edit',
	'procedure_deploy',
	'procedure_snapshot',
	'DEFAULT_HOME',
	'DEFAULT_GROUP',
	'DEFAULT_ROLE',
]

import os
import stat
import signal
import errno
import datetime
import calendar
import tempfile
import uuid
import re
import ansar.encode as ar
from .coding import *
from .binding import *
from .point import *
from .machine import *
from .lifecycle import *
from .home import *
from .rolling import *
from .storage import *
from .locking import *
from .processing import *
from .object import *
from .retry import *
from .grouping import *
from .properties import *
from .test import *

START_ORIGIN = POINT_OF_ORIGIN.START_ORIGIN
RUN_ORIGIN = POINT_OF_ORIGIN.RUN_ORIGIN

# Per-command arguments as required.
# e.g. command-line parameters specific to create.
class CreateSettings(object):
	def __init__(self,
			home_path=None,
			redirect_bin=None,
			redirect_lock=None,
			redirect_settings=None,
			redirect_logs=None,
			redirect_resource=None,
			redirect_tmp=None,
			redirect_model=None
			):
		self.home_path = home_path
		self.redirect_bin = redirect_bin
		self.redirect_lock = redirect_lock
		self.redirect_settings = redirect_settings
		self.redirect_logs = redirect_logs
		self.redirect_resource = redirect_resource
		self.redirect_tmp = redirect_tmp
		self.redirect_model = redirect_model

CREATE_SETTINGS_SCHEMA = {
	'home_path': ar.Unicode(),
	'redirect_bin': ar.Unicode(),
	'redirect_lock': ar.Unicode(),
	'redirect_settings': ar.Unicode(),
	'redirect_logs': ar.Unicode(),
	'redirect_resource': ar.Unicode(),
	'redirect_tmp': ar.Unicode(),
	'redirect_model': ar.Unicode(),
}

ar.bind(CreateSettings, object_schema=CREATE_SETTINGS_SCHEMA)

#
#
class AddSettings(object):
	def __init__(self, executable=None, role_name=None, home_path=None, start=0, step=1, count=1,
		settings_file=None,
		input_file=None,
		retry=None, storage=None):
		self.executable = executable
		self.role_name = role_name
		self.home_path = home_path
		self.start = start
		self.step = step
		self.count = count
		self.settings_file = settings_file
		self.input_file = input_file
		self.retry = retry
		self.storage = storage

ADD_SETTINGS_SCHEMA = {
	'executable': ar.Unicode(),
	'role_name': ar.Unicode(),
	'home_path': ar.Unicode(),
	'start': ar.Integer8(),
	'step': ar.Integer8(),
	'count': ar.Integer8(),
	'settings_file': ar.Unicode(),
	'input_file': ar.Unicode(),
	'retry': ar.UserDefined(RetryIntervals),
	'storage': ar.Integer8(),
}

ar.bind(AddSettings, object_schema=ADD_SETTINGS_SCHEMA)

#
#
class UpdateSettings(object):
	def __init__(self, role_name=None, home_path=None, executable=None, invert_search=False, groups=True, all_roles=True):
		self.role_name = role_name
		self.home_path = home_path
		self.executable = executable
		self.invert_search = invert_search
		self.groups = groups
		self.all_roles = all_roles

UPDATE_SETTINGS_SCHEMA = {
	'role_name': ar.Unicode(),
	'home_path': ar.Unicode(),
	'executable': ar.Unicode(),
	'invert_search': ar.Boolean(),
	'groups': ar.Boolean(),
	'all_roles': ar.Boolean(),
}

ar.bind(UpdateSettings, object_schema=UPDATE_SETTINGS_SCHEMA)

#
#
class DeleteSettings(object):
	def __init__(self, role_name=None, home_path=None, executable=None, invert_search=False, all_roles=False):
		self.role_name = role_name
		self.home_path = home_path
		self.executable = executable
		self.invert_search = invert_search
		self.all_roles = all_roles

DELETE_SETTINGS_SCHEMA = {
	'role_name': ar.Unicode(),
	'home_path': ar.Unicode(),
	'executable': ar.Unicode(),
	'invert_search': ar.Boolean(),
	'all_roles': ar.Boolean(),
}

ar.bind(DeleteSettings, object_schema=DELETE_SETTINGS_SCHEMA)

#
#
class DestroySettings(object):
	def __init__(self, home_path=None):
		self.home_path = home_path

DESTROY_SETTINGS_SCHEMA = {
	'home_path': ar.Unicode(),
}

ar.bind(DestroySettings, object_schema=CREATE_SETTINGS_SCHEMA)

#
#
class ListSettings(object):
	def __init__(self, role_name=None, home_path=None, executable=None, invert_search=False, long_listing=False, groups=False, all_roles=False):
		self.role_name = role_name
		self.home_path = home_path
		self.executable = executable
		self.invert_search = invert_search
		self.long_listing = long_listing
		self.groups = groups
		self.all_roles = all_roles

LIST_SETTINGS_SCHEMA = {
	'role_name': ar.Unicode(),
	'home_path': ar.Unicode(),
	'executable': ar.Unicode(),
	'invert_search': ar.Boolean(),
	'long_listing': ar.Boolean(),
	'groups': ar.Boolean(),
	'all_roles': ar.Boolean(),
}

ar.bind(ListSettings, object_schema=LIST_SETTINGS_SCHEMA)

#
#
class StartSettings(object):
	def __init__(self, role_name=None, group_name=None, home_path=None, executable=None, invert_search=False, main_role=None):
		self.role_name = role_name
		self.group_name = group_name
		self.home_path = home_path
		self.executable = executable
		self.invert_search = invert_search
		self.main_role = main_role

START_SETTINGS_SCHEMA = {
	'role_name': ar.Unicode(),
	'group_name': ar.Unicode(),
	'home_path': ar.Unicode(),
	'executable': ar.Unicode(),
	'invert_search': ar.Boolean(),
	'main_role': ar.Unicode(),
}

ar.bind(StartSettings, object_schema=START_SETTINGS_SCHEMA)

#
#
class RunSettings(object):
	def __init__(self, executable=None,
		role_name=None, group_name=None, create_group=False, home_path=None,
		invert_search=False,
		main_role=None,
		forwarding=None,
		code_path=None, test_run=False, test_analyzer=None):
		self.executable = executable
		self.role_name = role_name
		self.group_name = group_name
		self.create_group = create_group
		self.home_path = home_path
		self.invert_search = invert_search
		self.main_role = main_role
		self.forwarding = forwarding
		self.code_path = code_path
		self.test_run = test_run
		self.test_analyzer = test_analyzer

RUN_SETTINGS_SCHEMA = {
	'executable': ar.Unicode(),
	'role_name': ar.Unicode(),
	'group_name': ar.Unicode(),
	'create_group': ar.Boolean(),
	'home_path': ar.Unicode(),
	'invert_search': ar.Boolean(),
	'main_role': ar.Unicode(),
	'forwarding': ar.Boolean(),
	'code_path': ar.Unicode(),
	'test_run': ar.Boolean(),
	'test_analyzer': ar.Unicode(),
}

ar.bind(RunSettings, object_schema=RUN_SETTINGS_SCHEMA)

#
#
class PauseSettings(object):
	def __init__(self, executable=None,
		role_name=None, home_path=None,
		invert_search=False):
		self.executable = executable
		self.role_name = role_name
		self.home_path = home_path
		self.invert_search = invert_search

PAUSE_SETTINGS_SCHEMA = {
	'executable': ar.Unicode(),
	'role_name': ar.Unicode(),
	'home_path': ar.Unicode(),
	'invert_search': ar.Boolean(),
}

ar.bind(PauseSettings, object_schema=PAUSE_SETTINGS_SCHEMA)

#
#
class ResumeSettings(object):
	def __init__(self, executable=None,
		group_name=None, home_path=None,
		invert_search=False):
		self.executable = executable
		self.group_name = group_name
		self.home_path = home_path
		self.invert_search = invert_search

RESUME_SETTINGS_SCHEMA = {
	'executable': ar.Unicode(),
	'group_name': ar.Unicode(),
	'home_path': ar.Unicode(),
	'invert_search': ar.Boolean(),
}

ar.bind(ResumeSettings, object_schema=RESUME_SETTINGS_SCHEMA)

#
#
class StopSettings(object):
	def __init__(self, group_name=None, home_path=None, executable=None, invert_search=False):
		self.group_name = group_name
		self.home_path = home_path
		self.executable = executable
		self.invert_search = invert_search

STOP_SETTINGS_SCHEMA = {
	'group_name': ar.Unicode(),
	'home_path': ar.Unicode(),
	'executable': ar.Unicode(),
	'invert_search': ar.Boolean(),
}

ar.bind(StopSettings, object_schema=STOP_SETTINGS_SCHEMA)

# Extraction of logs for a role.
#
START_OF = ar.Enumeration(MONTH=0, WEEK=1, DAY=2, HOUR=3, MINUTE=4, HALF=5, QUARTER=6, TEN=7, FIVE=8)

class LogSettings(object):
	def __init__(self, role_name=None, home_path=None,
			clock=False, from_=None, last=None, start=None, back=None,
			to=None, span=None, count=None):
		# One of these for a <begin>
		self.role_name = role_name
		self.home_path = home_path
		self.clock = clock
		self.from_ = from_
		self.last = last
		self.start = start
		self.back = back

		# One of these (optional), for an <end>
		self.to = to
		self.span = span
		self.count = count

LOG_SETTINGS_SCHEMA = {
	'role_name': ar.Unicode(),
	'home_path': ar.Unicode(),
	"clock": ar.Boolean,
	"from_": ar.Unicode,
	"last": START_OF,
	"start": int,
	"back": ar.TimeSpan,

	"to": ar.Unicode,
	"span": ar.TimeSpan,
	"count": int,
}

ar.bind(LogSettings, object_schema=LOG_SETTINGS_SCHEMA)

#
#
class InputSettings(object):
	def __init__(self, role_name=None, home_path=None, input_file=None, executable=None):
		self.role_name = role_name
		self.home_path = home_path
		self.executable = executable
		self.input_file = input_file

INPUT_SETTINGS_SCHEMA = {
	"role_name": ar.Unicode(),
	"home_path": ar.Unicode(),
	"executable": ar.Unicode(),
	"input_file": ar.Unicode(),
}

ar.bind(InputSettings, object_schema=INPUT_SETTINGS_SCHEMA)

#
#
class SettingsSettings(object):
	def __init__(self, role_name=None, home_path=None, settings_file=None, executable=None):
		self.role_name = role_name
		self.home_path = home_path
		self.executable = executable
		self.settings_file = settings_file

SETTINGS_SETTINGS_SCHEMA = {
	"role_name": ar.Unicode(),
	"home_path": ar.Unicode(),
	"executable": ar.Unicode(),
	"settings_file": ar.Unicode(),
}

ar.bind(SettingsSettings, object_schema=SETTINGS_SETTINGS_SCHEMA)

#
#
class SetSettings(object):
	def __init__(self, property=None, role_name=None, home_path=None, executable=None, invert_search=False,
		property_file=None, retry_intervals=None, not_set=False, all_roles=False):
		self.property = property
		self.role_name = role_name
		self.home_path = home_path
		self.executable = executable
		self.invert_search = invert_search
		self.property_file = property_file
		self.retry_intervals = retry_intervals
		self.not_set = not_set
		self.all_roles = all_roles

SET_SETTINGS_SCHEMA = {
	"property": ar.Unicode,
	"role_name": ar.Unicode,
	"home_path": ar.Unicode,
	"executable": ar.Unicode,
	'invert_search': ar.Boolean(),
	"property_file": ar.Unicode(),
	"retry_intervals": ar.UserDefined(RetryIntervals),
	"not_set": ar.Boolean(),
	"all_roles": ar.Boolean(),
}

ar.bind(SetSettings, object_schema=SET_SETTINGS_SCHEMA)

#
#
class EditSettings(object):
	def __init__(self, property=None, role_name=None, home_path=None):
		self.property = property
		self.role_name = role_name
		self.home_path = home_path

EDIT_SETTINGS_SCHEMA = {
	"property": ar.Unicode,
	"role_name": ar.Unicode,
	"home_path": ar.Unicode,
}

ar.bind(EditSettings, object_schema=EDIT_SETTINGS_SCHEMA)

#
#
class DeploySettings(object):
	def __init__(self, build_path=None, snapshot_path=None, home_path=None):
		self.build_path = build_path
		self.snapshot_path = snapshot_path
		self.home_path = home_path

DEPLOY_SETTINGS_SCHEMA = {
	"build_path": ar.Unicode,
	"snapshot_path": ar.Unicode,
	"home_path": ar.Unicode,
}

ar.bind(DeploySettings, object_schema=DEPLOY_SETTINGS_SCHEMA)

#
#
class ReturnedSettings(object):
	def __init__(self, role_name=None, home_path=None, timeout=None, start=None):
		# One of these for a <begin>
		self.role_name = role_name
		self.home_path = home_path
		self.timeout = timeout
		self.start = start

RETURNED_SETTINGS_SCHEMA = {
	'role_name': ar.Unicode(),
	'home_path': ar.Unicode(),
	"timeout": ar.Float8,
	"start": ar.Integer8,
}

ar.bind(ReturnedSettings, object_schema=RETURNED_SETTINGS_SCHEMA)

#
#
def abort(self, completed=None):
	"""Clear an object of all its workers."""
	self.abort()
	while self.working():
		c = self.select(Completed)
		k = self.debrief()
		if completed is not None:
			completed[k] = c.value

def role_status(self, hb, selected):
	"""Try to lock everything. Return dicts of idle vs running."""
	started = {}
	idle = set()
	running = {}
	selected_roles = lor(list(selected))
	self.console(f'Detect status of associated roles ({selected_roles})')
	try:
		for role in selected:
			if not hb.role_exists(role):
				# Not present, e.g. a new group role so skip.
				# Not in idle and not in running.
				continue
			hr = hb.open_role(role, None, None)
			a = self.create(lock_and_hold, hr.home.lock.path, hr.role_name)
			self.assign(a, role)
			start_stop = hr.properties.start_stop
			if start_stop:
				started[role] = start_stop[-1].start
			else:
				started[role] = None

		# Expect a response for each entry;
		expected = self.working()
		for _ in range(expected):
			m = self.select(Stop, Ready, Completed)
			if isinstance(m, Stop):
				raise ar.Incomplete(Aborted())
			if isinstance(m, Ready):			# This one is idle.
				role = self.progress()
				idle.add(role)
				continue

			# Locker has completed. Probably active.
			role = self.debrief()
			value = m.value
			if isinstance(value, LockedOut):	 # Active.
				running[role] = (value, started[role])
				continue

			raise ar.Incomplete(ar.Failed(role_lock=(value, f'unexpected response for "{role}"')))
	finally:
		abort(self)
	return idle, running

def group_cleared(self, hb, running):
	role = list(running.keys())
	for _ in range(8):
		self.start(T1, 1.0)
		m = self.select(Stop, T1)
		if isinstance(m, Stop):
			raise ar.Incomplete(Aborted())
		_, sticky = role_status(self, hb, role)
		if len(sticky) == 0:
			return

	# Could not budge them all.
	s = lor(list(sticky.keys()))
	raise ar.Incomplete(ar.Failed(role_stop=(None, f'unresponsive process(es) {s}')))

def pause_and_stop(self, hb, running):
	group = {v[0].group_pid for r, v in running.items()}
	member = {v[0].pid for r, v in running.items() if v[0].pid not in group}

	gp = len(group)
	mb = len(member)
	self.trace(f'Pause {gp} groups and stop {mb} members')

	# Cannot guarantee the order of processing of the Pause
	# to a group and the Stop to a member. This is an
	# arbitrary nap to give the Pause messages a chance
	# to get ahead of terminating members.
	for pid in group:
		os.kill(pid, signal.SIGUSR1)		# Pause.

	self.start(T1, 0.5)
	self.select(T1, Stop)

	for pid in member:
		os.kill(pid, signal.SIGINT)			# Stop.

	group_cleared(self, hb, running)

def group_pause(self, hb, matched, force):
	idle, running = role_status(self, hb, matched)
	if not running:
		return idle, running

	for r in running.keys():
		if r.startswith('group.'):
			e = ar.Failed(group_pause=(r, f'cannot pause a running group process, use "stop"'))
			raise ar.Incomplete(e)

	#grouping = {v[0].group_pid for k, v in running.items()}
	#if len(grouping) > 1:
	#	s = lor(matched)
	#	e = ar.Failed(role_status=(None, f'roles "{s}" span multiple running groups'))
	#	raise ar.Incomplete(e)

	# Need that extra expression of intent.
	if not force:
		def show(pid):
			if pid is None:
				return '?'
			return f'{pid}'
		pids = ['<%d>(%s)' % (v[0].pid, show(v[0].group_pid)) for k, v in running.items()]
		pids = ', '.join(pids)
		s = lor(matched)
		e = ar.Failed(group_pause=(None, f'role(s) {s} currently running as {pids}, use "--force"'))
		raise ar.Incomplete(e)

	# Send the Pause and Stop signals.
	pause_and_stop(self, hb, running)

	return idle, running

def group_resume(self, running):
	grouping = {v[0].group_pid for k, v in running.items()}

	gl = len(grouping)
	self.trace(f'Resume {gl} groups')
	for group_pid in grouping:
		try:
			os.kill(group_pid, signal.SIGUSR2)		# Resume.
		except OSError:
			pass

def executable_file(executable):
	if not executable:
		e = ar.Rejected(home_path=(executable, f'executable available to home'))
		raise ar.Incomplete(e)
	try:
		s = os.stat(executable)
	except OSError as e:
		e = ar.Failed(file_status=(e, None))
		raise ar.Incomplete(e)

	mode = s.st_mode
	rwx = stat.filemode(mode)
	if len(rwx) != 10 or rwx[3] != 'x' or rwx[6] != 'x':
		e = ar.Failed(file_permissions=(rwx, 'not an executable file'))
		raise ar.Incomplete(e)
#
#
def already_exists(role):
	raise ar.Incomplete(ar.Failed(role_exists=(None, f'role "{role}" already present')))

def doesnt_exist(role, home):
	raise ar.Incomplete(ar.Failed(role_exists=(None, f'role "{role}" ({home}) does not exist or has unexpected contents')))

def no_matches(search):
	raise ar.Incomplete(ar.Failed(role_search=(None, f'no matches for "{search}"')))

def open_home(home):
	try:
		hb = Homebase(home, FULL_SERVICE)

		if not hb.plan_exists():
			e = ar.Failed(home_exists=(None, f'"{home}" does not exist or has unexpected contents'))
			raise ar.Incomplete(e)
		hb.open_plan()
	except (ar.CodecFailed, ar.FileFailure) as e:
		raise ar.Incomplete(ar.Failed(home_load=(e, None)))

	return hb

def open_role(role, home):
	hb = open_home(home)

	try:
		if not hb.role_exists(role):
			doesnt_exist(role, home)
		hr = hb.open_role(role, None, None)
	except (ar.CodecFailed, ar.FileFailure) as e:
		raise ar.Incomplete(ar.Failed(role_load=(e, None)))

	return hr

def find_role(hb, role_search, groups=False, subroles=False, executable=None, flip=False):
	if not role_search:
		role_search = [None]
		search = '(all)'
	else:
		search = lor(role_search, separator=' ')

	matched = set()
	for rs in role_search:
		machine = None if rs is None else re.compile(rs)

		def check_list(r):
			if '.' in r:
				if r.split('.')[0] == 'group':
					if not groups:
						return False
				elif not subroles:
					return False

			if machine and not machine.fullmatch(r):
				return False

			if executable:
				# Role is guaranteed to exist, i.e. role_list().
				hr = hb.open_role(r, None, None)
				if hr.properties.executable != executable:
					return False

			return True

		def check_role(r):
			t = check_list(r)
			if flip:
				return not t
			return t


		m = [r for r in hb.role_list() if check_role(r)]
		matched.update(m)

	return search, list(matched)

def find_files(role, folder):
	role_search = role if role is not None else 'all'
	if role is None:
		search = ar.Folder(path=folder.path)
	else:
		search = ar.Folder(path=folder.path, re=role)

	matched = [f for f in search.matching()]
	return matched

def long_form(path):
	d = {}
	path = os.path.abspath(path)
	m, _ = storage_manifest(path)
	for f, t in storage_walk(m):
		if isinstance(t, StorageListing):
			d[t.name] = f
	return d

def no_dots(a, tag):
	dotted = [d for d in a if '.' in d]
	if dotted:
		s = lor(dotted)
		e = ar.Failed(name_check=(s, f'sub-roles (dotted names) present in {tag}'))
		raise ar.Incomplete(e)

# Actual implementation of sub-commands starts here.
# Create, add, update... These are the global functions
# called by the internal handler functions inside the
# main object.
FULL_SERVICE = ['bin', 'lock', 'entry', 'settings', 'input', 'logs', 'resource', 'tmp', 'model']

DEFAULT_HOME = '.ansar-home'
DEFAULT_GROUP = 'default'
DEFAULT_ROLE = '{executable}-{number}'

HOME = 'home'
GROUP = 'group'
ROLE = 'role'
PROPERTY = 'property'
BUILD = 'build'
SNAPSHOT = 'snapshot'
FOLDER = 'folder'
EXECUTABLE = 'executable'

#
#
def procedure_create(self, create, path):
	path = ar.word_argument_2(path, create.home_path, DEFAULT_HOME, HOME)

	hb = Homebase(path, FULL_SERVICE)

	redirect = {}
	if create.redirect_bin: redirect['bin'] = create.redirect_bin
	if create.redirect_lock: redirect['lock'] = create.redirect_lock
	if create.redirect_settings: redirect['settings'] = create.redirect_settings
	if create.redirect_logs: redirect['logs'] = create.redirect_logs
	if create.redirect_resource: redirect['resource'] = create.redirect_resource
	if create.redirect_tmp: redirect['tmp'] = create.redirect_tmp
	if create.redirect_model: redirect['model'] = create.redirect_model

	# Resolve to full path.
	redirect = {k: os.path.abspath(v) for k, v in redirect.items()}

	# Cant create whats already there.
	if hb.plan_exists():
		e = ar.Failed(home_exists=(None, f'"{hb.home_path}" already exists'))
		raise ar.Incomplete(e)

	if redirect:
		r = ', '.join(redirect.keys())
		c = f'Creating "{hb.home_path}" (with redirects for {r})'
	else:
		c = f'Creating "{hb.home_path}"'
	self.console(c)

	hb.properties.guid = uuid.uuid4()
	hb.properties.created = ar.world_now()

	hb.create_plan(redirect)
	return None

#
#
def procedure_add(self, add, executable, role, home, ls):
	executable = ar.word_argument_2(executable, add.executable, None, EXECUTABLE)
	if executable is None:
		e = ar.Failed(procedure_add=(None, f'an <executable> is required'))
		raise ar.Incomplete(e)
	role = ar.word_argument_2(role, add.role_name, DEFAULT_ROLE, ROLE)
	home = ar.word_argument_2(home, add.home_path, DEFAULT_HOME, HOME)

	hb = open_home(home)

	# Suitability.
	resolved_executable = hb.resolve_executable(executable)
	executable_file(resolved_executable)

	# Shorthands
	start = add.start
	step = add.step
	count = add.count
	stop = start + count

	# Build table of new roles and their associated args.
	rv = {}	 # Expanded roles and their settings.
	kv = {}	 # Key-values for expansion of names and args.
	kv['executable'] = executable
	for i in range(start, stop, step):
		kv['number'] = i
		kv['uuid'] = uuid.uuid4()
		s = role.format(**kv)
		ls0 = {}
		ls1 = {}

		# This is "useful" but clashes with
		# any argument that might accept a complex
		# encoding, i.e. including braces.
		for k, v in ls[0].items():
			ls0[k] = v.format(**kv)
		for k, v in ls[1].items():
			ls1[k] = v.format(**kv)
		#for k, v in ls[0].items():
		#	ls0[k] = v
		#for k, v in ls[1].items():
		#	ls1[k] = v

		if add.settings_file:
			ls0['settings-file'] = add.settings_file
		if add.input_file:
			ls0['input-file'] = add.input_file

		# Always. Or zombie will never finish creation.
		ls0['store-settings'] = 'true'
		ls0['store-input'] = 'true'

		rv[s] = ls_args([ls0, ls1])

	# Now that intended additions are finalized, check for presence
	# of inappropriate names.
	adding = rv.keys()
	no_dots(adding, 'additions')
	if 'group' in adding:
		e = ar.Failed(name_check=(None, f'"group" is a reserved name'))
		raise ar.Incomplete(e)

	# Ensure that none of the imminent creations are
	# already on disk.
	existing = [e for e in hb.role_list()]
	collision = existing & adding
	if collision:
		s = lor(collision)
		e = ar.Failed(role_exists=(None, f'new role(s) "{s}" collide with existing roles in "{hb.home_path}"'))
		raise ar.Incomplete(e)

	s = lor(list(adding))
	self.console(f'Adding "{s}" ({hb.home_path}), executable "{resolved_executable}"')

	for k, ls in rv.items():
		# Let sub-process do all the creation as its in possession
		# of settings and input details.
		a = self.create(Process, resolved_executable,
			home_path=hb.home_path, role_name=k,
			settings=ls)
		self.assign(a, k)

		m = self.select(Completed, Stop)
		if isinstance(m, Stop):
			abort(self)
			raise ar.Incomplete(Aborted())

		# Process completed.
		r = self.debrief()
		value = m.value
		if isinstance(value, Ack):   # All done.
			pass
		elif isinstance(value, ar.Faulted):
			raise ar.Incomplete(value)
		else:
			e = ar.Failed(role_execute=(value, f'unexpected response from "{k}" ({resolved_executable})'))
			raise ar.Incomplete(e)

	return None

def procedure_update(self, update, force, role_search, ls):
	home = ar.word_argument_2(None, update.home_path, DEFAULT_HOME, HOME)

	hb = open_home(home)

	# Find matches or all.
	search, matched = find_role(hb, role_search,
		groups=update.groups,
		subroles=update.all_roles,
		executable=update.executable,
		flip=update.invert_search)

	_, running = group_pause(self, hb, matched, force)
	try:
		s = lor(matched)
		self.console(f'Updating "{s}" ({hb.home_path}), searched for {search}')

		ls.append('--store-settings=true')
		for m in matched:
			hr = hb.open_role(m, None, None)
			executable = hb.resolve_executable(hr.properties.executable)
			a = self.create(Process, executable,
				home_path=hb.home_path, role_name=m,
				settings=ls)
			self.assign(a, m)

			r = self.select(Completed, Stop)
			if isinstance(r, Stop):
				raise ar.Incomplete(Aborted())

			# Process completed. Remove record.
			m = self.debrief()
			value = r.value
			if isinstance(value, Ack):
				pass
			elif isinstance(value, ar.Faulted):
				raise ar.Incomplete(value)
			else:
				e = ar.Failed(role_execute=(value, f'unexpected response from "{m}" ({executable})'))
				raise ar.Incomplete(e)
	finally:
		abort(self)
		group_resume(self, running)

	return None

def procedure_delete(self, delete, role_search, home):
	home = ar.word_argument_2(None, delete.home_path, DEFAULT_HOME, HOME)

	hb = open_home(home)

	# Find matches or all.
	search, matched = find_role(hb, role_search,
		groups=True,
		subroles=True,
		executable=delete.executable,
		flip=delete.invert_search)
	s = lor(matched)

	_, running = role_status(self, hb, matched)
	if running:
		e = ar.Failed(role_delete=(None, f'cannot delete roles "{s}" from running groups, use "stop"'))
		raise ar.Incomplete(e)

	self.console(f'Deleting "{s}" ({hb.home_path}), searched for "{search}"')

	for r in matched:
		hr = hb.open_role(r, None, None)
		hb.procedure_delete(hr)

	return None

def list_home(self, list_, role_search):
	home = ar.word_argument_2(None, list_.home_path, DEFAULT_HOME, HOME)

	hb = open_home(home)

	# Find matches or all.
	search, matched = find_role(hb, role_search,
		groups=list_.groups,
		subroles=list_.all_roles,
		executable=list_.executable,
		flip=list_.invert_search)

	matched.sort()

	s = lor(matched)
	self.console(f'Listing "{s}" ({hb.home_path})')

	if not list_.long_listing:
		for m in matched:
			ar.output_line('%s' % (m,))
		return None

	folders, files, bytes = 0, 0, 0
	for m in matched:
		hr = hb.open_role(m, None, None)
		fo, fi, by = ar.shape_of_folder(hr.role_logs.path)
		ar.output_line('%-24s %s (%d/%d/%d)' % (m, hr.properties.executable, 1 + fo, fi, by))
		folders += 1 + fo
		files += fi
		bytes += by
	ar.output_line('%-24s (%d/%d/%d)' % ('totals', folders, files, bytes))

	return None

def procedure_destroy(self, destroy_, force, home):
	home = ar.word_argument_2(home, destroy_.home_path, DEFAULT_HOME, HOME)

	hb = open_home(home)

	matched = [g for g in hb.group_list()]
	_, running = role_status(self, hb, matched)
	if running:
		if not force:
			s = lor(list(running.keys()))
			e = ar.Failed(home_delete=(None, f'groups "{s}" are running, use "--force" or "stop"'))
			raise ar.Incomplete(e)

		for k, v in running.items():
			os.kill(v[0].pid, signal.SIGINT)

		group_cleared(self, hb, running)

	self.console(f'Destroying "{hb.home_path}"')

	# Can now remove without side-effects from
	# operational processes.
	hb.destroy_plan()
	return None

def procedure_run(self, run, role_search, ls):
	home = ar.word_argument_2(None, run.home_path, DEFAULT_HOME, HOME)

	group_name = run.group_name or 'default'
	if '.' in group_name:
		e = ar.Rejected(group_name=(group_name, f'no-dots name'))
		raise ar.Incomplete(e)
	group_role = f'group.{group_name}'

	hb = open_home(home)

	if run.create_group:
		_, running = role_status(self, hb, [group_role])
		if running:
			e = ar.Failed(group_start=(f'group "{group_name}" is already running', None))
			raise ar.Incomplete(e)

		try:
			a = self.create(Process, 'ansar-group',	
						origin=RUN_ORIGIN,
						home_path=hb.home_path, role_name=group_role, subrole=False,
						settings=[f'--roles='])

			# Wait.
			m = self.select(Completed, Stop)
			if isinstance(m, Stop):
				self.send(m, a)
				m = self.select(Completed)

			# Process.
			output = m.value
		finally:
			pass

		if not isinstance(output, Ack):
			e = ar.Failed(group_create=(None, f'unexpected {ar.tof(output)} from group creation process'))
			raise ar.Incomplete(e)
		
		return None

	search, matched = find_role(hb, role_search,
		groups=False,
		subroles=False,
		executable=run.executable,
		flip=run.invert_search)

	if not matched:
		e = ar.Failed(group_run=(None, f'no matches for {search}'))
		raise ar.Incomplete(e)

	_, running = role_status(self, hb, [group_role])
	if running:
		e = ar.Failed(group_start=(f'group "{group_name}" is already running', None))
		raise ar.Incomplete(e)

	_, running = role_status(self, hb, matched)
	if running:
		s = lor(list(running.keys()))
		e = ar.Failed(group_start=(None, f'role(s) "{s}" already running in a different group'))
		raise ar.Incomplete(e)

	s = lor(matched)
	self.console(f'Running "{s}" (group {group_name}) at "{hb.home_path}", searched for "{search}"')

	csv = ','.join(matched)
	ls.append(f'--roles={csv}')

	if run.main_role:
		if run.main_role not in matched:
			s = lor(matched)
			e = ar.Rejected(main_role=(run.main_role, f'[{s}]'))
			raise ar.Incomplete(e)
		ls.append(f'--main-role={run.main_role}')
		if run.forwarding:
			ls.append(f'--forwarding')

	try:
		a = self.create(Process, 'ansar-group',	
					origin=RUN_ORIGIN,
					home_path=hb.home_path, role_name=group_role, subrole=False,
					settings=ls)

		# Wait.
		m = self.select(Completed, Stop)
		if isinstance(m, Stop):
			self.send(m, a)
			m = self.select(Completed)

		# Process.
		output = m.value
	finally:
		pass

	if not isinstance(output, GroupRun):
		# This includes None, faults and
		# whatever may be returned by a "main-role".
		return output

	# Look for roles that generated test reports and collate
	# that into a full test suite.
	suite = TestSuite()

	# If provided, improve the quality of test information by
	# augmenting module names with their full path.
	lf = {}
	if run.code_path:
		lf = long_form(run.code_path)

	# Compile the results from tests across all the
	# completed processes.
	for role, value in output.completed.items():
		suite.role.append(role)
		if isinstance(value, TestReport):
			suite.report[role] = value
			for t in value.tested:
				t.source = lf.get(t.source, t.source)
				if t.condition:
					suite.passed += 1
				else:
					suite.failed += 1
					s = f'{t.source}:{t.line} - {t.text}'
					suite.navigation.append(s)

	if run.test_analyzer:
		#executable = object_resolve(run.test_analyzer)
		executable = hb.resolve_executable(run.test_analyzer)
		a = self.create(Process, executable, origin=RUN_ORIGIN, input=suite, debug=run.debug_level)
		self.assign(a, suite)
		r = self.select(Completed, Stop)

		if isinstance(r, Stop):
			abort(self)
			value = Aborted()
		else:
			s = self.debrief()
			value = r.value
			if not ar.is_message(value):
				t = ar.tof(value)
				value = ar.Faulted(f'unexpected completion of "{m}" ({t})')

		return value

	# Report test results rather than table of completions.
	if run.test_run:
		return suite
	return output

def procedure_start(self, start, role_search, ls):
	home = ar.word_argument_2(None, start.home_path, DEFAULT_HOME, HOME)

	group_name = start.group_name or 'default'
	if '.' in group_name:
		e = ar.Rejected(group_name=(group_name, f'no-dots name'))
		raise ar.Incomplete(e)
	group_role = f'group.{group_name}'

	hb = open_home(home)

	# Search the given home finding matches or all. Default behaviour is
	# to skip the sub-roles.
	search, matched = find_role(hb, role_search,
		groups=False,
		subroles=False,
		executable=start.executable,
		flip=start.invert_search)

	if not matched:
		e = ar.Failed(group_start=(None, f'no matches for {search}'))
		raise ar.Incomplete(e)

	_, running = role_status(self, hb, [group_role])
	if running:
		e = ar.Failed(group_start=(f'group "{group_name}" is already running', None))
		raise ar.Incomplete(e)

	_, running = role_status(self, hb, matched)
	if running:
		s = lor(list(running.keys()))
		e = ar.Failed(group_start=(f'roles "{s}" already running in a different group', None))
		raise ar.Incomplete(e)

	s = lor(matched)
	self.console(f'Starting "{s}" (group {group_name}) at "{hb.home_path}", searched for "{search}"')

	csv = ','.join(matched)
	ls.append(f'--roles={csv}')

	if start.main_role:
		if start.main_role not in matched:
			s = lor(matched)
			e = ar.Rejected(main_role=(start.main_role, f'[{s}]'))
			raise ar.Incomplete(e)
		ls.append(f'--main-role={start.main_role}')

	try:
		#executable = object_resolve('ansar-group')
		#executable = hb.resolve_executable('ansar-group')
		a = self.create(Process, 'ansar-group',	
					origin=START_ORIGIN,
					home_path=hb.home_path, role_name=group_role, subrole=False,
					settings=ls)

		# Wait for Ack from new process to verify that
		# framework is operational.
		m = self.select(Completed, Stop)
		if isinstance(m, Stop):
			# Honor the slim chance of a control-c before
			# the framework can respond.
			self.send(m, a)
			m = self.select(Completed)

		# Process.
		value = m.value
		if isinstance(value, Ack):	   # New instance established itself.
			pass
		elif isinstance(value, ar.Faulted):
			raise ar.Incomplete(value)
		elif isinstance(value, LockedOut):
			e = ar.Failed(role_lock=(None, f'"{group_role}" already running as <{value.pid}>'))
			raise ar.Incomplete(e)
		else:
			e = ar.Failed(role_execute=(value, f'unexpected response from "{group_role}" ({executable})'))
			raise ar.Incomplete(e)
	finally:
		pass

	return None

def procedure_pause(self, pause, force, role_search, home):
	home = ar.word_argument_2(None, pause.home_path, DEFAULT_HOME, HOME)

	hb = open_home(home)

	# Search the given home finding matches or all. Default behaviour is
	# to skip the sub-roles.
	search, matched = find_role(hb, role_search,
		groups=False,
		subroles=False,
		executable=pause.executable,
		flip=pause.invert_search)

	if not matched:
		e = ar.Failed(role_search=(None, f'no matches for "{search}"'))
		raise ar.Incomplete(e)

	s = lor(matched)
	self.console(f'Pausing "{s}" at "{hb.home_path}", searched for "{search}"')

	group_pause(self, hb, matched, force)

	return None

def procedure_resume(self, resume, force, group_search):
	home = ar.word_argument_2(None, resume.home_path, DEFAULT_HOME, HOME)

	hb = open_home(home)
	if not group_search:
		matched = [r for r in hb.role_list() if r.startswith('group.')]
		search = '(all)'
	else:
		#for g in group_search:
		#	if '.' in g:
		#		e = ar.Rejected(group_name=(g, f'no-dots name'))
		#		raise ar.Incomplete(e)
		group_role = [f'group.{g}' for g in group_search]

		search, matched = find_role(hb, group_role,
			groups=True)

	if not matched:
		e = ar.Failed(group_search=(None, f'no matches for "{search}"'))
		raise ar.Incomplete(e)

	_, running = role_status(self, hb, matched)
	s = lor(matched)
	if len(running) != len(matched) and not force:
		e = ar.Failed(group_resume=(None, f'not all of matched groups "{s}" are running, use "--force"'))
		raise ar.Incomplete(e)

	self.console(f'Resuming groups "{s}" ({hb.home_path})')
	if not running:
		return None

	for k, v in running.items():
		os.kill(v[0].pid, signal.SIGUSR2)

	return None

def procedure_stop(self, stop, group_search):
	home = ar.word_argument_2(None, stop.home_path, DEFAULT_HOME, HOME)

	hb = open_home(home)
	if not group_search:
		matched = [r for r in hb.role_list() if r.startswith('group.')]
		search = '(all)'
	else:
		#for g in group_search:
		#	if '.' in g:
		#		e = ar.Rejected(group_name=(g, f'no-dots name'))
		#		raise ar.Incomplete(e)
		group_role = [f'group.{g}' for g in group_search]

		search, matched = find_role(hb, group_role,
			groups=True)

	if not matched:
		e = ar.Failed(group_search=(None, f'no matches for "{search}"'))
		raise ar.Incomplete(e)

	_, running = role_status(self, hb, matched)

	s = lor(matched)
	self.console(f'Stopping groups "{s}" ({hb.home_path})')

	if not running:
		return None

	for k, v in running.items():
		os.kill(v[0].pid, signal.SIGINT)

	group_cleared(self, hb, running)

	return None

def short_delta(d):
	t = ar.span_to_text(d.total_seconds())
	i = t.find('d')
	if i != -1:
		j = t.find('h')
		if j != -1:
			return t[:j + 1]
		return t[:i + 1]
	i = t.find('h')
	if i != -1:
		j = t.find('m')
		if j != -1:
			return t[:j + 1]
		return t[:i + 1]
	# Minutes or seconds only.
	i = t.find('.')
	if i != -1:
		i += 1
		j = t.find('s')
		if j != -1:
			e = j - i
			e = min(1, e)
			return t[:i + e] + 's'
		return t[:i] + 's'

def procedure_status(self, list_, role_search):
	home = ar.word_argument_2(None, list_.home_path, DEFAULT_HOME, HOME)

	hb = open_home(home)

	# Find matches or all.
	search, matched = find_role(hb, role_search,
		groups=list_.groups,
		subroles=list_.all_roles,
		executable=list_.executable,
		flip=list_.invert_search)
	matched.sort()

	_, running = role_status(self, hb, matched)

	now = datetime.datetime.now(ar.UTC)
	def long_status():
		for m in matched:
			try:
				v, s0 = running[m]
			except KeyError:
				continue

			if s0 is not None:
				d = now - s0
				s = '%s' % (short_delta(d),)
			else:
				s = '(never started)'
			def dq(pid):
				if pid is None:
					return '0'
				return f'{pid}'
			ar.output_line('%-24s <%s> (%s) %s' % (m, dq(v.pid), dq(v.group_pid), s))

	def short_status():
		for m in matched:
			try:
				v, s0 = running[m]
			except KeyError:
				continue

			ar.output_line(m)

	s = lor(matched)
	self.console(f'Status "{s}" ({hb.home_path}), searched for "{search}"')

	if list_.long_listing:
		long_status()
	else:
		short_status()
	return None

def procedure_history(self, list_, role, home):
	role = ar.word_argument_2(role, list_.role_name, None, ROLE)
	home = ar.word_argument_2(home, list_.home_path, DEFAULT_HOME, HOME)

	hr = open_role(role, home)

	def long_history():
		now = datetime.datetime.now(ar.UTC)
		for s in hr.properties.start_stop:
			start = ar.world_to_text(s.start)
			if s.stop is None:
				ar.output_line('%s ... ?' % (start,))
				continue
			stop = ar.world_to_text(s.stop)
			d = s.stop - s.start
			span = '%s' % (short_delta(d),)
			if isinstance(s.returned, ar.Incognito):
				ar.output_line('%s ... %s (%s) %s' % (start, stop, span, s.returned.type_name))
			else:
				ar.output_line('%s ... %s (%s) %s' % (start, stop, span, s.returned.__class__.__name__))

	def short_history():
		for i, s in enumerate(hr.properties.start_stop):
			now = datetime.datetime.now(ar.UTC)
			d = now - s.start
			start = '%s ago' % (short_delta(d),)
			if s.stop is None:
				ar.output_line('[%d] %s ... ?' % (i, start))
				continue
			d = s.stop - s.start
			stop = short_delta(d)
			if isinstance(s.returned, ar.Incognito):
				ar.output_line('[%d] %s ... %s (%s)' % (i, start, stop, s.returned.type_name))
			else:
				ar.output_line('[%d] %s ... %s (%s)' % (i, start, stop, s.returned.__class__.__name__))

	self.console(f'History for "{hr.role_name}" ({hr.home.home_path})')

	if list_.long_listing:
		long_history()
	else:
		short_history()
	return None

def procedure_returned(self, returned, role, home):
	role = ar.word_argument_2(role, returned.role_name, None, ROLE)
	if role is None:
		r = ar.Rejected(role=(None, 'name'))
		raise ar.Incomplete(r)
	home = ar.word_argument_2(home, returned.home_path, DEFAULT_HOME, HOME)
	timeout = ar.word_argument_2(None, returned.timeout, None, ROLE)
	start = ar.word_argument_2(None, returned.start, None, HOME)

	hr = open_role(role, home)

	start_stop = hr.properties.start_stop
	if len(start_stop) < 1:
		e = ar.Failed(history_access=(None, f'role "{role}" has no start/stop records'))
		raise ar.Incomplete(e)

	ls = len(start_stop) - 1	# Last stop
	if start is None:
		start = ls
	elif start < 0:
		start = ls + 1 + start

	if start < 0 or start > ls:
		raise ar.Incomplete(ar.Rejected(start=(start, (0, ls))))

	# Criteria met - valid row in the table.
	start_stop = hr.properties.start_stop
	selected = start_stop[start]
	anchor = selected.start

	# This row has already returned.
	if selected.stop is not None:
		return selected.returned

	# Cannot poll for completion of anything other
	# than the last row.
	start_stop = hr.properties.start_stop
	if start != ls:
		raise ar.Incomplete(ar.Faulted('no record of role stopping at [{start}]', 'never will be'))

	if timeout is not None:
		self.start(T1, timeout)

	self.start(T2, 1.0)
	while True:
		m = self.select(Stop, T1, T2)
		if isinstance(m, Stop):
			break
		elif isinstance(m, T1):
			returned(TimedOut())
			return 1
		elif isinstance(m, T2):
			r, v = ar.recover_property(hr.properties, hr.role_entry, 'start_stop')
			if len(r) < start:
				raise ar.Incomplete(ar.Faulted('lost original start position', 'index out-of-range'))
			if r[start].start != anchor:
				raise ar.Incomplete(ar.ar.Faulted('lost original start position', 'datetime anchor'))
			if r[start].stop is not None:
				returned(r[start].returned)
				break
			self.start(T2, 1.0)

	return None

# Logging starts here with supporting
# functions.
def from_last(last):
	d = datetime.datetime.now(ar.UTC)

	if last == START_OF.MONTH:
		f = datetime.datetime(d.year, d.month, 1, tzinfo=d.tzinfo)
	elif last == START_OF.WEEK:
		dow = d.weekday()
		dom = d.day - 1
		if dom >= dow:
			f = datetime.datetime(d.year, d.month, d.day - dow, tzinfo=d.tzinfo)
		elif d.month > 1:
			t = dow - dom
			r = calendar.monthrange(d.year, d.month - 1)
			f = datetime.datetime(d.year, d.month - 1, r[1] - t, tzinfo=d.tzinfo)
		else:
			t = dow - dom
			r = calendar.monthrange(d.year - 1, 12)
			f = datetime.datetime(d.year - 1, 12, r[1] - t, tzinfo=d.tzinfo)
	elif last == START_OF.DAY:
		f = datetime.datetime(d.year, d.month, d.day, tzinfo=d.tzinfo)
	elif last == START_OF.HOUR:
		f = datetime.datetime(d.year, d.month, d.day, hour=d.hour, tzinfo=d.tzinfo)
	elif last == START_OF.MINUTE:
		f = datetime.datetime(d.year, d.month, d.day, hour=d.hour, minute=d.minute, tzinfo=d.tzinfo)
	elif last == START_OF.HALF:
		t = d.minute % 30
		m = d.minute - t
		f = datetime.datetime(d.year, d.month, d.day, hour=d.hour, minute=m, tzinfo=d.tzinfo)
	elif last == START_OF.QUARTER:
		t = d.minute % 15
		m = d.minute - t
		f = datetime.datetime(d.year, d.month, d.day, hour=d.hour, minute=m, tzinfo=d.tzinfo)
	elif last == START_OF.TEN:
		t = d.minute % 10
		m = d.minute - t
		f = datetime.datetime(d.year, d.month, d.day, hour=d.hour, minute=m, tzinfo=d.tzinfo)
	elif last == START_OF.FIVE:
		t = d.minute % 5
		m = d.minute - t
		f = datetime.datetime(d.year, d.month, d.day, hour=d.hour, minute=m, tzinfo=d.tzinfo)
	else:
		return None
	return f

#
#
def clocker(self, hr, begin, end, count):
	try:
		for d, t in read_log(hr.role_logs, begin, end, count):
			if self.halted:
				return Aborted()
			c = d.astimezone(tz=None)		   # To localtime.
			s = c.strftime('%Y-%m-%dt%H:%M:%S') # Normal part.
			f = c.strftime('%f')[:3]			# Up to milliseconds.
			h = '%s.%s' % (s, f)
			i = t.index(' ')
			ar.output_line(h, newline=False)
			ar.output_line(t[i:], newline=False)
	except (KeyboardInterrupt, SystemExit) as e:
		raise e
	except Exception as e:
		condition = str(e)
		fault = ar.Faulted(condition)
		return fault
	return None

bind_any(clocker)

#
#
def printer(self, hr, begin, end, count):
	try:
		for _, t in read_log(hr.role_logs, begin, end, count):
			if self.halted:
				return Aborted()
			ar.output_line(t, newline=False)
	except (KeyboardInterrupt, SystemExit) as e:
		raise e
	except Exception as e:
		condition = str(e)
		fault = ar.Faulted(condition)
		return fault
	return None

bind_any(printer)

#
#
def world_or_clock(s, clock):
	if clock:
		t = ar.text_to_clock(s)
		d = datetime.datetime.fromtimestamp(t, tz=ar.UTC)
		return d
	return ar.text_to_world(s)

def procedure_log(self, log, role, home):
	role = ar.word_argument_2(role, log.role_name, None, ROLE)
	home = ar.word_argument_2(home, log.home_path, DEFAULT_HOME, HOME)
	if not role:
		s = 'a <role> is required'
		raise ar.Incomplete(ar.Faulted(s))

	hr = open_role(role, home)

	begin, end = None, None
	if log.from_ is not None:
		begin = world_or_clock(log.from_, log.clock)
		self.console('Beginning at from')
	elif log.last is not None:
		begin = from_last(log.last)
		if begin is None:
			e = ar.Rejected(last=(None, list(START_OF.kv.items())))
			raise ar.Incomplete(e)
		self.console('Beginning at LAST')
	elif log.start is not None:
		start_stop = hr.properties.start_stop
		if len(start_stop) < 1:
			e = ar.Faulted('history access', f'{role} has no history')
			raise ar.Incomplete(e)
		if log.start < 0:
			y = len(start_stop) + log.start
		else:
			y = log.start
		try:
			s = start_stop[y]
		except IndexError:
			ln = len(start_stop)
			e = ar.Rejected(start=(log.start, (0, ln - 1)))
			raise ar.Incomplete(e)
		begin = s.start
		p1 = y + 1
		if p1 < len(start_stop):
			end = start_stop[p1].start
		else:
			end = None
		self.console('Beginning at START')
	elif log.back is not None:
		d = datetime.datetime.now(ar.UTC)
		t = datetime.timedelta(seconds=log.back)
		begin =  d - t
		self.console('Beginning at BACK')

	count = None
	if log.to is not None:
		end = world_or_clock(log.to, log.clock)
		self.console('Ending at TO')
	elif log.span is not None:
		t = datetime.timedelta(seconds=log.span)
		end = begin + t
		self.console('Ending at SPAN')
	elif log.count is not None:
		count = log.count
		# Override an assignment associated with "start".
		end = None
		self.console('Ending on COUNT')
	# Else
	#   end remains as the default None or
	#   the stop part of a start-stop.

	# Now that <begin> and <end> have been established, a
	# few more sanity checks.
	if begin is None:
		e = ar.Failed(start_mark=(None, f'<begin> not defined and not inferred'))
		raise ar.Incomplete(e)

	if end is not None and end < begin:
		e = ar.Failed(mark_order=(None, f'<end> comes before <begin>'))
		raise ar.Incomplete(e)

	self.console(f'Extracting logs "{hr.role_name}" ({hr.home.home_path})')

	if log.clock:
		a = self.create(clocker, hr, begin, end, count)
	else:
		a = self.create(printer, hr, begin, end, count)
	m = self.select(Stop, Completed)
	if isinstance(m, Stop):
		halt(a)
		m = self.select(Completed)
		raise ar.Incomplete(Aborted())
	value = m.value
	if value is None:   # Reached the end.
		pass
	elif isinstance(value, ar.Faulted):	 # ar.Failed to complete stream.
		raise ar.Incomplete(value)
	else:
		e = ar.Failed(log_read=(value, f'unexpected reader response'))
		raise ar.Incomplete(e)

	return None

def procedure_folder(self, list_, selected, role, home):
	selected = ar.word_argument_2(selected, None, None, FOLDER)
	role = ar.word_argument_2(role, list_.role_name, None, ROLE)
	home = ar.word_argument_2(home, list_.home_path, DEFAULT_HOME, HOME)
	if selected is None:
		r = ar.Rejected(folder=(None, 'name'))
		raise ar.Incomplete(r)
	if role is None:
		r = ar.Rejected(role=(None, 'name'))
		raise ar.Incomplete(r)

	hr = open_role(role, home)

	self.console(f'Folder "{selected}", for "{role}" ({hr.home.home_path})')

	# All the folders that *might* be part of this
	# role context.

	folder = {
		'bin': hr.home.bin,
		'settings': hr.role_settings,
		'logs': hr.role_logs,
		'tmp': hr.role_tmp,
		'model': hr.role_model,
		'resource': hr.role_resource,
	}
	# Filter out the unavailable folders.
	possibles = [k for k, v in folder.items() if isinstance(v, ar.Folder)]
	if selected not in possibles:
		e = ar.Rejected(folder=(selected, possibles))
		raise ar.Incomplete(e)

	# Finally. Have a folder, print the filesystem location.
	ar.output_line('%s' % (folder[selected].path,))

	return None

def procedure_input(self, input, force, role, home):
	role = ar.word_argument_2(role, input.role_name, None, ROLE)
	home = ar.word_argument_2(home, input.home_path, DEFAULT_HOME, HOME)

	search = '(all)' if role is None else role
	hb = open_home(home)

	# Find matches or all.
	matched = find_files(role, hb.input)
	if not matched:
		e = ar.Failed(role_search=(None, f'no input for "{search}"'))
		raise ar.Incomplete(e)

	s = lor(matched)
	self.console(f'Input "{s}" ({hb.home_path})')

	if input.input_file:
		file_settings = [
			f'--input-file={input.input_file}',
			'--store-input=true',
		]
	else:   # Get file.
		if len(matched) != 1:
			n = len(matched)
			e = ar.Failed(role_search=(None, f'matched {n} roles'))
			raise ar.Incomplete(e)
		# Cant use sub-process as encoding is placed on stdout.
		m = matched[0]
		input_change = os.path.join(hb.input.path, m + '.json')
		try:
			with open(input_change, 'r') as f:
				s = f.read()
		except OSError as e:
			raise ar.Incomplete(ar.Failed(file_read=(e, None)))
		ar.output_line(s)
		return None

	_, running = group_pause(self, hb, matched, force)
	try:
		for m in matched:
			hr = hb.open_role(m, None, None)
			executable = hr.properties.executable
			if input.executable and executable != input.executable:
				continue
			#executable = object_resolve(executable)
			executable = hb.resolve_executable(executable)

			self.console(f'Running "{executable}" ({m}) to update input')
			a = self.create(Process, executable,
				origin=RUN_ORIGIN,
				home_path=hb.home_path, role_name=hr.role_name,
				settings=file_settings)
			self.assign(a, hr.role_name)
			r = self.select(Completed, Stop)
			if isinstance(r, Stop):
				raise ar.Incomplete(Aborted())

			# Process completed. Remove record.
			m = self.debrief()
			value = r.value
			if isinstance(value, Ack):
				pass
			elif isinstance(value, ar.Faulted):
				raise ar.Incomplete(value)
			elif isinstance(value, LockedOut):
				e = ar.Failed(role_lock=(None, f'"{m}" already running as <{value.pid}>'))
				raise ar.Incomplete(e)
			else:
				e = ar.Failed(role_execute=(value, f'unexpected response from "{m}" ({executable})'))
				raise ar.Incomplete(e)
	finally:
		abort(self)
		group_resume(self, running)

	return None

def procedure_settings(self, settings, force, role, home):
	role = ar.word_argument_2(role, settings.role_name, None, ROLE)
	home = ar.word_argument_2(home, settings.home_path, DEFAULT_HOME, HOME)

	search = '(all)' if role is None else role
	hb = open_home(home)

	# Find matches or all.
	matched = find_files(role, hb.settings)
	if not matched:
		e = ar.Failed(role_search=(None, f'no settings for "{search}"'))
		raise ar.Incomplete(e)

	s = lor(matched)
	self.console(f'Settings "{s}" ({home})')

	if settings.settings_file:
		file_settings = [
			f'--settings-file={settings.settings_file}',
			'--store-settings=true',
		]
	else:   # Get file.
		if len(matched) != 1:
			n = len(matched)
			e = ar.Failed(role_search=(None, f'matched {n} roles'))
			raise ar.Incomplete(e)
		# Cant use sub-process as encoding is placed on stdout.
		m = matched[0]
		settings_change = os.path.join(hb.settings.path, m + '.json')
		try:
			with open(settings_change, 'r') as f:
				s = f.read()
		except OSError as e:
			raise ar.Incomplete(ar.Failed(file_read=(e, None)))
		ar.output_line(s)
		return None

	_, running = group_pause(self, hb, matched, force)
	try:
		for m in matched:
			hr = hb.open_role(m, None, None)
			executable = hr.properties.executable
			if settings.executable and executable != settings.executable:
				continue
			#executable = object_resolve(executable)
			executable = hb.resolve_executable(executable)

			self.console(f'Running "{executable}" ({m}) to update settings')
			a = self.create(Process, executable, origin=RUN_ORIGIN,
				home_path=hb.home_path, role_name=hr.role_name,
				settings=file_settings)
			self.assign(a, hr.role_name)
			r = self.select(Completed, Stop)
			if isinstance(r, Stop):
				raise ar.Incomplete(Aborted())

			# Process completed. Remove record.
			m = self.debrief()
			value = r.value
			if isinstance(value, Ack):
				pass
			elif isinstance(value, ar.Faulted):
				raise ar.Incomplete(value)
			elif isinstance(value, LockedOut):
				e = ar.Failed(role_lock=(None, f'"{m}" already running as <{value.pid}>'))
				raise ar.Incomplete(e)
			else:
				e = ar.Failed(role_execute=(value, f'unexpected response from "{m}" ({executable})'))
				raise ar.Incomplete(e)
	finally:
		abort(self)
		group_resume(self, running)

	return None

def store(v, t=None, pretty=False):
	codec = ar.CodecJson(pretty_format=pretty)
	t = t or ar.UserDefined(type(v))
	s = codec.encode(v, t)
	if pretty:
		s += '\n'
	return s

def recover(s, c, t=None):
	codec = ar.CodecJson()
	t = t or ar.UserDefined(type(c))
	v, a = codec.decode(s, t)
	return v, a

def procedure_get(self, properties, set_, selected, role, home):
	selected = ar.word_argument_2(selected, set_.property, None, PROPERTY)
	role = ar.word_argument_2(role, set_.role_name, None, ROLE)
	home = ar.word_argument_2(home, set_.home_path, DEFAULT_HOME, HOME)

	if selected is None:
		e = ar.Rejected(get_property=(None, 'a <property> is required'))
		raise ar.Incomplete(e)
	selected = selected.replace('-', '_')
	selected = selected.strip()

	if role is None:
		e = ar.Rejected(get_role=(None, 'a <role> is required'))
		raise ar.Incomplete(e)

	hb = open_home(home)
	hr = hb.open_role(role, None, None, properties())
	properties = hr.properties

	# Verify the chosen property.
	if not hasattr(properties, selected):
		e = ar.Rejected(property=(selected, list(properties.__dict__)))
		raise ar.Incomplete(e)

	self.console(f'Get property "{selected}" ({hr.role_name}, {hr.home.home_path})')

	# Convert name to runtime value.
	try:
		t = properties.__art__.value[selected]
		v = getattr(properties, selected)
	except (AttributeError, KeyError):
		s = ar.tof(properties)
		raise ar.Incomplete(ar.Failed(property_type=(None, 'type "{s}" not registered?')))
	except ar.CodecFailed as e:
		raise ar.Incomplete(ar.Failed(property_encode=(e, None)))

	ar.output_encode(v, t=t)
	return None

READ_ONLY = [
	"id",
	"created",
	"executable",
]

def procedure_set(self, properties, set_, force, selected, role_search, js):
	if selected is None:
		e = ar.Rejected(set_property=(None, 'a <property> is required'))
		raise ar.Incomplete(e)
	if len(role_search) < 1:
		e = ar.Rejected(set_role=(None, 'at least one <role> is required'))
		raise ar.Incomplete(e)

	selected = selected.replace('-', '_')
	selected = selected.strip()
	if selected in READ_ONLY:
		e = ar.Rejected(set_property=(selected, 'read-only property'))
		raise ar.Incomplete(e)

	home = ar.word_argument_2(None, set_.home_path, DEFAULT_HOME, HOME)

	hb = open_home(home)

	try:
		t = properties.__art__.value[selected]
	except (KeyError, TypeError, AttributeError) as e:
		e = ar.Failed(role_properties=(e, f'no type information for "{selected}"'))
		raise ar.Incomplete(e)

	value = None
	if js is not None:
		try:
			value, _ = recover(js, None, t=t)
		except ar.CodecError as e:
			e = ar.Failed(property_decode=(e, f'JSON encoding of "{selected}"'))
			raise ar.Incomplete(e)

	# Find matches or all.
	search, matched = find_role(hb, role_search,
		groups=True,
		subroles=True,
		executable=set_.executable,
		flip=set_.invert_search)
	if not matched:
		e = ar.Failed(role_search=(None, f'no match for "{search}"'))
		raise ar.Incomplete(e)

	s = lor(matched)
	self.console(f'Set property "{selected}" (roles {s}), searched for "{search}"')

	_, running = group_pause(self, hb, matched, force)
	try:
		for m in matched:
			hr = hb.open_role(m, None, None, properties=properties())
			store_property(hr.properties, hr.role_entry, selected, value)
	except OSError as e:
		raise ar.Incomplete(ar.Failed(property_delete=(e, None)))
	except (ar.CodecFailed, ar.FileFailure) as e:
		raise ar.Incomplete(ar.Failed(property_store=(e, None)))
	finally:
		group_resume(self, running)

	return None

def procedure_edit(self, properties, edit, force, selected, role, home):
	selected = ar.word_argument_2(selected, edit.property, None, PROPERTY)
	role = ar.word_argument_2(role, edit.role_name, None, ROLE)
	home = ar.word_argument_2(home, edit.home_path, DEFAULT_HOME, HOME)

	if selected is None:
		e = ar.Rejected(edit_property=(None, 'a <property> is required'))
		raise ar.Incomplete(e)

	if role is None:
		e = ar.Rejected(edit_role=(None, 'a <role> is required'))
		raise ar.Incomplete(e)

	selected = selected.replace('-', '_')
	selected = selected.strip()
	if selected in READ_ONLY:
		e = ar.Rejected(edit_property=(selected, 'read-only property'))
		raise ar.Incomplete(e)

	hr = open_role(role, home, properties=properties())

	try:
		t = properties.__art__.value[selected]
		v = getattr(hr.properties, selected)
	except KeyError:
		raise ar.Incomplete(ar.Failed(property_type=(selected, 'no type information available')))
	except AttributeError:
		raise ar.Incomplete(ar.Failed(property_value=(selected, 'no such property')))

	_, running = group_pause(self, hr.home, [role], force)
	editor = os.getenv('ANSAR_EDITOR') or 'vi'

	self.console(f'Editing property "{selected}", "{role}" ({hr.home.home_path}) using editor "{editor}"')
	try:
		fd, name = tempfile.mkstemp()
		os.close(fd)

		# Prepare materials for editor.
		temporary = ar.File(name, t, decorate_names=False)
		if v is not None:
			temporary.store(v)
		else:
			temporary.store(ar.make(t))

		# Setup detection of change.
		modified = os.stat(name).st_mtime

		# Run the editor.
		self.console('Run the editor')
		a = self.create(Utility, editor, name)
		self.assign(a, editor)
		m = self.select(Completed, ar.Faulted)

		e = self.debrief()
		value = m.value
		if isinstance(value, ar.Faulted):
			raise ar.Incomplete(value)

		# Was the file modified?
		if os.stat(name).st_mtime == modified:
			raise ar.Incomplete(ar.Failed(property_store=(None, f'value for "{selected}" not modified')))

		# Validate contents and update the runtime.
		self.console('Parse the materials before setting')
		a, _ = temporary.recover()
		hr.store(selected, a)
	except (ar.CodecFailed, ar.FileFailure) as e:
		raise ar.Incomplete(ar.Failed(property_store=(e, None)))
	finally:
		os.remove(name)
		group_resume(self, running)

	return None

# DEPLOY
# Transfer machinery
def folder_transfer(self, delta, target):
	"""An async routine to copy folders-and-files to target folder."""

	# Interruption happens at the lowest level of transfer activity, i.e before
	# each IO operation (i.e. read or write of blocks). Parent object calls
	# a halt() on this object and the halted flag is checked by every delta
	# opcode (e.g. storage.AddFile) before every IO. If halted it raises the special
	# TransferHalted exception to jump back to this code.
	machine = DeltaMachine(self, target)
	try:
		deltas = len(delta)
		self.console(f'File transfer ({deltas} deltas) to {target}')
		for d in delta:
			d(machine)
			aliases = machine.aliases()
		self.console(f'Move {aliases} aliases to targets')
		machine.rename()
	except ar.TransferHalted:
		return Aborted()
	except OSError as e:
		condition = str(e)
		fault = ar.Faulted(condition)
		return fault
	finally:
		aliases = machine.aliases()
		self.console(f'Clear {aliases} aliases')
		machine.clear()
	return Ack()

bind_any(folder_transfer)

class INITIAL: pass
class RUNNING: pass
class HALTED: pass

class FolderTransfer(Point, StateMachine):
	def __init__(self, delta, target):
		Point.__init__(self)
		StateMachine.__init__(self, INITIAL)
		self.delta = delta
		self.target = target
		self.transfer = None

def FolderTransfer_INITIAL_Start(self, message):
	self.transfer = self.create(folder_transfer, self.delta, self.target)
	return RUNNING

def FolderTransfer_RUNNING_Completed(self, message):
	value = message.value
	self.complete(value)

def FolderTransfer_RUNNING_Stop(self, message):
	halt(self.transfer)
	return HALTED

def FolderTransfer_HALTED_Completed(self, message):
	self.complete(Aborted())

FOLDER_TRANSFER_DISPATCH = {
	INITIAL: (
		(Start,), ()
	),
	RUNNING: (
		(Completed, Stop), ()
	),
	HALTED: (
		(Completed,), ()
	),
}

bind_any(FolderTransfer, FOLDER_TRANSFER_DISPATCH)

#
#
class STOPPED: pass

class SettingsTransfer(Point, StateMachine):
	def __init__(self, hb, role, executable, settings_change, setting_values):
		Point.__init__(self)
		StateMachine.__init__(self, INITIAL)
		self.hb = hb
		self.role = role
		self.executable = executable
		self.settings_change = settings_change
		self.setting_values = setting_values
		self.transfer = None

def SettingsTransfer_INITIAL_Start(self, message):
	role = self.role
	executable = self.executable
	settings_change = self.settings_change
	setting_values = self.setting_values

	settings = []
	if settings_change:
		self.console(f'Settings file "{settings_change}" to {role} ({executable})')
		settings.append(f'--settings-file={settings_change}')

	if setting_values:
		values = ', '.join(setting_values.keys())
		self.console(f'Values files "{values}" to {role} ({executable})')
		for s, v in setting_values.items():
			with open(v, "r") as f:
				value = f.read()
			settings.append(f'--{s}={value}')

	settings.append('--store-settings=true')

	self.transfer = self.create(Process, executable, origin=RUN_ORIGIN, debug=object_settings.debug_level,
		home_path=self.hb.home_path, role_name=role,
		settings=settings)
	return RUNNING

def SettingsTransfer_RUNNING_Completed(self, message):
	value = message.value
	self.complete(value)

def SettingsTransfer_RUNNING_Stop(self, message):
	self.send(message, self.transfer)
	return STOPPED

def SettingsTransfer_STOPPED_Completed(self, message):
	self.complete(Aborted())

SETTINGS_TRANSFER_DISPATCH = {
	INITIAL: (
		(Start,), ()
	),
	RUNNING: (
		(Completed, Stop), ()
	),
	STOPPED: (
		(Completed,), ()
	),
}

bind_any(SettingsTransfer, SETTINGS_TRANSFER_DISPATCH)

#
#
class InputTransfer(Point, StateMachine):
	def __init__(self, hb, role, executable, input_change):
		Point.__init__(self)
		StateMachine.__init__(self, INITIAL)
		self.hb = hb
		self.role = role
		self.executable = executable
		self.input_change = input_change
		self.transfer = None

def InputTransfer_INITIAL_Start(self, message):
	role = self.role
	executable = self.executable
	input_change = self.input_change

	settings = []
	self.console(f'Input file "{input_change}" to {role} ({executable})')
	settings.append(f'--input-file={input_change}')

	settings.append('--store-input=true')

	self.transfer = self.create(Process, executable, origin=RUN_ORIGIN, debug=object_settings.debug_level,
			home_path=self.hb.home_path, role_name=role,
			settings=settings)
	return RUNNING

def InputTransfer_RUNNING_Completed(self, message):
	value = message.value
	self.complete(value)

def InputTransfer_RUNNING_Stop(self, message):
	self.send(message, self.transfer)
	return STOPPED

def InputTransfer_STOPPED_Completed(self, message):
	self.complete(Aborted())

INPUT_TRANSFER_DISPATCH = {
	INITIAL: (
		(Start,), ()
	),
	RUNNING: (
		(Completed, Stop), ()
	),
	STOPPED: (
		(Completed,), ()
	),
}

bind_any(InputTransfer, INPUT_TRANSFER_DISPATCH)

#
#
def procedure_deploy(self, deploy, force, build, snapshot, home):
	build = ar.word_argument_2(build, deploy.build_path, None, BUILD)
	snapshot = ar.word_argument_2(snapshot, deploy.snapshot_path, None, SNAPSHOT)
	home = ar.word_argument_2(home, deploy.home_path, DEFAULT_HOME, HOME)

	if build is None and snapshot is None:
		r = ar.Rejected(deploy=(None, 'no <build> and no <snapshot> - nothing to do'))
		raise ar.Incomplete(r)

	hb = open_home(home)

	# Extract the map of role-executable, i.e. many-to-1.
	def executable(r):
		hr = hb.open_role(r, None, None)
		return hr.properties.executable
	role_executable = {r: executable(r) for r in hb.role_list()}

	# And the inverse map, i.e. 1-to-many.
	executable_roles = {}
	for r, e in role_executable.items():
		try:
			roles = executable_roles[e]
		except KeyError:
			roles = set()
			executable_roles[e] = roles
		roles.add(r)

	roles = set(role_executable.keys())
	executables = set(executable_roles.keys())

	# Results of scans for change.
	file_change = []
	settings_change = []
	input_change = []
	setting_value_change = []

	# Unique set of names of the roles affected
	# by the detected changes.
	touching_roles = set()

	def cannot_deploy(bs, fs, bt, ft):
		if not bs:
			return f'unexpected source "{fs}"'
		if not bt:
			return 'target not found'
		return 'no error'

	if build:
		build = os.path.abspath(build)
		# Special case of file transfer method.
		SHARED_BIN = DELTA_FILE_ADD | DELTA_FILE_UPDATE	# Cant do DELTA_FILE_UGM, no source.
		s, ugm = storage_manifest(build)
		t, _ = storage_manifest(hb.bin.path)
		delta = [d for d in storage_delta(s, t, flags=SHARED_BIN)]
		changing = set(d.source.name for d in delta)

		if len(changing) > 0:					# There is significant change.
			touched = len(touching_roles)
			for c in changing:					# Executable
				r = executable_roles.get(c)		# Roles configured with.
				if r:
					touching_roles |= r			# Remember.

			todo = (build, hb.bin.path, delta, ugm)		# Record of todo.
			file_change.append(todo)
			cn = len(changing)
			tn = len(touching_roles) - touched
			self.console(f'Detected {cn} changing executables (added {tn} associated roles)')

	# Results of scan without regard to whether something
	# has changed, i.e. this is what is available.
	resource_by_executable = {}
	model_by_role = {}
	settings_by_role = {}
	input_by_role = {}
	setting_value_by_role = {}

	if snapshot:
		snapshot = os.path.abspath(snapshot)
		# Load all the deployment methods defined in this
		# snapshot area.
		method = set(f for f in os.listdir(snapshot))

		# For each method scan for changes and record in the
		# relevant results list.
		if 'resource-by-executable' in method:
			p = os.path.join(snapshot, 'resource-by-executable')

			# It might be possible to treat the entire resource
			# folder as one manifest but determining which
			# executables/roles are changing becomes much harder.
			for executable in os.listdir(p):
				source = os.path.join(p, executable)
				target = os.path.join(hb.resource.path, executable)
				bs, bt = os.path.isdir(source), os.path.isdir(target)
				if not bs or not bt:
					cd = cannot_deploy(bs, 'folder', bt, 'folder')
					self.warning(f'Cannot deploy "resource-by-executable/{executable}" ({cd})')
					continue
				s, ugm = storage_manifest(source)
				t, _ = storage_manifest(target)
				delta = [d for d in storage_delta(s, t)]
				resource_by_executable[executable] = source
				if len(delta) > 0:
					touched = len(touching_roles)
					r = executable_roles.get(executable)
					if r:
						touching_roles |= r
					todo = (source, target, delta, ugm)
					file_change.append(todo)
					dn = len(delta)
					nr = len(touching_roles) - touched
					self.console(f'Detected {dn} resource changes for "{executable}" (added {nr} associated roles)')

		if 'model-by-executable' in method:
			# To be considered. See settings-by-executable.
			pass

		if 'model-by-role' in method:
			p = os.path.join(snapshot, 'model-by-role')
			for role in os.listdir(p):
				source = os.path.join(p, role)
				target = os.path.join(hb.model.path, role)
				bs, bt = os.path.isdir(source), os.path.isdir(target)
				if not bs or not bt:
					cd = cannot_deploy(bs, 'folder', bt, 'folder')
					self.warning(f'Cannot deploy "model-by-role/{role}" ({cd})')
					continue
				s, ugm = storage_manifest(source)
				t, _ = storage_manifest(target)
				delta = [d for d in storage_delta(s, t)]
				model_by_role[role] = source
				if len(delta) > 0:
					touching_roles.add(role)
					todo = (source, target, delta, ugm)
					file_change.append(todo)
					dn = len(delta)
					self.console(f'Detected {dn} model changes for "{role}"')

		# Settings and input.
		if 'settings-by-executable' in method:
			# To be considered. Creates complex relationship between
			# settings for all roles using an executable, specific roles
			# and setting values. And then figure out what should be done
			# when one of these files changes or one of the related
			# setting value files changes.
			pass

		if 'settings-by-role' in method:
			p = os.path.join(snapshot, 'settings-by-role')
			for r in os.listdir(p):
				role, _ = os.path.splitext(r)
				source = os.path.join(p, r)
				target = os.path.join(hb.settings.path, r)
				bs, bt = os.path.isfile(source), os.path.isfile(target)
				if not bs or not bt:
					cd = cannot_deploy(bs, 'file', bt, 'file')
					self.warning(f'Cannot deploy "settings-by-role/{r}" ({cd})')
					continue
				s = os.stat(source)
				t = os.stat(target)
				settings_by_role[role] = source
				if s.st_mtime > t.st_mtime:
					touching_roles.add(role)
					todo = (source, role, None, None)
					settings_change.append(todo)
					self.console(f'Detected settings change for "{role}"')

		if 'setting-value-by-executable' in method:
			# To be considered. See settings-by-executable.
			pass

		if 'setting-value-by-role' in method:
			p = os.path.join(snapshot, 'setting-value-by-role')
			# Each role.
			for role in os.listdir(p):
				role_path = os.path.join(p, role)
				if not os.path.isdir(role_path):
					self.warning(f'Cannot deploy "setting-value-by-role/{role}" (unexpected source)')
					continue
				target = os.path.join(hb.settings.path, role + '.json')
				if not os.path.isfile(target):
					self.warning(f'Cannot deploy "setting-value-by-role/{role}" (target not found)')
					continue
				t = os.stat(target)
				setting_value = {}
				sv = []
				# Each setting.
				for s in os.listdir(role_path):
					setting, _ = os.path.splitext(s)
					source = os.path.join(role_path, s)
					if not os.path.isfile(source):
						self.warning(f'Cannot deploy "setting-value-by-role/{role}/{s}" (unexpected source)')
						continue
					# Value for setting for role.
					v = os.stat(source)
					setting_value[setting] = source
					if v.st_mtime > t.st_mtime:
						todo = (setting, source)
						sv.append(todo)
				setting_value_by_role[role] = setting_value
				if len(sv) > 0:
					touching_roles.add(role)
					todo = (None, role, sv, None)
					setting_value_change.append(todo)
					sn = len(sv)
					self.console(f'Detected {sn} setting-value changes for "{role}"')

		if 'input-by-role' in method:
			p = os.path.join(snapshot, 'input-by-role')
			for r in os.listdir(p):
				role, _ = os.path.splitext(r)
				source = os.path.join(p, r)
				target = os.path.join(hb.input.path, r)
				bs, bt = os.path.isfile(source), os.path.isfile(target)
				if not bs or not bt:
					cd = cannot_deploy(bs, 'file', bt, 'file')
					self.warning(f'Cannot deploy "input-by-role/{r}" ({cd})')
					continue
				s = os.stat(source)
				t = os.stat(target)
				input_by_role[role] = source
				if s.st_mtime > t.st_mtime:
					touching_roles.add(role)
					todo = (source, role, None, None)
					input_change.append(todo)
					self.console(f'Detected input changes for "{role}"')

	if len(file_change) < 1 and len(settings_change) < 1 and len(setting_value_change) < 1 and len(input_change) < 1:
		self.console('Nothing to deploy')
		return None

	tr = [r for r in touching_roles if '.' not in r]
	_, running = group_pause(self, hb, tr, force)

	try:
		self.console('Starting transfer of materials')

		for t in file_change:
			target = t[1]
			delta = t[2]
			a = self.create(FolderTransfer, delta, target)
			self.assign(a, t)

		full_settings = set()
		for s in settings_change:
			source = s[0]
			role = s[1]
			full_settings.add(role)
			# Overlay any defined setting-value content.
			v = setting_value_by_role.get(role)
			a = self.create(SettingsTransfer, hb, role, role_executable[role], source, v)
			self.assign(a, s)

		for rsv in setting_value_change:
			role = rsv[1]
			sv = rsv[2]
			if role in full_settings:
				continue
			v = {s: v for s, v in sv}
			a = self.create(SettingsTransfer, hb, role, role_executable[role], None, v)
			self.assign(a, rsv)

		while self.working():
			m = self.select(Completed, Stop)
			if isinstance(m, Stop):
				raise ar.Incomplete(Aborted())

			# Completed.
			t = self.debrief()
			target = t[1]
			self.console(f'Completed transfer to "{target}"')
			value = m.value
			if isinstance(value, Ack):   # Reached the end.
				pass
			elif isinstance(value, ar.Faulted):	 # ar.Failed to complete transfer.
				fault = str(value)
				target = t[1]
				self.console(f'Fault in transfer to "{target}" ({fault})')
				raise ar.Incomplete(value)
			else:
				raise ar.Incomplete(ar.Failed(file_transfer=(value, 'unexpected response to settings transfer')))

		for i in input_change:
			source = i[0]
			role = i[1]
			a = self.create(InputTransfer, hb, role, role_executable[role], source)
			self.assign(a, i)

		while self.working():
			m = self.select(Completed, Stop)
			if isinstance(m, Stop):
				raise ar.Incomplete(Aborted())

			# Completed.
			t = self.debrief()
			target = t[1]
			self.console(f'Completed transfer to "{target}"')
			value = m.value
			if isinstance(value, Ack):		# Reached the end.
				pass
			elif isinstance(value, ar.Faulted):	# ar.Failed to complete transfer.
				fault = str(value)
				target = t[1]
				self.console(f'Fault in transfer to "{target}" ({fault})')
				raise ar.Incomplete(value)
			else:
				raise ar.Incomplete(ar.Failed(file_transfer=(value, 'unexpected response to input transfer')))
	finally:
		abort(self)
		group_resume(self, running)
	return None

def procedure_snapshot(self, deploy, force, snapshot, home):
	snapshot = ar.word_argument_2(snapshot, deploy.snapshot_path, None, SNAPSHOT)
	home = ar.word_argument_2(home, deploy.home_path, DEFAULT_HOME, HOME)

	if snapshot is None:
		r = ar.Rejected(reference=(None, 'no <snapshot> - nothing to do'))
		raise ar.Incomplete(r)

	hb = open_home(home)

	# Extract the map of role-executable, i.e. many-to-1.
	def executable(r):
		hr = hb.open_role(r, None, None)
		return hr.properties.executable
	role_executable = {r: executable(r) for r in hb.role_list()}

	# And the inverse map, i.e. 1-to-many.
	executable_roles = {}
	for r, e in role_executable.items():
		try:
			roles = executable_roles[e]
		except KeyError:
			roles = set()
			executable_roles[e] = roles
		roles.add(r)

	roles = set(role_executable.keys())

	# Results of scans for change.
	# Source, target, delta, ugm
	file_change = []
	#setting_value_change = []

	touching_roles = set()

	snapshot = os.path.abspath(snapshot)
	try:
		os.makedirs(snapshot)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	method = set(f for f in os.listdir(snapshot))

	source = hb.resource.path
	target = os.path.join(snapshot, 'resource-by-executable')
	s, ugm = storage_manifest(source)
	if 'resource-by-executable' in method or s.manifests > 0 or s.listings > 0:
		# As a read-only space its debatable whether this should
		# be part of an snapshot.
		# Handled as a wholesale delta rather than per-executable.
		try:
			os.makedirs(target)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise
		t, _ = storage_manifest(target)
		delta = [d for d in storage_delta(s, t)]
		if len(delta) > 0:
			for k in s.content.keys():
				r = executable_roles.get(k)
				if r:
					touching_roles |= r
			todo = (source, target, delta, ugm)
			file_change.append(todo)

			dr = len(delta)
			nr = len(touching_roles)
			self.console(f'Detected {dr} resource changes ({nr} associated roles)')

	source = hb.model.path
	target = os.path.join(snapshot, 'model-by-role')
	s, ugm = storage_manifest(source)
	if 'model-by-role' in method or s.manifests > 0 or s.listings > 0:
		try:
			os.makedirs(target)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise
		t, _ = storage_manifest(target)
		delta = [d for d in storage_delta(s, t)]
		if len(delta) > 0:
			r = set(s.content.keys())
			touching_roles |= r
			todo = (source, target, delta, ugm)
			file_change.append(todo)

			dm = len(delta)
			nr = len(r)
			self.console(f'Detected {dm} model changes ({nr} associated roles)')

	source = hb.settings.path
	target = os.path.join(snapshot, 'settings-by-role')
	s, ugm = storage_manifest(source)
	if 'settings-by-role' in method or s.manifests > 0 or s.listings > 0:
		try:
			os.makedirs(target)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise
		t, _ = storage_manifest(target)
		delta = [d for d in storage_delta(s, t)]
		if len(delta) > 0:
			r = set(os.path.splitext(k)[0] for k in s.content.keys())
			touching_roles |= r
			todo = (source, target, delta, ugm)
			file_change.append(todo)

			ds = len(delta)
			nr = len(r)
			self.console(f'Detected {ds} settings changes ({nr} associated roles)')

	if 'setting-value-by-role' in method:
		pass

	source = hb.input.path
	target = os.path.join(snapshot, 'input-by-role')
	s, ugm = storage_manifest(source)
	if 'input-by-role' in method or s.manifests > 0 or s.listings > 0:
		try:
			os.makedirs(target)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise
		t, _ = storage_manifest(target)
		delta = [d for d in storage_delta(s, t)]
		if len(delta) > 0:
			r = set(os.path.splitext(k)[0] for k in s.content.keys())
			touching_roles |= r
			todo = (source, target, delta, ugm)
			file_change.append(todo)

			di = len(delta)
			nr = len(r)
			self.console(f'Detected {di} input changes ({nr} associated roles)')

	if len(file_change) < 1:
		self.console('Nothing to snapshot')
		return None

	tr = [r for r in touching_roles if '.' not in r]
	_, running = group_pause(self, hb, tr, force)

	self.console('Starting snapshot of materials')
	try:

		for t in file_change:
			target = t[1]
			delta = t[2]
			a = self.create(FolderTransfer, delta, target)
			self.assign(a, t)

		while self.working():
			m = self.select(Completed, Stop)
			if isinstance(m, Stop):
				raise ar.Incomplete(Aborted())

			# Completed.
			t = self.debrief()
			target = t[1]
			self.console(f'Completed snapshot to "{target}"')
			value = m.value
			if isinstance(value, Ack):			# Reached the end.
				pass
			elif isinstance(value, ar.Faulted):		# ar.Failed to complete transfer.
				raise ar.Incomplete(value)
			else:
				raise ar.Incomplete(ar.Failed(file_tansfer=(value, 'unexpected response to snapshot')))
	finally:
		abort(self)
		group_resume(self, running)
	return None

def ls_args(ls):
	args = ['--%s=%s' % (k, v) for k, v in ls[0].items()]
	args.extend(['-%s=%s' % (k, v) for k, v in ls[1].items()])
	return args
