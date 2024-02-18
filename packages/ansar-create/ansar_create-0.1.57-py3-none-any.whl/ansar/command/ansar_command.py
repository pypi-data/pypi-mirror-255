# Author: Scott Woods <scott.18.ansar@gmail.com.com>
# MIT License
#
# Copyright (c) 2022 Scott Woods
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

"""Utility to maintain the operational folders and files of standard components.

Starts with the process-as-an-async-object abstraction and takes it to
the next level. There is a new abstraction that manages a collection
of one or more processes. A complete runtime environment is provided for
each process, i.e. a place for temporary files and persisted files, and
a per-process configuration. Once configured to satisfy requirements a
process can be started and stopped repeatedly using single commands.
"""
__docformat__ = 'restructuredtext'

__all__ = [
	'main',
]

import sys

import ansar.create as ar
from ansar.create.procedure import *

# Shims between command-line and library procedures.
# Provide access to ansar-encode.
versioning_settings = ar.VersioningSettings()
compare_settings = ar.CompareSettings()
release_settings = ar.ReleaseSettings()

# Shorthands.
START_ORIGIN = ar.POINT_OF_ORIGIN.START_ORIGIN
RUN_ORIGIN = ar.POINT_OF_ORIGIN.RUN_ORIGIN

create_settings = CreateSettings()
add_settings = AddSettings()
update_settings = UpdateSettings()
delete_settings = DeleteSettings()
destroy_settings = DestroySettings()
list_settings = ListSettings()
start_settings = StartSettings()
run_settings = RunSettings()
pause_settings = PauseSettings()
resume_settings = ResumeSettings()
stop_settings = StopSettings()
log_settings = LogSettings()
input_settings = InputSettings()
settings_settings = SettingsSettings()
set_settings = SetSettings()
edit_settings = EditSettings()
deploy_settings = DeploySettings()
returned_settings = ReturnedSettings()

def versioning(self, settings, ls, word):
	'''Print a human representation of the current version info. Returns nothing.'''
	version_module = ar.word_argument(0, word)
	return ar.procedure_versioned(versioning_settings, version_module)

def compare(self, settings, ls, word):
	'''Compare the current version info against saved image of most recently released.'''
	version_module = ar.word_argument(0, word)
	release_file = ar.word_argument(1, word)
	return ar.procedure_compare(compare_settings, version_module, release_file)

def release(self, settings, ls, word):
	'''Overwrite the saved image of version info with the current info.'''
	version_module = ar.word_argument(0, word)
	release_file = ar.word_argument(1, word)
	return ar.procedure_release(release_settings, version_module, release_file)


def ls_args(ls):
	args = ['--%s=%s' % (k, v) for k, v in ls[0].items()]
	args.extend(['-%s=%s' % (k, v) for k, v in ls[1].items()])
	return args

#
#
def create(self, _, ls, word):
	home = ar.word_argument(0, word)
	return procedure_create(self, create_settings, home)

def add(self, _, ls, word):
	executable = ar.word_argument(0, word)
	role = ar.word_argument(1, word)
	home = ar.word_argument(2, word)
	return procedure_add(self, add_settings, executable, role, home, ls)

def update(self, settings, ls, word):
	# A list of search expressions.
	role = word

	return procedure_update(self, update_settings, settings.force, role, ls_args(ls))

def delete(self, settings, ls, word):
	# Settings reuse.
	role = word
	return procedure_delete(self, delete_settings, role)

def list_(self, _, ls, word):
	role = word
	return list_home(self, list_settings, role)

def destroy(self, settings, ls, word):
	# Settings reuse.
	home = ar.word_argument(0, word)
	return procedure_destroy(self, destroy_settings, settings.force, home)

def run(self, _, ls, word):
	role = word
	return procedure_run(self, run_settings, role, ls_args(ls))

def start(self, _, ls, word):
	role = word
	return procedure_start(self, start_settings, role, ls_args(ls))

def pause(self, settings, ls, word):
	role = word
	return procedure_pause(self, pause_settings, settings.force, role)

