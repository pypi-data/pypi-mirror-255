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

"""Command-line tool for the ansar-encode library.

.
"""
__docformat__ = 'restructuredtext'

__all__ = [
	'main',
]

import ansar.encode as ar

# Parameters for the different sub-commands.
versioning_settings = ar.VersioningSettings()
compare_settings = ar.CompareSettings()
release_settings = ar.ReleaseSettings()

# Shims between the command-line and library procedures.
#
def versioning(settings, word):
	'''Print a human representation of the current version info. Returns nothing.'''
	version_module = ar.word_argument(0, word)
	return ar.procedure_versioned(versioning_settings, version_module)

def compare(settings, word):
	'''Compare the current version info against saved image of most recently released.'''
	version_module = ar.word_argument(0, word)
	release_file = ar.word_argument(1, word)
	return ar.procedure_compare(compare_settings, version_module, release_file)

def release(settings, word):
	'''Overwrite the saved image of version info with the current info.'''
	version_module = ar.word_argument(0, word)
	release_file = ar.word_argument(1, word)
	return ar.procedure_release(release_settings, version_module, release_file)

#
#
table = ar.jump_table(
	(versioning, versioning_settings),
	(compare, compare_settings),
	(release, release_settings),
)

def ansar():
	'''Version management in the build and release areas of software development.

	ansar versioning
	ansar --dump-settings
	* versioning
	Print the current version information on the console.
	* compare
	Compare the current version information against a saved image and report
	any issues. Any issue that might subvert the processing of versioned
	materials "in the wild" will result in a non-zero exit code.
	* release
	Update the saved image with the current version information. Subsequent
	use of the compare sub-command will be relative to the new image.
	'''
	settings = None

	sub_command, words = ar.command_words()
	if sub_command is None:
		return None

	# Everything lined up for execution of
	# the selected sub-command.
	output = sub_command(settings, words)
	return output

# Placeholder.
# Just add members and factory_settings parameter.
class Settings(object):
	def __init__(self):
		pass

SETTINGS_SCHEMA = {}

ar.bind(Settings, object_schema=SETTINGS_SCHEMA)

# Package entry-point. And a pretty standard
# code layout.
def main():
	ar.create_command(ansar, parameter_passing=ar.sub_command_passing, parameter_table=table)

# Python entry-point. Needed for debugging.
if __name__ == '__main__':
	main()
