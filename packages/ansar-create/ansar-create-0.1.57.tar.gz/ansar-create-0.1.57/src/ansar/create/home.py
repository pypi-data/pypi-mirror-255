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

"""An operational environment for a collection of processes.

"""
__docformat__ = 'restructuredtext'

import os
import shutil
import ansar.encode as ar
from .retry import RetryIntervals
from .properties import load_properties, recover_property, store_property

__all__ = [
	'FULL_SERVICE',
	'TOOL_SERVICE',
	'StartStop',
	'HomeProperties',
	'RoleProperties',
	'HomeRole',
	'Homebase',
]

# Name of the redirect file, i.e. if it exists then it contains the
# absolute path of where expected materials can be found, rather than
# in the folder containing the redirect.
REDIRECT = '.redirect'

class StartStop(object):
	def __init__(self, start=None, stop=None, returned=None):
		self.start = start
		self.stop = stop
		self.returned = returned

START_STOP_SCHEMA = {
	"start": ar.WorldTime,
	"stop": ar.WorldTime,
	"returned": ar.Any,
}

ar.bind(StartStop, object_schema=START_STOP_SCHEMA)

STARTING_AND_STOPPING = 8

# Services provided;
# bin ....... executable files
# entry ..... name for a process
# settings .. persistent configuration
# input ..... default arguments
# logs ...... records of activity
# resource .. read-only per-executable materials
# tmp ....... cleared on start
# model ..... persistent, compiled materials

FULL_SERVICE = ['bin', 'entry', 'lock', 'settings', 'input', 'logs', 'resource', 'tmp', 'model', 'properties']
TOOL_SERVICE = ['entry', 'settings', 'input', 'resource', 'properties']

def get_decoration(p, s, t):
	if p is None:
		f = None
		v = None
	else:
		f = p.file(s, t)
		try:
			v, _ = f.recover()
		except ar.FileNotFound:
			v = None
	return [t, f, v]

def set_decoration(p, s, t, v):
	if p is None:
		f = None
	else:
		f = p.file(s, t)
		if v is not None:
			f.store(v)
	return [t, f, v]

#
#
class HomeProperties(object):
	def __init__(self, guid=None, created=None):
		self.guid = guid
		self.created = created

HOME_PROPERTIES_SCHEMA = {
	'guid': ar.UUID(),
	'created': ar.WorldTime(),
}

class RoleProperties(object):
	def __init__(self, guid=None, created=None, executable=None, start_stop=None, retry=None, storage=None):
		self.guid = guid
		self.created = created
		self.executable = executable
		self.start_stop = start_stop or ar.default_deque()
		self.retry = retry or RetryIntervals(step_limit=0)
		self.storage = storage

ROLE_PROPERTIES_SCHEMA = {
	'guid': ar.UUID(),
	'created': ar.WorldTime(),
	'executable': ar.Unicode(),
	'start_stop': ar.DequeOf(StartStop),
	'retry': ar.UserDefined(RetryIntervals),
	'storage': ar.Integer8(),
}

ar.bind(HomeProperties, object_schema=HOME_PROPERTIES_SCHEMA)
ar.bind(RoleProperties, object_schema=ROLE_PROPERTIES_SCHEMA)

#
#
class HomeRole(object):
	def __init__(self, home, role):
		self.home = home				# Parent.

		self.role_name = role			# First segment of full name.

		self.role_entry = None			# Folder for properties.
		self.role_settings = None		# Tfv.
		self.role_logs = None			# Folder access to records.
		self.role_resource = None		# Instance access to read-only executable materials.
		self.role_tmp = None			# ... to cleared space.
		self.role_model = None			# ... to saved space.
		self.role_input = None			# Tfv.

		# Properties.
		self.properties = RoleProperties()

	def entry_started(self):
		properties = self.properties
		start_stop = properties.start_stop

		s = StartStop(start=ar.world_now())
		start_stop.append(s)
		n = len(start_stop)
		while n > STARTING_AND_STOPPING:
			start_stop.popleft()
			n -= 1
		if self.role_entry:
			store_property(properties, self.role_entry, 'start_stop', start_stop)

	def entry_returned(self, returned):
		properties = self.properties
		start_stop = properties.start_stop

		s = start_stop[-1]
		if s.stop is not None:  # Already stopped.
			return
		s.stop = ar.world_now()
		s.returned = returned
		if self.role_entry:
			store_property(properties, self.role_entry, 'start_stop', start_stop)