def resume(self, settings, ls, word):
	group = word
	return procedure_resume(self, resume_settings, settings.force, group)

def stop(self, settings, ls, word):
	group = word
	return procedure_stop(self, stop_settings, group)

def status(self, _, ls, word):
	# Settings reuse.
	role = word
	return procedure_status(self, list_settings, role)

def history(self, _, ls, word):
	# Settings reuse.
	role = ar.word_argument(0, word)
	home = ar.word_argument(1, word)
	return procedure_history(self, list_settings, role, home)

def returned(self, _, ls, word):
	role = ar.word_argument(0, word)
	home = ar.word_argument(1, word)

	return procedure_returned(self, returned_settings, role, home)

def log(self, _, ls, word):
	role = ar.word_argument(0, word)
	home = ar.word_argument(1, word)

	# Initial sanity checks and a default <begin>.
	f = [log_settings.from_, log_settings.last, log_settings.start, log_settings.back]
	c = len(f) - f.count(None)
	if c == 0:
		log_settings.back = ar.text_to_span('5m')   # Default query of last 5 mins.
	elif c != 1:
		# one of <from>, <last>, <start> or <back> is required
		r = ar.Rejected(start_mark=(None, ['from', 'last', 'start', 'back']))
		raise ar.Incomplete(r)

	t = [log_settings.to, log_settings.span, log_settings.count]
	c = len(t) - t.count(None)
	if c == 0:
		pass		# Default is query to end-of-log or end of start-stop.
	elif c != 1:
		# one of <to>, <span> or <count> is required
		r = ar.Rejected(end_mark=(None, ['to', 'span', 'count']))
		raise ar.Incomplete(r)

	return procedure_log(self, log_settings, role, home)

def folder(self, _, ls, word):
	# Settings reuse.
	selected = ar.word_argument(0, word)
	role = ar.word_argument(1, word)
	home = ar.word_argument(2, word)
	return procedure_folder(self, list_settings, selected, role, home)

def input_(self, settings, ls, word):
	role = ar.word_argument(0, word)
	home = ar.word_argument(1, word)
	return procedure_input(self, input_settings, settings.force, role, home)

def settings(self, settings, ls, word):
	# Settings reuse.
	role = ar.word_argument(0, word)
	home = ar.word_argument(1, word)
	return procedure_settings(self, settings_settings, settings.force, role, home)

def get(self, _, ls, word):
	# Positional and settings options for 3 args.
	selected = ar.word_argument(0, word)
	role = ar.word_argument(1, word)
	home = ar.word_argument(2, word)
	return procedure_get(self, set_settings, selected, role, home)

def set_(self, settings, ls, word):
	# Convert word[] into property and role[].
	if len(word) < 2:
		e = ar.Rejected(set_property=(None, 'a <property> and at least one <role> are required'))
		raise ar.Incomplete(e)

	selected = word[0]
	role = word[1:]

	if set_settings.not_set:
		js = None
	elif set_settings.property_file:
		with open(set_settings.property_file, 'r') as f:
			js = f.read()
	else:
		js = sys.stdin.read()

	return procedure_set(self, ar.RoleProperties, set_settings, settings.force, selected, role, js)

def edit(self, settings, ls, word):
	# Positional and settings options for 3 args.
	selected = ar.word_argument(0, word)
	role = ar.word_argument(1, word)
	home = ar.word_argument(2, word)

	return procedure_edit(self, ar.RoleProperties, edit_settings, settings.force, selected, role, home)

def deploy(self, settings, ls, word):
	build = ar.word_argument(0, word)
	snapshot = ar.word_argument(1, word)
	home = ar.word_argument(2, word)
	return procedure_deploy(self, deploy_settings, settings.force, build, snapshot, home)

def snapshot(self, settings, ls, word):
	snapshot = ar.word_argument(0, word)
	home = ar.word_argument(1, word)
	return procedure_snapshot(self, deploy_settings, settings.force, snapshot, home)


