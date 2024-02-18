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

import sys
import json

from .support import *
from .message import *
from .portable import *
from .convert import *
from .codec import *
from .json import *
from .file import *

__all__ = [
	'CommandError',
	'value_type',
	'word_argument',
	'word_argument_2',
	'argv0',
	'program_path',
	'program_name',
	'program_extent',
	'file_recover',
	'file_store',
	'input_decode',
	'output_encode',
	'output_line',
	'output_human',
	'command_error',
]

#
#
CommandError = (TypeError, AttributeError, ValueError, IndexError, KeyError, OSError)

#
#
argv0 = sys.argv[0]
program_path, program_name, program_extent = breakpath(argv0)

#
#
def value_type(value):
	t = fix_expression(type(value), {})
	return t

#
#
def word_argument(i, w):
	if i < len(w):
		return w[i]
	return None

def word_argument_2(w, a, d, name):
	if w is not None:
		if a is not None:
			t = f'a value for "{name}" detected as a word and an argument'
			raise Incomplete(Faulted(t))
		return w
	return a or d


#
#
def file_recover(name, t, decorate_names=False):
	f = File(name, t, decorate_names=decorate_names)
	r = f.recover()
	return r

def file_store(name, value, t=None, decorate_names=False, pretty_format=True):
	f = File(name, t, decorate_names=False, pretty_format=pretty_format)
	f.store(value)

#
#
def input_decode(t):
	#utf8_input  = io.TextIOWrapper(sys.stdin.buffer,  encoding='utf-8', errors='strict')
	input = sys.stdin.read()

	codec = CodecJson()
	value = codec.decode(input, t)
	return value

def output_encode(value, t=None, pretty_format=True):
	codec = CodecJson(pretty_format=pretty_format)
	if t is None:
		t = value_type(value)
	output = codec.encode(value, t)

	sys.stdout.write(output)
	sys.stdout.write('\n')

# Human-readable representation of
# output value.
def output_Boolean(value, t): return '<true>' if value else '<false>'
def output_Byte(value, t):
	s = chr(value)
	s = repr(s)
	s = s[1:-1]
	return f'[{s}]'
def output_Character(value, t):
	s = value.decode()
	s = repr(s)
	s = s[1:-1]
	return f"'{s}'"
def output_Rune(value, t):
	return f'"{value}"'
def output_Integer2(value, t): return str(value)
def output_Integer4(value, t): return str(value)
def output_Integer8(value, t): return str(value)
def output_Unsigned2(value, t): return str(value)
def output_Unsigned4(value, t): return str(value)
def output_Unsigned8(value, t): return str(value)
def output_Float4(value, t): return str(value)
def output_Float8(value, t): return str(value)
def output_Block(value, t):
	s = value.decode()
	s = repr(s)
	s = s[1:-1]
	return f'[{s}]'
def output_String(value, t):
	s = value.decode()
	s = repr(s)
	s = s[1:-1]
	return f"'{s}'"
def output_Unicode(value, t):
	return f'"{value}"'
def output_Enumeration(value, t): return t.to_name(value)
def output_ClockTime(value, t): return clock_to_text(value)
def output_TimeSpan(value, t): return span_to_text(value)
def output_WorldTime(value, t): return world_to_text(value)
def output_TimeDelta(value, t): return delta_to_text(value)
def output_UUID(value, t): return str(value)

def output_Type(value, t):
	s = value.__art__.path
	return f'<{s}>'
def output_TargetAddress(value, t): return f'-{value}'
def output_Address(value, t): return f'+{value}'

def output_Word(value, t):
	s = json.dumps(value)
	return s