class Homebase(object):
	def __init__(self, path, plan):
		self.supplied_path = path

		a = os.path.abspath(path)
		b = ar.breakpath(a)

		self.home_path = a
		self.home_name = b[1]

		# Schemas.
		self.home_plan = plan

		# On-disk root.
		self.home = None

		# Under the root.
		self.bin = None
		self.lock = None
		self.entry = None
		self.settings = None
		self.input = None
		self.logs = None
		self.resource = None
		self.tmp = None
		self.model = None

		self.bin_path = None
		self.bin_env = None

		# Properties...
		self.properties = HomeProperties()

		self.basic_plan()

	# Set of queries that provide for create/open of a complex,
	# persistent object. Each step creates new folders+files or
	# recovers existing materials, returning progress indicators
	# and building an image of what is present on disk.

	def basic_plan(self):
		'''Build an in-memory, read-only sketch of the static elements.'''
		self.home = ar.Folder(self.home_path, auto_create=False)

		def if_required(service):
			if service not in self.home_plan:
				return None
			return self.home.folder(service)

		# Create the base set of expected folder objects.
		self.bin = if_required('bin')
		self.lock = if_required('lock')
		self.resource = if_required('resource')
		self.entry = if_required('entry')
		self.settings = if_required('settings')
		self.input = if_required('input')
		self.logs = if_required('logs')
		self.tmp = if_required('tmp')
		self.model = if_required('model')

	def plan_exists(self):
		'''Compare the in-memory sketch against the disk reality.'''
		leaf = [
			self.bin, self.lock, self.resource, self.entry, self.settings, self.input,
			self.logs, self.tmp, self.model
		]
		for f in leaf:
			if f and not f.exists():
				return False
		return True

	def ready_for_subprocessing(self):
		'''Prepare materials for wanting to start a sub-process.'''
		bin_env = dict(os.environ)
		old = bin_env.get('PATH', None)

		if old and self.bin:
			bin_path = f'{self.bin.path}:{old}'
			bin_env['PATH'] = bin_path
		else:
			bin_path = None

		self.bin_path = bin_path
		self.bin_env = bin_env

	def resolve_executable(self, name):
		if self.bin_path:
			s = shutil.which(name, path=self.bin_path)
		else:
			s = shutil.which(name)
		return s

	def create_plan(self, redirect):
		self.home = ar.Folder(self.home.path)

		# Function that honours redirects and creates the necessary
		# folders and support materials (e.g. a back-link).
		def follow(location, read_only=False):
			if location is None:
				return None
			location = ar.Folder(location.path)
			b = ar.breakpath(location.path)
			try:
				over = redirect[b[1]]
			except KeyError:
				return location
			f = location.file(REDIRECT, str)
			# Distinct treatment for folders that can/cant be safely
			# shared by multiple components.
			if not read_only:
				s = str(self.id[2])
				s = 'ansar-%s-%s' % (b[1], s)
				over = os.path.join(over, s)	# A per-id folder at external location.
			f.store(over)
			location = ar.Folder(over)
			if read_only:
				return location
			set_decoration(location, '.ansar-origin', str, self.home.path)
			return location

		# Establish the essential elements of a home.
		self.bin = follow(self.bin, read_only=True)
		self.lock = follow(self.lock)
		self.settings = follow(self.settings)
		self.input = follow(self.input)
		self.logs = follow(self.logs)
		self.resource = follow(self.resource, read_only=True)
		self.tmp = follow(self.tmp)
		self.model = follow(self.model)
		self.entry = follow(self.entry)

		#
		#
		load_properties(self.properties, self.home, create_default=True)

		# Build support materials for lookup/verification of
		# entry executables.
		self.ready_for_subprocessing()

	def open_plan(self):
		self.home = ar.Folder(self.home.path)

		def follow(location, read_only=False):
			if location is None:
				return None
			location = ar.Folder(location.path)
			f = location.file(REDIRECT, str)
			try:
				path, _ = f.recover()
			except ar.FileNotFound:
				return location
			location = ar.Folder(path)
			return location

		self.bin = follow(self.bin, read_only=True)
		self.lock = follow(self.lock)
		self.settings = follow(self.settings)
		self.input = follow(self.input)
		self.logs = follow(self.logs)
		self.resource = follow(self.resource, read_only=True)
		self.tmp = follow(self.tmp)
		self.model = follow(self.model)
		self.entry = follow(self.entry)

		#
		#
		load_properties(self.properties, self.home)

		self.ready_for_subprocessing()

	def destroy_plan(self):
		'''Explicit clearance of folders that may be redirected and not read-only.'''

		self.lock and ar.remove_folder(self.lock.path)
		self.settings and ar.remove_folder(self.settings.path)
		self.input and ar.remove_folder(self.input.path)
		self.logs and ar.remove_folder(self.logs.path)

		self.tmp and ar.remove_folder(self.tmp.path)
		self.model and ar.remove_folder(self.model.path)

		self.home and ar.remove_folder(self.home.path)

	def role_exists(self, role):
		if role is None:
			raise ValueError('null/empty role')
		if self.entry is None:
			raise ValueError('home has no entries')

		p = os.path.join(self.entry.path, role)
		if os.path.isdir(p):
			return True
		return False

	'''
	def open_role(self, name, settings, input, properties):
		hr = HomeRole(self, name)

		def if_required(f):
			if f is None:
				return None
			return f.folder(name)

		hr.role_entry = if_required(self.entry)
		hr.role_logs = if_required(self.logs)
		hr.role_tmp = if_required(self.tmp)
		hr.role_model = if_required(self.model)

		for k, tv in properties.items():
			t, _ = tv
			tfv = get_decoration(hr.role_entry, k, t)
			setattr(hr, k, tfv)

		if self.settings:
			if settings:
				t = ar.UserDefined(type(settings))
				hr.role_settings = get_decoration(self.settings, hr.role_name, t)
				hr.set_store(settings)
			else:
				s = os.path.join(self.settings.path, hr.role_name + '.json')
				if os.path.isfile(s):
					hr.role_settings = [None, None, None]

		if self.input:
			if input:
				t = ar.fix_expression(type(input), {})
				hr.role_input = get_decoration(self.input, hr.role_name, t)
			else:
				s = os.path.join(self.input.path, hr.role_name + '.json')
				hr.role_input = [None, None, None]

		if hr.role_tmp:
			ar.remove_contents(hr.role_tmp.path)

		if self.resource and hasattr(hr, 'executable') and hr.executable[2]:
			hr.role_resource = self.resource.folder(hr.executable[2])
		
		return hr
	'''

	def tool_exists(self, role):
		p = os.path.join(self.entry.path, role)
		t = os.path.isdir(p)
		return t

	def clear_folder(self, folder, role):
		for name in os.listdir(folder.path):
			p = os.path.join(folder.path, name)
			if os.path.isdir(p):
				ar.remove_folder(p)
			else:
				os.remove(p)

	def procedure_delete(self, hr):
		'''.'''
		self.entry and self.clear_folder(self.entry, hr.role_name)
		self.lock and self.clear_folder(self.lock, hr.role_name)
		self.settings and self.clear_folder(self.settings, hr.role_name)
		self.input and self.clear_folder(self.input, hr.role_name)
		self.logs and self.clear_folder(self.logs, hr.role_name)
		self.tmp and self.clear_folder(self.tmp, hr.role_name)
		self.model and self.clear_folder(self.model, hr.role_name)

	def verify(self):
		folder = (
			self.bin,
			self.role_logs,
			self.role_resource,
			self.role_tmp,
			self.role_model,
		)

		for f in folder:
			if f is not None and not f.exists():
				s = 'Location "%s" not found' % (f.path,)
				raise ValueError(s)

	def role_list(self):
		for f in os.listdir(self.entry.path):
			yield f

	def group_list(self):
		for f in os.listdir(self.entry.path):
			if f.startswith('group.'):
				yield f

	def open_role(self, role, settings, input, properties=None):
		hr = HomeRole(self, role)

		def if_required(f):
			if f is None:
				return None
			return f.folder(role)

		hr.role_entry = if_required(self.entry)
		hr.role_logs = if_required(self.logs)
		hr.role_tmp = if_required(self.tmp)
		hr.role_model = if_required(self.model)

		if properties:
			hr.properties = properties
		
		if hr.role_entry:
			load_properties(hr.properties, hr.role_entry, create_default=True)

		if self.settings:
			if settings:
				t = ar.UserDefined(type(settings))
				hr.role_settings = get_decoration(self.settings, role, t)
				if hr.role_settings[2] is None and settings is not None:
					hr.role_settings[1].store(settings)
					hr.role_settings[2] = settings

		if self.input:
			if input:
				t = ar.fix_expression(type(input), {})
				hr.role_input = get_decoration(self.input, role, t)
				if hr.role_input[2] is None and input is not None:
					hr.role_input[1].store(input)
					hr.role_input[2] = input

		if hr.role_tmp:
			ar.remove_contents(hr.role_tmp.path)

		if self.resource and hr.properties.executable:
			hr.role_resource = self.resource.folder(hr.properties.executable)
		return hr
