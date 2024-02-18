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

from .point import pt, Threaded, PointTest
from .machine import Stateless, bind_stateless
from .lifecycle import Start, Stop, Enquiry

__all__ = [
	'TestRecord',
	'TestReport',
	'TestSuite',
	'test_enquiry',
]

class TestReport(object):
	"""A sequence of test results.

	Each call to Point.test() produces an entry in the tested
	member. This object is the intended return value for a test
	process.

	:param passed: count of true tests
	:type passed: int
	:param failed: count of false tests
	:type failed: int
	:param tested: sequence of PointTests
	:type tested: list
	"""
	def __init__(self, passed=0, failed=0, tested=None):
		self.passed = passed
		self.failed = failed
		self.tested = tested or ar.default_vector()

TEST_REPORT_SCHEMA = {
	"passed": int,
	"failed": int,
	"tested": ar.VectorOf(PointTest),
}

ar.bind(TestReport, object_schema=TEST_REPORT_SCHEMA, copy_before_sending=False)

#
#
class TestSuite(object):
	"""A collection of TestReports.

	Each TestReport collected by a parent process, e.g. the
	ansar tool, is gathered into suite of reports.

	:param report: a TestReport per role
	:type report: dict
	"""
	def __init__(self, role=None, report=None, passed=0, failed=0, navigation=None):
		self.role = role or ar.default_vector()
		self.report = report or ar.default_map()
		self.passed = passed
		self.failed = failed
		self.navigation = navigation or ar.default_vector()

TEST_SUITE_SCHEMA = {
	"role": ar.VectorOf(str),
	"report": ar.MapOf(str, TestReport),
	"navigation": ar.VectorOf(str),
}

ar.bind(TestSuite, object_schema=TEST_SUITE_SCHEMA, copy_before_sending=False)

# Per-process, background collation of test results.
#
MAXIMUM_TESTS = 255

class TestRecord(Threaded, Stateless):
	"""
	"""
	def __init__(self):
		Threaded.__init__(self, blocking=True)
		Stateless.__init__(self)
		self.tested = []
		self.overflow = False

def TestRecord_Start(self, message):
	pass

def TestRecord_PointTest(self, message):
	if len(self.tested) < MAXIMUM_TESTS:
		self.tested.append(message)
		return

	if not self.overflow:
		p = PointTest()
		p.stamp = message.stamp
		p.name = self.__art__.name

		p.condition = False
		p.source = message.source
		p.line = message.line

		p.text = f'Cannot exceed {MAXIMUM_TESTS} tests'
		self.tested.append(p)
		self.overflow = True

def TestRecord_Enquiry(self, message):
	r = TestReport()
	for t in self.tested:
		if t.condition:
			r.passed += 1
		else:
			r.failed += 1
	r.tested = self.tested
	self.reply(r)

def TestRecord_Stop(self, message):
	self.complete()

bind_stateless(TestRecord,
	(Start, PointTest, Enquiry, Stop),
	lifecycle=False, message_trail=False, execution_trace=False)

#
#
def test_enquiry(self):
	self.send(Enquiry(), pt.test_address)
