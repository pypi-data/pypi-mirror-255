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

import os
from .portable import *
from .message import *

__all__ = [
	'Gas',
	'breakpath',
	'tof',
	'Incomplete',
	'jump_table',
	'show_fault',
	'name_text',
	'Faulted',
	'Rejected',
	'Failed',
	'FAULTED_SCHEMA',
]

#
#
class Gas(object):
	"""Build an object from the specified k-v args, suitable as a global context.

	:param kv: map of names and value
	:type path: dict
	"""
	def __init__(self, **kv):
		"""Convert the named values into object attributes."""
		for k, v in kv.items():
			setattr(self, k, v)

#
#
def breakpath(p):
	"""Break apart the full path into folder, file and extent (3-tuple)."""
	p, f = os.path.split(p)
	name, e = os.path.splitext(f)
	return p, name, e

#
#
def tof(value):
	if isinstance(value, Incognito):
		s = value.type_name
		t = f'Incognito({s})'
	try:
		t = type(value)
		if t == type:
			return value.__name__
		t = t.__name__
	except (TypeError, AttributeError):
		return 'undiscoverable type'

	return t

# For termination of sub-commands without having
# to detect and propagate through the call stack.

class Incomplete(Exception):
	def __init__(self, value):
		Exception.__init__(self)
		self.value = value

# Support functions for the
# sub-command and args machinery.
def jump_table(*args):
	t = {a[0].__name__.rstrip('_'): a for a in args}
	return t

# Generalized error signaling.
class Faulted(object):
	"""Generic error signal to interested party."""
	def __init__(self, condition=None, explanation=None, error_code=None, exit_code=None):
		self.condition = condition or 'fault'
		self.explanation = explanation or 'cause unspecified'
		self.error_code = error_code
		self.exit_code = exit_code

	def __str__(self):
		s = f'{self.condition} ({self.explanation})'
		return s

FAULTED_SCHEMA = {
	'condition': Unicode,
	'explanation': Unicode,
	'error_code': Integer8,
	'exit_code': Integer8,
}

#
#
def lont(kv):
	a = [f'{k}: {v}' for k, v in kv.items()]
	return ', '.join(a)

def name_text(kv):
	if len(kv) < 1:
		return f'unspecified'
	
	c = 0
	r = {}
	for k, v in kv.items():
		c += len(k) + 2 + len(v) + 2
		r[k] = v
		if c > 128:
			# Output getting too long. Compose
			# an abbreviation.
			break

	if len(r) < len(kv):
		s = lont(r)
		return f'{s}...({len(kv)})'
	return lont(kv)

def rejected(v):
	if v is None:
		return ''
	return f'({v})'

def show_fault(v):
	if isinstance(v, tuple) and len(v) == 2:
		lo = show_fault(v[0])
		hi = show_fault(v[1])
		return f'[{lo}...{hi}]'
	elif isinstance(v, list):
		a = [show_fault(t) for t in v]
		s = ', '.join(a)
		return f'[{s}]'
	elif isinstance(v, str):
		return f'{v}'
	elif isinstance(v, (bool, int, float)):
		return f'{v}'
	elif hasattr(v, '__str__'):
		return f'{v}'
	elif v is None:
		return '?'
	t = tof(v)
	return t

def value_expected(ve):
	value, expected = ve
	if value is None:
		if expected is None:
			return 'unspecified'
		e = show_fault(expected)
		return f'expected {e}'

	if expected is None:
		v = show_fault(value)
		return f'{v}'

	v = show_fault(value)
	e = show_fault(expected)
	return f'{v} (expected {e})'

def rejected_values(nve):
	rejected = {f'{k}': value_expected(ve) for k, ve in nve.items()}
	text = name_text(rejected)
	return rejected, text

def failed_operation(nuf):
	if len(nuf) != 1:
		return 'internal:', '(op count)'
	operation, uf = next(iter(nuf.items()))

	if len(uf) != 2:
		return 'internal:', '(uf pair)'
	unexpected, further = uf

	if unexpected is None:
		if further is None:
			return operation, f'{operation}: (unspecified)'
		f = show_fault(further)
		return operation, f'{operation}: ({f})'
	u = show_fault(unexpected)

	if further is None:
		return operation, f'{operation}: {u}'
	f = show_fault(further)
	return operation, f'{operation}: {u} ({f})'

class Rejected(Faulted):
	def __init__(self, error_code=None, exit_code=None, **nve):
		rejected, text = rejected_values(nve)
		Faulted.__init__(self, 'rejected values', text, error_code=error_code, exit_code=exit_code)
		self.rejected = rejected

class Failed(Faulted):
	def __init__(self, error_code=None, exit_code=None, **nuf):
		operation, text = failed_operation(nuf)
		Faulted.__init__(self, 'failed operation', text, error_code=error_code, exit_code=exit_code)
		self.operation = operation

REJECTED_SCHEMA = {
	'rejected': MapOf(Unicode(), Unicode()),
}

FAILED_SCHEMA = {
	'operation': Unicode(),
}

REJECTED_SCHEMA.update(FAULTED_SCHEMA)
FAILED_SCHEMA.update(FAULTED_SCHEMA)

bind_message(Faulted, object_schema=FAULTED_SCHEMA, copy_before_sending=False)
bind_message(Rejected, object_schema=REJECTED_SCHEMA, copy_before_sending=False)
bind_message(Failed, object_schema=FAILED_SCHEMA, copy_before_sending=False)
