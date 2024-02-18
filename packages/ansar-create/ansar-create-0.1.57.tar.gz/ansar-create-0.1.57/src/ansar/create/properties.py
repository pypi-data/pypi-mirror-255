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

""".

.
"""

__docformat__ = 'restructuredtext'

import ansar.encode as ar

__all__ = [
	'load_properties',
	'recover_property',
	'store_property',
]


def load_properties(properties, folder, create_default=False):
	t = ar.tof(properties)
	try:
		schema = properties.__art__.value
	except AttributeError:
		raise ar.Failed(properties_load=(None, f'type "{t}" is not a registered type'))

	for name, t in schema.items():
		f = folder.file(name, t)
		try:
			value, _ = f.recover()
		except ar.FileNotFound:
			if create_default:
				value = getattr(properties, name)
				f.store(value)
			continue
		except (ar.FileFailure, ar.CodecError) as e:
			raise ar.Failed(property_load=(e, f'type "{t}"'))

		setattr(properties, name, value)

def recover_property(properties, folder, name, create_default=None):
	s = ar.tof(properties)
	try:
		t = properties.__art__.value[name]
	except KeyError:
		raise ar.Failed(property_recover=(None, f'type "{s}" has no such property "{name}"'))
	except AttributeError:
		raise ar.Failed(property_recover=(None, f'type "{s}" is not a registered type'))

	f = folder.file(name, t)
	try:
		value, tag = f.recover()
	except ar.FileNotFound:
		value, tag = getattr(properties, name, None), None
		if create_default is not None:
			f.store(value)
		return value, tag
	except (ar.FileFailure, ar.CodecError) as e:
		raise ar.Failed(property_recover=(e, f'type "{s}"'))

	setattr(properties, name, value)
	return value, tag

def store_property(properties, folder, name, value):
	s = ar.tof(properties)
	try:
		t = properties.__art__.value[name]
	except KeyError:
		raise ar.Failed(property_store=(None, f'type "{s}" has no such property "{name}"'))
	except AttributeError:
		raise ar.Failed(property_store=(None, f'type "{s}" is not a registered type'))

	f = folder.file(name, t)
	try:
		f.store(value)
	except (ar.FileFailure, ar.CodecError) as e:
		raise ar.Failed(property_store=(e, f'type "{s}"'))
	setattr(properties, name, value)
