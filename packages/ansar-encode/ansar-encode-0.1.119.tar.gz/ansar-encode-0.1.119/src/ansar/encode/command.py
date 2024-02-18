# Author: Scott Woods <scott.18.ansar@gmail.com.com>
# MIT License
#
# Copyright (c) 2022-2023 Scott Woods
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

"""Implementation of the command concept.

Specification of the standard settings/parameters and access to
the values extracted at runtime.
"""
__docformat__ = 'restructuredtext'

__all__ = [
	'CommandSettings',
	'command_settings',
	'command_executable',
	'command_args',
	'command_words',
	'command_variables',
	'command_unknown',
	'command_custom_settings',
	'command_passing',
	'sub_command_passing',
	'load_args',
	'load_variables',
	'load_settings',
	'load_input',
	'command_output',
	'create_command',
]

import sys

from .args import *
from .portable import *
from .message import *
from .support import *
from .runtime import *
from .primitive import *
from .file import *
from .codec import *
from .json import *

#
#
class CommandSettings(object):
	def __init__(self, pure_command=False,
		settings_file=None,
		input_file=None, output_file=None,
		dump_settings=False, dump_input=False,
		pretty_output=True,
		help=False):
		self.pure_command = pure_command
		self.settings_file = settings_file
		self.input_file = input_file
		self.output_file = output_file
		self.dump_settings = dump_settings
		self.dump_input = dump_input
		self.pretty_output = pretty_output
		self.help = help

COMMAND_SETTINGS_SCHEMA = {
	'pure_command': Boolean(),
	'settings_file': Unicode(),
	'input_file': Unicode(),
	'output_file': Unicode(),
	'dump_settings': Boolean(),
	'dump_input': Boolean(),
	'pretty_output': Boolean(),
	'help': Boolean(),
}

bind_message(CommandSettings, object_schema=COMMAND_SETTINGS_SCHEMA)


command_settings = CommandSettings()

#
#
cc = Gas(environment_variables={}, command_executable=None, command_args=[], command_words=[], unknown_args=None, custom_settings=None)

#
#
def command_variables():
	"""Global access to the values decoded from the environment. Returns the variables object."""
	return cc.environment_variables

def command_executable():
	"""Global access to the host executable. Returns a str."""
	return cc.command_executable

def command_args():
	"""Global access to the words appearing on the command-line. Returns a list of words."""
	return cc.command_args

def command_words():
	"""Global access to the words appearing on the command-line. Returns a list of words."""
	return cc.command_words

def command_unknown():
	"""Global access to the settings specific to a command."""
	return cc.custom_settings

def command_custom_settings():
	"""Global access to the settings specific to a command."""
	return cc.custom_settings

# Standard parameter processing. Check for name collision.
#
def command_passing(special_settings):
	if special_settings is not None:
		a = command_settings.__art__.value.keys()
		b = special_settings.__art__.value.keys()
		c = set(a) & set(b)
		if len(c) > 0:
			j = ', '.join(c)
			raise ValueError('collision in settings names - {collisions}'.format(collisions=j))
	executable, word, ls = break_args()
	x, r = extract_args(command_settings, ls, special_settings)
	arg_values(command_settings, x)
	return executable, word, r

