# Author: Scott Woods <scott.18.ansar@gmail.com.com>
# MIT License
#
# Copyright (c) 2017-2024 Scott Woods
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
'''.

.
'''
import ansar.connect as ar

__all__ = [
	'main',
]

# Just need an object to stay "on duty" while the 
# global ServiceDirectory does its work.
def directory(self, settings):
	a = self.create(ar.ServiceDirectory, settings.directory_scope, settings.connect_above, settings.accept_below)
	m = self.select(ar.HostPort, ar.Completed, ar.Stop)
	if isinstance(m, ar.Completed):
		return m.value
	elif isinstance(m, ar.Stop):
		self.send(m, a)

	# Received HostPort or Stop.
	m = self.select(ar.Completed, ar.Stop)
	if isinstance(m, ar.Completed):
		return m.value
	return ar.Aborted()

ar.bind(directory)

#
#
class Settings(object):
	def __init__(self, directory_scope=None, connect_above=None, accept_below=None):
		self.directory_scope = directory_scope or ar.ScopeOfService.HOST
		self.connect_above = connect_above or ar.HostPort()
		self.accept_below = accept_below or ar.HostPort()

SETTINGS_SCHEMA = {
	'directory_scope': ar.ScopeOfService,
	'connect_above': ar.Any(),
	'accept_below': ar.UserDefined(ar.HostPort),
}

ar.bind(Settings, object_schema=SETTINGS_SCHEMA)

factory_settings = Settings(directory_scope=ar.ScopeOfService.HOST,
	connect_above=ar.LocalPort(32175))

#
#
def main():
    ar.create_object(directory, factory_settings=factory_settings)

# The standard entry point. Needed for IDEs
# and debugger sessions.
if __name__ == '__main__':
    main()
