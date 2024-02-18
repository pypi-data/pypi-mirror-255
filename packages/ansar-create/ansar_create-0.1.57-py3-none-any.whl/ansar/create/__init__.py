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

"""Tools and runtime for asynchronous programming.

Repo: git@github.com:mr-ansar/ansar-create.git
Branch: main
Commit: 9b0abe05f0914168be08659a13abc41d223dd7bb
Version: 0.1.56 (2024-02-10@12:54:32+NZDT)
"""

from ansar.encode import *

from .coding import cannot, lor
from .space import NO_SUCH_ADDRESS
from .space import create_an_object, find_object, destroy_an_object
from .space import OpenAddress
from .space import abdicate_to_address, discard_address
from .space import send_a_message
from .space import set_queue, get_queue, get_queue_address
from .space import start_a_thread, running_in_thread

from .lifecycle import Start, Completed
from .lifecycle import Stop, Pause, Resume
from .lifecycle import Aborted, TimedOut
from .lifecycle import AWOL, Overloaded, OutOfService
from .lifecycle import Nothing, Ready, NotReady, Enquiry
from .lifecycle import Maybe, Cannot, Interrupted, Exhausted
from .lifecycle import Ack, Nak

from .properties import load_properties, recover_property, store_property

from .pending import Queue, Buffering, Machine, SelectTimer, Other

from .point import Point
from .point import completed_object
from .point import T1, T2, T3, T4
from .point import StartTimer, CancelTimer
from .point import PointLog
from .point import RedirectLog
from .point import OpenTap, CloseTap, TapLine
from .point import Threaded, Channel
from .point import object_dispatch
from .point import bind_point, bind_function
from .point import halt
from .point import AutoStop
from .point import PointTest

from .machine import Stateless, StateMachine, bind_stateless, bind_statemachine

from .retry import RetryIntervals, intervals_only, smart_intervals, Retry
from .locking import LockUp, lock_file, unlock_file, LockedOut, lock_and_hold

from .log import PEAK_BEFORE_BLOCKING, LogAgent
from .log import log_to_stderr, log_to_nowhere, select_logs, LogToMemory
from .rolling import read_log

from .test import TestReport, TestSuite, test_enquiry

from .root import start_up, tear_down
from .root import open_channel, drop_channel, OpenChannel, AddOn
from .home import StartStop, Homebase, HomeProperties, RoleProperties
from .processing import Process, Punctuation, Utility, process_args
from .grouping import GroupRun

from .procedure import CreateSettings, AddSettings, UpdateSettings, DeleteSettings, DestroySettings, ListSettings
from .procedure import StartSettings, RunSettings, PauseSettings, ResumeSettings, StopSettings
from .procedure import LogSettings, InputSettings, SettingsSettings, SetSettings, EditSettings
from .procedure import DeploySettings, ReturnedSettings

from .procedure import procedure_create, procedure_add, procedure_update, procedure_delete, list_home, procedure_destroy
from .procedure import procedure_run, procedure_start, procedure_pause, procedure_resume, procedure_stop, procedure_status
from .procedure import procedure_history, procedure_returned, procedure_log, procedure_folder, procedure_input, procedure_settings
from .procedure import procedure_get, procedure_set, procedure_edit
from .procedure import procedure_deploy, procedure_snapshot

from .object import POINT_OF_ORIGIN, start_origin, run_origin
from .object import LOG_NUMBER
from .object import ObjectSettings, object_settings
from .object import object_role, object_args, object_variables, object_executable, object_words
from .object import object_custom_settings, object_unknown, store_settings
from .object import object_input
from .object import object_resource_folder, object_tmp_folder, object_model_folder
from .object import object_resource_path, object_tmp_path, object_model_path
from .object import object_passing, sub_object_passing
from .object import co
from .object import create_object

from .storage import DELTA_FILE_ADD, DELTA_FILE_UPDATE, DELTA_FILE_UGM, DELTA_FILE_REMOVE
from .storage import DELTA_FOLDER_ADD, DELTA_FOLDER_UPDATE, DELTA_FOLDER_UGM, DELTA_FOLDER_REMOVE
from .storage import DELTA_FILE_CRUD, DELTA_FOLDER_CRUD
from .storage import DELTA_CRUD

from .storage import TransferHalted, DeltaMachine
from .storage import StorageTables, StorageAttributes, StorageManifest, StorageListing
from .storage import storage_manifest, storage_delta, storage_walk
from .storage import AddFolder, RemoveFolder
from .storage import AddFile, UpdateFile, RemoveFile, UpdateUser, UpdateGroup, UpdateMode
from .storage import ReplaceWithFile, ReplaceWithFolder

from .binding import bind_any

bind = bind_any
create = create_object