#
#
def sub_command_passing(specific_settings, table):
	if specific_settings is not None:
		a = command_settings.__art__.value.keys()	# All commands.
		b = specific_settings.__art__.value.keys()	# This command.
		c = set(a) & set(b)
		if len(c) > 0:
			j = ', '.join(c)
			raise ValueError(f'collision in settings names - {j}')

	executable, ls1, sub, ls2, word = sub_args()
	x1, r1 = extract_args(command_settings, ls1, specific_settings)
	arg_values(command_settings, x1)

	def no_sub_required(s):
		return s.help or s.dump_settings or s.dump_input

	sub_command = None
	if sub is not None:
		try:
			fs = table[sub]
			sub_command = fs[0]
			sub_settings = fs[1]
		except (KeyError, IndexError):
			raise ValueError(f'unknown sub-command "{sub}"')

		if sub_settings:
			x2, r2 = extract_args(sub_settings, ls2, None)
			arg_values(sub_settings, x2)
		else:
			r2 = ls2
	elif no_sub_required(command_settings):
		# Give framework a chance to complete some
		# admin operation.
		r2 = ({}, {})
	else:
		raise ValueError('no-op command')

	lf, sf = r2
	if len(lf) or len(sf):
		lk, sk = lf.keys(), sf.keys()
		ld = [k for k in lk]
		sd = [k for k in sk]
		ld.extend(sd)
		detected = ', '.join(ld)
		raise ValueError(f'unknown settings ({detected}) detected in sub-arguments')

	bundle = (sub_command, word)

	return executable, bundle, r1

#
#
def load_args(factory_settings, passing, table):
	try:
		# Parse out args vs words, split into framework settings
		# vs command.
		if table is None:
			executable, word, args = passing(factory_settings)
		else:
			executable, word, args = passing(factory_settings, table)

	except CommandError as e:
		f = Failed(command_args=(e, 'not a properly formed command line'))
		raise Incomplete(f)
	
	return executable, word, args

def load_variables(factory_variables):
	if factory_variables is None:
		return None
	try:
		variables = environment_variables(factory_variables)

	except CommandError as e:
		f = Failed(command_variables=(e,'cannot process environment variables'))
		raise Incomplete(f)

	return variables

def load_settings(factory_settings, args, upgrade):
	unknown = None
	if factory_settings is None:
		return None, unknown

	if not is_message(factory_settings):
		t = tof(factory_settings)
		f = Failed(command_settings=(None, 'object "{t}" is not a registered message'))
		raise Incomplete(f)

	tos = value_type(factory_settings)
	try:
		if command_settings.settings_file:
			settings, v = file_recover(command_settings.settings_file, tos)
		else:
			settings, v = factory_settings, None

		if v is not None:
			mismatch = f'mismatched version ({v}) of settings'
			if not upgrade:
				f = Failed(settings_upgrade=(mismatch, 'no upgrade feature available'))
				raise Incomplete(f)
			try:
				settings = upgrade(settings, v)
			except CommandError as e:
				f = Failed(settings_upgrade=(mismatch, e))
				raise Incomplete(f)

		x, r = extract_args(settings, args, None)
		if len(r[0]) > 0 or len(r[1]) > 0:
			lf, sf = r
			lk, sk = lf.keys(), sf.keys()
			ld = [k for k in lk]
			sd = [k for k in sk]
			ld.extend(sd)
			unknown = ', '.join(ld)
			#f = Failed(command_args=(None, f'unknown settings ({unknown}) detected in arguments'))
			#raise Incomplete(f)
		arg_values(settings, x)
	except (FileFailure, CodecFailed) as e:
		f = Failed(settings_load=(e, None))
		raise Incomplete(f)
	except CommandError as e:
		f = Failed(settings_load=(e, 'unexpected name or name/value mismatch?'))
		raise Incomplete(f)

	return settings, unknown

def load_input(factory_input, input_type, word, upgrade):
	if factory_input is None:
		return None

	toi = input_type or value_type(factory_input)
	try:
		# Explicit file has priority, then the presence/absence
		# of command-line words (e.g. files), then input
		# piped from the parent.
		if command_settings.input_file:
			input, v = file_recover(command_settings.input_file, toi)
		elif word:
			input, v = factory_input, None
		else:
			input, v = input_decode(toi)

		if v is not None:
			mismatch = f'mismatched version ({v}) of input'
			if not upgrade:
				f = Failed(input_upgrade=(mismatch, 'no upgrade feature available'))
				raise Incomplete(f)
			try:
				settings = upgrade(settings, v)
			except CommandError as e:
				f = Failed(input_upgrade=(mismatch, e))
				raise Incomplete(f)

	except (FileFailure, CodecFailed) as e:
		f = Failed(input_decode=(e, 'cannot decode input'))
		raise Incomplete(f)

	return input