# Bring all the functions together as a table that
# uses the function name, i.e. f.__name__ as a key.
table = ar.jump_table(
	# Access to ansar-encode.
	(versioning, versioning_settings),
	(compare, compare_settings),
	(release, release_settings),

	# CRUD of process definitions.
	(create, create_settings),
	(add, add_settings),
	(update, update_settings),
	(delete, delete_settings),
	(list_, list_settings),
	(destroy, destroy_settings),

	# CRUD of processes, i.e. instances of definitions.
	(run, run_settings),
	(start, start_settings),
	(pause, pause_settings),
	(resume, resume_settings),
	(stop, stop_settings),
	(status, list_settings),

	# Monitoring and control of existing definitions
	# and any associated instances.
	(history, list_settings),
	(returned, returned_settings),
	(log, log_settings),
	(folder, list_settings),
	(input_, input_settings),
	(settings, settings_settings),
	(get, set_settings),
	(set_, set_settings),
	(edit, edit_settings),

	# Transfer of binaries and materials to-and-from
	# repo and live home.
	(deploy, deploy_settings),
	(snapshot, deploy_settings),
)


#
#
class Settings(object):
	def __init__(self, force=False, user_name=None, user_key=None):
		'''
		* force
		Override cautionary behaviour, mostly relating to the unintended termination
		or running processes.
		'''
		self.force = force

SETTINGS_SCHEMA = {
	'force': ar.Boolean(),
}

ar.bind(Settings, object_schema=SETTINGS_SCHEMA)

#
#
def ansar(self, settings):
	'''Process configuration and orchestration.

	ansar create --redirect-bin=dist
	ansar add zombie
	ansar start zombie-0
	ansar status zombie-0
	ansar log zombie-0
	ansar stop
	* create
	Print the current version information on the console.
	* add
	Compare the current version information against a saved image and report
	any issues. Any issue that might subvert the processing of versioned
	materials "in the wild" will result in a non-zero exit code.
	* update
	Update the saved image with the current version information. Subsequent
	use of the compare sub-command will be relative to the new image.

	* versioning
	Print the current version information on the console.
	* compare
	Compare the current version information against a saved image and report
	any issues. Any issue that might subvert the processing of versioned
	materials "in the wild" will result in a non-zero exit code.
	* release
	Update the saved image with the current version information. Subsequent
	use of the compare sub-command will be relative to the new image.
	* create
	Create a folder to hold the configurations of one or more processes.
	* add
	Create the configuration of a process.
	* update
	Modify the configuration settings of a process.
	* delete
	Remove the configuration of a process.
	* list
	Print a list of the currently defined processes.
	* destroy
	Remove the folder and all the process configurations it may contain.
	* run
	Execute one or more processes and wait for the result.
	* start
	Initiate one or more processes in the background.
	* pause
	Terminate one or more running processes with the intention of a restart.
	* resume
	Restart all previously paused processes.
	* stop
	Terminate one or more processes.
	* status
	Print a list of the currently running processes.
	* history
	Print the start/pause/resume/stop details of a particular process.
	* returned
	Print the value returned by the most recent completion of a process.
	* log
	Print the logs created by a specified process.
	* folder
	Print an actual runtime location relating to a specified process.
	* input
	View and modify the configured input of a process.
	* settings
	View and modify the configured settings of a process.
	* get
	View the management properties of a process.
	* set
	Modify the management properties of a process.
	* edit
	View and modify the management properties of a process.
	* deploy
	Orchestrate the update of process configurations.
	* snapshot
	Take a copy of all process runtimes.
	'''
	sub_command, ls, words = ar.object_words()
	if sub_command is None:
		return None

	# Everything lined up for execution of
	# the selected sub-command.
	try:
		output = sub_command(self, settings, ls, words)
	except ar.Incomplete as e:
		return e.value
	return output

ar.bind(ansar)

#
#
factory_settings = Settings()

def main():
	ar.create_object(ansar, factory_settings=factory_settings, parameter_passing=ar.sub_object_passing, parameter_table=table)

# The standard entry point. Needed for IDEs
# and debugger sessions.
if __name__ == '__main__':
	main()
