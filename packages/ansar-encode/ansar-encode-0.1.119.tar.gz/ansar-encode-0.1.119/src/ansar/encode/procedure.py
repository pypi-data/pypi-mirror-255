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

"""Programmatic access to essential operations associated with this library.

Find the command-line interface to these operations in;
src/ansar/command/ansar_command.py.
"""
__docformat__ = 'restructuredtext'

__all__ = [
	'VersioningSettings',
	'CompareSettings',
	'ReleaseSettings',
	'procedure_versioned',
	'procedure_compare',
	'procedure_release',
]

import os
from .support import *
from .primitive import *
from .portable import *
from .message import *
from .runtime import *

#
#
DEFAULT_VERSION = 'released.py'			# User-supplied list of registered "document" messages.
DEFAULT_RELEASE = '.ansar-released'		# Snapshot of version details of most recently released software

VERSION = 'version'
RELEASE = 'release'

# Parameters for the different sub-commands.
class VersioningSettings(object):
	def __init__(self, version_module=None):
		self.version_module = version_module

VERSIONING_SCHEMA = {
	'version_module': Unicode(),
}

bind_message(VersioningSettings, object_schema=VERSIONING_SCHEMA)


class CompareSettings(object):
	def __init__(self, version_module=None, release_file=None,
		notes=False, warnings=False, faults=False):
		self.version_module = version_module
		self.release_file = release_file
		self.notes = notes
		self.warnings = warnings
		self.faults = faults

COMPARE_SETTINGS_SCHEMA = {
	'version_module': Unicode(),
	'release_file': Unicode(),
	'notes': Boolean(),
	'warnings': Boolean(),
	'faults': Boolean(),
}

bind_message(CompareSettings, object_schema=COMPARE_SETTINGS_SCHEMA)


class ReleaseSettings(object):
	def __init__(self, version_module=None, release_file=None):
		self.version_module = version_module
		self.release_file = release_file

SET_SETTINGS_SCHEMA = {
	'version_module': Unicode(),
	'release_file': Unicode(),
}

bind_message(ReleaseSettings, object_schema=SET_SETTINGS_SCHEMA)

#
#

def procedure_versioned(versioned, version_module):
	'''Print a human representation of the current version info. Returns nothing.'''

	version_module = word_argument_2(version_module, versioned.version_module, DEFAULT_VERSION, VERSION)

	# Always a dict thou possibly empty. Errors
	# skip this processing via exceptions.
	current = load_module(version_module)

	for k, v in current.items():
		output_line(f'{k}:')
		for x, y in v.items():
			output_line(f'\t{x}/{y}')
	
	# No further output.
	return None

def procedure_compare(compare, version_module, release_file):
	'''Compare the current version info against saved image of most recently released.'''

	version_module = word_argument_2(version_module, compare.version_module, DEFAULT_VERSION, VERSION)
	release_file = word_argument_2(release_file, compare.release_file, DEFAULT_RELEASE, RELEASE)

	# Load the current and previous (i.e. saved) images
	module = load_module(version_module)
	release = load_release(release_file)

	# If no previous then its a fresh situation. so
	# just current as the new previous and terminate.
	if release is None:
		save_release(module, release_file)
	else:
		compare_release(module, release, compare)
		# Fatal flaws in the version info result in
		# faults/exceptions.
	return None

def procedure_release(release, version_module, release_file):
	version_module = word_argument_2(version_module, release.version_module, DEFAULT_VERSION, VERSION)
	release_file = word_argument_2(release_file, release.release_file, DEFAULT_RELEASE, RELEASE)
	# Load the current image. Errors skip this
	# processing using exceptions.
	release = load_module(version_module)

	# Create or overwrite the current image as
	# the new reference for furture version checks.
	save_release(release, release_file)

	return None

# Support functions.
#
def major_minor(mm):
	if not isinstance(mm, str):
		raise Incomplete(Rejected(version=(mm, '"string <major>.<minor>"')))
	s = mm.split('.')
	if len(s) != 2:
		raise Incomplete(Rejected(version=(mm, '"<major>.<minor>"')))
	try:
		m, n = int(s[0]), int(s[0])
	except (TypeError, ValueError):
		raise Incomplete(Rejected(version=(mm, '2 integers separated by a dot')))

	return m, n

def odd_sequence(p, c):
	'''Sanity checks on the version tag.'''
	p_major, p_minor = major_minor(p)
	c_major, c_minor = major_minor(c)
	if c_major < p_major:				# 
		return True
	if c_major == p_major:
		if c_minor < p_minor:
			return True
	return False