def run_command(command, settings, input):
	output = None
	try:
		if settings:
			if input:
				return command(settings, input)
			return command(settings)
		elif input:
			return command(None, input)
		return command()
	except (KeyboardInterrupt, SystemExit):
		raise
	except Incomplete:
		raise
	except CommandError as e:
		output = Failed(command=(e, None))
	except Exception as e:
		output = Failed(command=(e, None))
	return output

def command_output(output):
	# Default exit code is success, i.e. framework operating properly.
	code = 0
	if output is None:
		return code

	def error_code():
		# Need a framework-specific exit code but also
		# need to honour any exit code specified in a
		# command fault.
		code = 171 if code == 0 else code
		return code

	# Command has faulted. If console-based (the default) put
	# diagnostic on stderr and terminate.
	if isinstance(output, Faulted):
		code = 172 if output.exit_code is None else output.exit_code
		if not command_settings.pure_command:
			command_error(output)
			return code

	# Place the command output/fault in a requested file.
	if command_settings.output_file:
		try:
			file_store(command_settings.output_file, output, t=Any())
			return code
		except (FileFailure, CodecFailed) as e:
			# Framework has faulted. Fault is the new
			# output.
			output = Failed(command_output=(e, None))
			if not command_settings.pure_command:
				command_error(output)
				return error_code()

	# Place the command output/fault or framework fault
	# on stdout.
	try:
		if not is_message(output):
			t = tof(output)
			output = Faulted(f'object returned a "{t}"', 'not a registered message')
			if not command_settings.pure_command:
				command_error(fault)
				return code

		if command_settings.pure_command:
			output_encode(output, t=Any())
		else:
			output_human(output)

	except (CodecFailed, OSError) as e:
		# Output does not encode or the stream/platform is
		# compromised. Worth trying to put diagnostic on stderr
		# but otherwise we are hosed.
		if not command_settings.pure_command:
			fault = Failed(command_output=(e, None))
			command_error(fault)
		return error_code()

	return code

#
#
def create_command(command,
	factory_settings=None, factory_input=None, input_type=None, factory_variables=None,
	upgrade=None,
	parameter_passing=command_passing, parameter_table=None):

	# Start with a command line of flags and words and declaration
	# information about what to expect in the way of parameters and
	# piped input, i.e. if any.

	try:
		# Break down the command line with reference to the
		# name/type information in the settings object.
		executable, words, args = load_args(factory_settings, parameter_passing, parameter_table)

		cc.command_executable = executable
		cc.command_words = words
		cc.command_args = args

		# Extract values from the environment with reference
		# to the name/type info in the variables object.
		variables = load_variables(factory_variables)

		cc.environment_variables = variables

		# Extract values from the words and args off the command
		# line, with reference to the name/type ino in the
		# settings object.
		settings, unknown = load_settings(factory_settings, args, upgrade)

		cc.unknown_args = unknown
		cc.settings = settings

		# Non-operational features, i.e. command object not called.
		# Place settings for this command on stdout.
		if command_settings.help:
			command_help(command, settings, parameter_table)
			raise Incomplete(None)
		elif command_settings.dump_settings:
			if settings is None:
				f = Failed(command_dump=(None, 'no settings defined'))
				raise Incomplete(f)
			try:
				output_encode(settings)
			except CodecFailed as e:
				f = Failed(command_dump=(e, None))
				raise Incomplete(f)
			raise Incomplete(None)

		# Read an encoding from stdin or a file (as according to
		# command_settings).
		input = load_input(factory_input, input_type, words, upgrade)

		cc.input = input

		# Non-operational features, i.e. command object not called.
		# Place input for this command on stdout.
		if command_settings.dump_input:
			if input is None:
				f = Failed(command_input=(None, 'no input defined'))
				raise Incomplete(f)
			try:
				output_encode(input, t=input_type)
			except CodecFailed as e:
				f = Failed(command_dump=(e, None))
				raise Incomplete(f)
			raise Incomplete(None)

		# Context is ready for the actual command.
		output = run_command(command, settings, input)

	except Incomplete as e:
		output = e.value

	code = command_output(output)

	sys.exit(code)