output_table = {
	Boolean: output_Boolean,
	Byte: output_Byte,
	Character: output_Character,
	Rune: output_Rune,
	Block: output_Block,
	String: output_String,
	Unicode: output_Unicode,
	Integer2: output_Integer2,
	Integer4: output_Integer4,
	Integer8: output_Integer8,
	Unsigned2: output_Unsigned2,
	Unsigned4: output_Unsigned4,
	Unsigned8: output_Unsigned8,
	Float4: output_Float4,
	Float8: output_Float8,
	Enumeration: output_Enumeration,
	ClockTime: output_ClockTime,
	TimeSpan: output_TimeSpan,
	WorldTime: output_WorldTime,
	TimeDelta: output_TimeDelta,
	UUID: output_UUID,
	Type: output_Type,
	TargetAddress: output_TargetAddress,
	Address: output_Address,
	Word: output_Word,
}

COMPACT = (
	Boolean,
	Byte, Character, Rune,
	Integer2, Integer4, Integer8,
	Float4, Float8,
	Enumeration,
	WorldTime, ClockTime, TimeSpan,
	UUID,
	Type,
	TargetAddress, Address,
	Word,
)

def output_human(value, member=None, t=None, tab=0, bread=None):
	if bread is None:
		bread = set()

	if t is None:
		t = UserDefined(type(value))

	singular = isinstance(member, bytes)
	if isinstance(member, int):
		member = f'[{member}]: '
	elif singular:
		c = member.decode()
		member = f'{c} '
	elif member is None:
		member = ''
	else:
		member = f'{member}: '

	f = output_table.get(type(t), None)
	if f is not None:
		if value is None:
			output_line(f'{member}<null>', tab=tab)
		else:
			s = f(value, t)
			#output_line(f'{member}: {s}', tab=tab)
			output_line('%s%s' % (member, s), tab=tab)

	elif isinstance(t, UserDefined):
		e = t.element
		r = e.__art__
		s = r.value
		name = r.name

		def compact():
			for k, v in s.items():
				if type(v) not in COMPACT:
					return False
			return True

		if len(s) == 0:
			output_line(f'{member}{name}()', tab=tab)
		elif len(s) < 11 and compact():
			v = ['%s=%s' % (k, output_table[type(v)](getattr(value, k), v)) for k, v in s.items()]
			v = ', '.join(v)
			output_line(f'{member}{name}({v})', tab=tab)
		else:
			output_line(f'{member}{name}', tab=tab)

			for k, v in s.items():
				d = getattr(value, k)
				output_human(d, member=k, t=v, tab=tab + 1, bread=bread)

	elif isinstance(t, ArrayOf):
		e = type(t.element)
		if len(value) == 0:
			output_line(f'{member}(array)[]', tab=tab)
		elif len(value) < 11 and e in COMPACT:
			v = [output_table[e](x, e) for x in value]
			v = ', '.join(v)
			output_line(f'{member}(array)[{v}]', tab=tab)
		elif e in COMPACT:
			output_line(f'{member}(array)[', tab=tab)
			for i in range(0, len(value), 10):
				v = value[i:i + 10]
				v = [output_table[e](x, t) for x in v]
				v = ', '.join(v)
				output_line(v, tab=tab + 1)
			output_line(']', tab=tab)
		else:
			output_line(f'{member}(array)[{t.size}]', tab=tab)
			for i, d in enumerate(value):
				output_human(d, member=i, t=t.element, tab=tab + 1, bread=bread)

	elif isinstance(t, VectorOf):
		e = type(t.element)
		if len(value) == 0:
			output_line(f'{member}(vector)[]', tab=tab)
		elif len(value) < 11 and e in COMPACT:
			v = [output_table[e](x, e) for x in value]
			v = ', '.join(v)
			output_line(f'{member}(vector)[{v}]', tab=tab)
		elif e in COMPACT:
			output_line(f'{member}(vector)[', tab=tab)
			for i in range(0, len(value), 10):
				v = value[i:i + 10]
				v = [output_table[e](x, t) for x in v]
				v = ', '.join(v)
				output_line(v, tab=tab + 1)
			output_line(']', tab=tab)
		else:
			output_line(f'{member}(vector)', tab=tab)
			for i, d in enumerate(value):
				output_human(d, member=i, t=t.element, tab=tab + 1, bread=bread)

	elif isinstance(t, SetOf):
		e = type(t.element)
		if len(value) == 0:
			output_line(f'{member}(set){{}}', tab=tab)
		elif len(value) < 11 and e in COMPACT:
			v = [output_table[e](x, e) for x in value]
			v = ', '.join(v)
			output_line('%s(set){%s}' % (member, v), tab=tab)
		elif e in COMPACT:
			output_line(f'{member}(set){{', tab=tab)
			x = iter(value)
			n = len(value)
			for i in range(0, n, 10):
				r = n - i
				p = min(r, 10)
				v = [next(x) for i in range(p)]
				v = [output_table[e](y, e) for y in v]
				v = ', '.join(v)
				output_line(v, tab=tab + 1)
			output_line('}', tab=tab)
		else:
			output_line(f'{member}(set)', tab=tab)
			for d in value:
				output_human(d, b'#', t=t.element, tab=tab + 1, bread=bread)

	elif isinstance(t, MapOf):
		k = type(t.key)
		v = type(t.value)
		if len(value) == 0:
			output_line(f'{member}{{}}', tab=tab)
		elif k in COMPACT and v in COMPACT:
			if len(value) < 11:
				v = [(output_table[k](a, type(t.key)), output_table[v](b, type(t.value))) for a, b in value.items()]
				v = [f'{t[0]}: {t[1]}' for t in v]
				v = ', '.join(v)
				output_line('%s(map){%s}' % (member, v), tab=tab)
			else:
				output_line(f'{member}(map){{', tab=tab)
				for a, b in value.items():
					x, y = output_table[k](a, type(t.key)), output_table[v](b, type(t.value))
					output_line(f'{x}: {y}', tab=tab + 1)
				output_line('}', tab=tab)
		else:
			output_line(f'{member}(map){{', tab=tab)
			for k, v in value.items():
				output_human(k, member=b'@', t=t.key, tab=tab + 1, bread=bread)
				output_human(v, member=b'=', t=t.value, tab=tab + 1, bread=bread)
			output_line('}', tab=tab)
	elif isinstance(t, DequeOf):
		e = type(t.element)
		if len(value) == 0:
			output_line(f'{member}(deque)[]', tab=tab)
		elif len(value) < 11 and e in COMPACT:
			v = [output_table[e](x, e) for x in value]
			v = ', '.join(v)
			output_line(f'{member}(deque)[{v}]', tab=tab)
		elif e in COMPACT:
			output_line(f'{member}(deque)[', tab=tab)
			x = iter(value)
			n = len(value)
			for i in range(0, n, 10):
				r = n - i
				p = min(r, 10)
				v = [next(x) for i in range(p)]
				v = [output_table[e](y, e) for y in v]
				v = ', '.join(v)
				output_line(v, tab=tab + 1)
			output_line(']', tab=tab)

		else:
			output_line(f'{member}(deque)[', tab=tab)
			for i, d in enumerate(value):
				output_human(d, member=i, t=t.element, tab=tab + 1, bread=bread)
			output_line(']', tab=tab)

	elif isinstance(t, PointerTo):
		x = id(value)
		output_line(f'{member}(pointer)[{x:08x}]', tab=tab)
		if value is None:
			output_line(f'* <null>', tab=tab + 1)
		elif id(value) in bread:
			output_line(f'* (circular reference)', tab=tab + 1)
		else:
			bread.add(id(value))
			output_human(value, member=b'*', t=t.element, tab=tab + 1, bread=bread)

	elif isinstance(t, Any):
		output_line(f'{member}(any)', tab=tab)
		if value is None:
			output_line(f'? <null>', tab=tab + 1)
		else:
			output_human(value, member=b'?', t=UserDefined(type(value)), tab=tab + 1, bread=bread)

#
#
def output_line(line, tab=0, newline=True, **kv):
	if kv:
		line = line.format(**kv)

	if tab:
		sys.stdout.write('+   ' * tab)

	sys.stdout.write(line)
	if newline:
		sys.stdout.write('\n')

#
#
def command_error(fault):
	sys.stderr.write(f'{program_name}: {fault}\n')
