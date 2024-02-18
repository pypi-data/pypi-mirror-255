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
'''A network fixture that creates directories for connected clients.

Rather than a unique network address (IP + port) per directory, this
process uses a single address while managing multiple directories. Multiple
deployments of different products or different instances of the same
product can be supported.
'''
import ansar.connect as ar
from ansar.connect.directory import find_overlap

__all__ = [
	'main',
]

# All the states for all the machines in
# this module.
class INITIAL: pass
class STARTING: pass
class READY: pass
class CLEARING: pass

CONNECT_ABOVE_TABLE = ar.MapOf(ar.Unicode(), ar.Any())

# The process object.
#
class InstantDirectory(ar.Threaded, ar.StateMachine):
	def __init__(self, settings):
		ar.Threaded.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.settings = settings
		self.public_access = None		# This fixture listens here.
		self.accepted = {}				# Connected clients.
		self.directory = {}				# Directory per product+instance.
		self.connect_above = {}			# Upward link per product+instance.
		self.sub_directory = {}			# Sub-directories to directory.
		self.model = None				# File storage of connect_above.
		self.store = None				# Storage methods.
		self.recover = None

def InstantDirectory_INITIAL_Start(self, message):
	model = ar.object_model_folder()
	if model is None:
		self.complete(ar.Failed(model_load=(None, 'no model storage')))

	self.model = model.file('connect-above', CONNECT_ABOVE_TABLE, create_default=True)

	# Custom I/O routines.
	def store(connect_above=None):
		connect_above = connect_above or self.connect_above
		self.model.store(connect_above)

	def recover():
		self.connect_above, _ = self.model.recover()
		return self.connect_above
	
	self.store = store
	self.recover = recover

	# Initial load.
	self.recover()

	ar.listen(self, self.settings.public_access)
	return STARTING

# Verify access
def InstantDirectory_STARTING_Listening(self, message):
	self.public_access = message
	return READY

def InstantDirectory_STARTING_NotListening(self, message):
	# Something wrong. Bail.
	self.complete(ar.Faulted('No public access for FOH', message.error_text))

def InstantDirectory_STARTING_Stop(self, message):
	# External intervention.
	self.complete(ar.Aborted())

# Connections from IP clients.
def InstantDirectory_READY_Accepted(self, message):
	# Need to remember connection details for full
	# operation of directories. Accepted messages
	# will be forwarded later to appropriate
	# directories.
	self.accepted[self.return_address] = message

	acc = message.accepted_ipp
	ipp = f'{acc.host}:{acc.port}'
	self.trace(f'Accepted client at "{ipp}"')
	return READY

def InstantDirectory_READY_Abandoned(self, message):
	# Need to generate abandon messages for the
	# relevant directories.
	p = self.accepted.pop(self.return_address, None)
	if p is None:
		self.warning(f'Abandoned by unknown client')
		return READY

	acc = p.accepted_ipp
	ipp = f'{acc.host}:{acc.port}'

	sub_directory, directory = find_overlap(self.sub_directory, self.return_address)
	if sub_directory is None:
		self.trace(f'Abandoned by client at "{ipp}" (not registered as sub-directory')
		return READY

	self.forward(message, directory, self.return_address)
	self.trace(f'Abandoned by client at "{ipp}"')

	return READY

def InstantDirectory_READY_Closed(self, message):
	# Need to generate abandon messages for the
	# relevant directories.
	p = self.accepted.pop(self.return_address, None)
	if p is None:
		self.warning(f'Close of unknown client')
		return READY

	acc = p.accepted_ipp
	ipp = f'{acc.host}:{acc.port}'

	self.trace(f'Close of client at "{ipp}"')

	return READY

def InstantDirectory_READY_InstantLookup(self, message):
	settings = self.settings

	product_name = message.product_name or 'acme'
	product_instance = message.product_instance or 'development'
	k = f'{product_name}:{product_instance}'

	d = self.directory.get(k)
	if d is None:
		c = self.connect_above.get(k)
		if c is None:
			c = settings.connect_above			# Start with common default.
			self.connect_above[k] = c
			self.store()

		d = self.create(ar.ServiceDirectory,
			settings.directory_scope,			# All at same scope.
			c,
			ar.HostPort())						# Disabled.

		self.assign(d, k)
		self.directory[k] = d

	self.sub_directory[self.return_address] = d
	return_address, accepted = find_overlap(self.accepted, self.return_address)
	if return_address:
		self.forward(accepted, d, return_address)
	self.reply(ar.YourInstant(d))
	return READY

def InstantDirectory_READY_HostPort(self, message):
	# Consume the redundant message. Listening by
	# all directories is disabled, so host-port
	# is empty.
	return READY

def InstantDirectory_READY_Completed(self, message):
	k = self.debrief()
	d = self.directory.pop(k, None)
	if d is None:
		self.warning(f'Termination of unknown object')
		return READY
	self.warning(f'Termination of directory "{k}", tearing down')
	
	# A directory has died. Force any sub-directories
	# to re-connect and thereby create a new
	# instance.
	for s, v in self.sub_directory.items():
		if v == d:
			self.send(ar.Close(), s)

	return READY

def InstantDirectory_READY_Stop(self, message):
	if self.working():
		self.abort()
		return CLEARING
	self.complete(ar.Ack())

def InstantDirectory_CLEARING_Completed(self, message):
	self.debrief()
	if self.working():
		return CLEARING
	self.complete(ar.Ack())

INSTANT_DIRECTORY_DISPATCH = {
    INITIAL: (
        (ar.Start,), ()
    ),
    STARTING: (
        (ar.Listening, ar.NotListening, ar.Stop), ()
    ),
    READY: (
        (ar.Accepted, ar.Abandoned, ar.Closed,
		ar.InstantLookup, ar.HostPort,
		ar.Completed,
		ar.Stop), ()
    ),
    CLEARING: (
        (ar.Completed), ()
    ),
}

ar.bind(InstantDirectory, INSTANT_DIRECTORY_DISPATCH)


# Allow configuration of network details.
#
class Settings(object):
	def __init__(self, directory_scope=None, connect_above=None, accept_below=None, public_access=None):
		self.directory_scope = directory_scope
		self.connect_above = connect_above
		self.public_access = public_access or ar.HostPort()

SETTINGS_SCHEMA = {
	'directory_scope': ar.ScopeOfService,
	'connect_above': ar.Any(),
	'public_access': ar.UserDefined(ar.HostPort),
}

ar.bind(Settings, object_schema=SETTINGS_SCHEMA)

#
#
factory_settings = Settings(directory_scope=ar.ScopeOfService.HOST,
	connect_above=ar.HostPort(),
	public_access=ar.LocalPort(32174))

#
#
def main():
    ar.create_object(InstantDirectory, factory_settings=factory_settings)

# The standard entry point. Needed for IDEs
# and debugger sessions.
if __name__ == '__main__':
    main()
