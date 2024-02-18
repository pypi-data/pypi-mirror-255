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
__docformat__ = 'restructuredtext'

import ansar.create as ar
from .socketry import *
from .transporting import *
from .plumbing import *

__all__ = [
    'UseAddress',
    'NoAddress',
	'ConnectToAddress',
]

#
#
class UseAddress(object):
	def __init__(self, address=None):
		self.address = address

ar.bind(UseAddress, object_schema={'address': ar.Address()})

#
#
class NoAddress(object): pass

ar.bind(NoAddress)


#
#
class INITIAL: pass
class PENDING: pass
class CONNECTED: pass
class GLARING: pass
class CLOSING: pass

class GlareTimer(object):
	pass

ar.bind(GlareTimer)

#
#
class ConnectToAddress(ar.Point, ar.StateMachine):
	def __init__(self, ipp, keep_connected=True):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.ipp = ipp
		self.keep_connected = keep_connected

		self.started = None
		self.attempts = 0

		self.connected = None
		self.remote = None

		self.closing = None
		self.intervals = None
		self.retry = None

	def reschedule(self):
		if self.intervals is None:
			s = local_private_public(self.ipp.host)
			r = ip_retry(s)
			self.intervals = r
		
		if self.retry is None:
			self.retry = ar.smart_intervals(self.intervals)

		try:
			p = next(self.retry)
		except StopIteration:
			self.retry = None
			return False
	
		self.start(GlareTimer, p)
		return True

# INITIAL
# Launch this object.
def ConnectToAddress_INITIAL_Start(self, message):
	# Start from nothing.
	self.started = ar.world_now()
	connect(self, self.ipp)
	self.attempts = 1
	return PENDING

# PENDING
# Waiting for results of connect.
# Transport established.
def ConnectToAddress_PENDING_Connected(self, message):
	self.connected = message
	self.remote = self.return_address

	# Remote object is ready.
	self.send(UseAddress(self.return_address), self.parent_address)
	return CONNECTED

def ConnectToAddress_PENDING_NotConnected(self, message):
	# Attempt failed.
	# No session and no change of status for owner.
	# Schedule another or perhaps end of attempts.
	if self.reschedule():
		return GLARING

	x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
	self.complete(x)

def ConnectToAddress_PENDING_Stop(self, message):
	# Local termination.
	# Connected could be orphaned here.
	self.complete(ar.Aborted())

# CONNECTED
# Caretaker role. Pass app messages on to owner
# and wait for further control messages.
def ConnectToAddress_CONNECTED_Unknown(self, message):
	# Normal operation.	Forward app message on to proper target.
	self.forward(message, self.parent_address, self.return_address)
	return CONNECTED

def ConnectToAddress_CONNECTED_Abandoned(self, message):
	# Normal end of a session.
	# Are there intended to be others?
	if self.keep_connected:
		# Start the retries up again.
		self.started = ar.world_now()
		self.attempts = 0
		self.retry = None
		if self.reschedule():
			# Update the owner that the current session
			# is over.
			self.send(NoAddress(), self.parent_address)
			return GLARING
		# Will only happen on a retry value that
		# allows no retries.
		x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
		self.complete(x)

	# End of session and only wanted 1.
	self.complete(message)

def ConnectToAddress_CONNECTED_Stop(self, message):
	# This object ended by app. Take that as
	# signal to end this session and not activate retries.
	self.send(Close(ar.Aborted()), self.remote)
	return CLOSING

def ConnectToAddress_CONNECTED_Closed(self, message):
	# Local end has sent close to the proxy. Treat this
	# as a short-circuit version of above.
	self.complete(message.value)

# GLARING
# After a failed attempt or after abandoned.
def ConnectToAddress_GLARING_Unknown(self, message):
	# Non-control message sneaking through.
	self.forward(message, self.parent_address, self.return_address)
	return GLARING

def ConnectToAddress_GLARING_GlareTimer(self, message):
	connect(self, self.ipp)
	self.attempts += 1
	return PENDING

def ConnectToAddress_GLARING_Stop(self, message):
	# Drop GlareTimer
	self.complete(ar.Aborted())

# CLOSING
def ConnectToAddress_CLOSING_Abandoned(self, message):
	# Terminated by remote before close could get through.
	self.complete(message)

def ConnectToAddress_CLOSING_Closed(self, message):
	# Completion of CONNECTED-Stop.
	self.complete(message.value)

CONNECT_TO_ADDRESS_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	PENDING: (
		(Connected, NotConnected, ar.Stop), ()
	),
	CONNECTED: (
		(ar.Unknown, Abandoned, ar.Stop, Closed), ()
	),
	GLARING: (
		(ar.Unknown, GlareTimer, ar.Stop), ()
	),
	CLOSING: (
		(Abandoned, Closed), ()
	),
}

ar.bind(ConnectToAddress, CONNECT_TO_ADDRESS_DISPATCH)