# Generate some help for command-line users,
# extracted from the settings class.
FURTHER_INFORMATION = '''Refer to the relevant libary web-pages for more detailed information on
this command. There are lists of the available parameters, descriptions
of how to properly represent complex values and tutorial information.'''

# A console request for info about a component.
def command_help(command, settings, table):
	def not_available(reason):
		f = Failed(command_help=(None, f'no help available ({reason})'))
		raise Incomplete(f)

	not_documented = 'command not documented'
	try:
		command_doc = command.__doc__
	except AttributeError:
		not_available(not_documented)

	if not command_doc:
		not_available(not_documented)

	# Break down the raw lines, esp with respect to
	# whether this command is sub-command based.
	command = command_doc.split('\n')
	command = [c.strip() for c in command]
	if len(command) > 2 and command[0] and not command[1]:
		tagline = command[0]
		description = command[2:]
	else:
		tagline = None
		description = command

	# Drop trailing, empty lines.
	while description and not description[-1]:
		description.pop()

	# Further split of settings according to whether
	# command has sub-commands.
	sub_command = None
	if table:
		# Synthesize a fake sub-command to catch any
		# lines of examples.
		notes = []
		name = None
		sub_command = {name: notes}

		for d in description:
			if d.startswith('* '):
				notes = []
				name = d[2:]
				sub_command[name] = notes
			elif d:
				sub_command[name].append(d)

	# Split the settings doc according to the type
	# info on the settings object.
	arg = None
	if settings is not None:
		not_documented = 'settings not documented'
		tos = type(settings)
		try:
			settings_doc = tos.__init__.__doc__
		except AttributeError:
			not_available(not_documented)

		if not settings_doc:
			not_available(not_documented)

		arguments = settings_doc.split('\n')
		arguments = [a.strip() for a in arguments]

		# Drop trailing, empty lines.
		while arguments and not arguments[-1]:
			arguments.pop()

		arg = {}
		notes = []
		name = None
		arg[name] = notes

		for a in arguments:
			if a.startswith('* '):
				notes = []
				name = a[2:]
				arg[name] = notes
			elif a:
				arg[name].append(a)

	# Presentation
	if table:
		output_line(f'Usage: {program_name} --<name>=<value>... <sub-command> --<name>=<value>... <word>...')
		if tagline:
			output_line(tagline)

		output_line(f'Examples:')
		for x in sub_command[None]:
			output_line(f'$ {x}')

		output_line(f'Sub-commands:')
		for s, note in sub_command.items():
			if s is None:
				continue
			output_line(f'* {s}')
			for n in note:
				output_line(n)

		if arg and len(arg) > 1:
			output_line(f'Settings:')
			for a in arg[None]:
				output_line(f'{a}')
			for a, note in arg.items():
				if a is None:
					continue
				output_line(f'* {a}')
				for n in note:
					output_line(n)

		output_line(f'Further information:')
		output_line(FURTHER_INFORMATION)
		return
	
	# Non sub-command.
	output_line(f'Usage: {program_name} --<name>=<value>... <word>...')
	if tagline:
		output_line(tagline)

	for d in description:
		output_line(d)

	if arg and len(arg) > 1:
		output_line(f'Settings:')
		for a in arg[None]:
			output_line(f'{a}')
		for a, note in arg.items():
			if a is None:
				continue
			output_line(f'* {a}')
			for n in note:
				output_line(n)

	output_line(f'Further information:')
	output_line(FURTHER_INFORMATION)
