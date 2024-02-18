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

"""General coding support.

Classes and functions that may be useful in any
Python development, i.e. not dependent on Ansar.
"""

__docformat__ = 'restructuredtext'

import sys
import ansar.encode as ar

__all__ = [
	'cannot',
	'lor',
]

def cannot(line, newline=True, **kv):
	"""Place an error diagnostic on stderr, including the executable name."""
	if kv:
		t = line.format(**kv)
	else:
		t = line

	h = ar.program_name
	sys.stderr.write(h)
	sys.stderr.write(': ')
	sys.stderr.write(t)
	if newline:
		sys.stderr.write('\n')

#
#
def lor(a, max=32, separator=', '):
	t = 0
	for i, s in enumerate(a):
		t += len(s) + 2
		if t > max:
			# Output getting too long. Compose
			# an abbreviation.
			s = ', '.join(a[:i + 1])
			return f'{s} ... ({len(a)})'
	# No overflow including the
	# empty list.
	return separator.join(a)