def compare_release(current, previous, compare):
	# Checks and balances.
	warnings, faults = 0, 0
	for d, r in current.items():
		try:
			p = previous[d]
		except KeyError:
			compare.notes and detected(d, None, 'added registration')
			continue

		changed = False
		for k, v in r.items():
			try:
				x = p[k]
			except KeyError:
				# No longer reached
				compare.warnings and detected(d, k, 'reachable added')
				warnings += 1
				changed = True
				continue

			if x == v:
				# No change, nothing to worry about.
				continue

			if odd_sequence(x, v):
				t = None if k == d else k
				compare.faults and detected(d, t, f'unexpected version change to "{d}" ({x} to {v})')
				faults += 1
				changed = True
				continue

			if k == d:
				continue	# Reference to itself.

			# Different version on reachable type.
			compare.warnings and detected(d, k, f'changed reachable version ({x} to {v})')
			warnings += 1
			changed = True

		a = r.keys()
		for t in p.keys():
			if t not in a:
				compare.warnings and detected(d, t, 'reachable removed')
				warnings += 1
				changed = True

		if changed and r[d] == p[d]:
			compare.faults and detected(d, None, 'reachables have changed while registration version has not')
			faults += 1

	c = current.keys()
	for s in previous.keys():
		if s not in c:
			compare.notes and detected(s, None, 'removed registration')

	if faults:
		s = f'{faults} faults and {warnings} warnings'
		x = Failed(compare_versions=(None, s))
		raise Incomplete(x)

def detected(document, reachable, text):
	if reachable:
		line = '%s (%s) - %s' % (document, reachable, text)
	else:
		line = '%s - %s' % (document, text)

	output_line(line)

def save_release(release, name):
	try:
		with open(name, 'w', encoding='utf-8') as f:
			for k, v in release.items():
				s = ','.join([f'{x}/{y}' for x, y in v.items()])
				f.write(f'{k}:{s}\n')
	except OSError as e:
		f = Failed(release_save=(e, None))
		raise Incomplete(f)

def load_release(name):
	try:
		with open(name, 'r', encoding='utf-8') as f:
			contents = f.read()
	except FileNotFoundError as e:
		return None

	release = {}
	lines = contents.splitlines()
	for ln in lines:
		doc = ln.split(':')
		d = doc[0]
		reachable = doc[1].split(',')
		for r in reachable:
			kv = r.split('/')
			try:
				a = release[d]
			except KeyError:
				a = {}
				release[d] = a
			major_minor(kv[1])
			a[kv[0]] = kv[1]
		if d not in release[d]:
			f = Failed(release_load=(None, f'document "{d}" does not include itself'))
			raise Incomplete(f)
	return release

#
#
OUTPUT_FILE = 'next-release.txt'
PRINT_TO_FILE = r'''
import ansar.encode.release as rl
with open(OUTPUT_FILE,'w',encoding = 'utf-8') as f:
	for k, v in rl.reachable.items():
		s = ','.join(['%s/%s' % (x.__art__.path, y) for x, y in v.items()])
		f.write('%s:%s\n' % (k.__art__.path, s))
'''

def load_module(version_module):
	dir, base = os.path.split(version_module)
	root, ext = os.path.splitext(base)

	if root == '' or ext != '.py':
		r = Rejected(module_load=(version_module, '[optional/path/]name.py'))
		raise Incomplete(r)
	relocated = None
	if dir:
		relocated = os.getcwd()
		os.chdir(dir)

	cwd = os.getcwd()
	header = 'import sys\nsys.path.insert(0,"%s")\nimport %s\nOUTPUT_FILE = "%s"\n%s\n'
	code = header % (cwd, root, OUTPUT_FILE, PRINT_TO_FILE)

	try:
		# Generate.
		exec(code)
	except ModuleNotFoundError as e:
		f = Failed(module_load=(e, None))
		raise Incomplete(f)
	except (CodingProblem, MessageRegistrationError) as e:
		f = Failed(module_load=(e, None))
		raise Incomplete(f)
	except SyntaxError as e:
		f = Failed(module_load=(None, 'improper configuration values, e.g. module name includes dashes?'))
		raise Incomplete(f)

	current = load_release(OUTPUT_FILE)
	if current is None:
		f = Failed(module_internal=(None, f'no output file "{OUTPUT_FILE}" generated'))
		raise Incomplete(f)

	os.remove(OUTPUT_FILE)
	if relocated:
		os.chdir(relocated)
	return current
