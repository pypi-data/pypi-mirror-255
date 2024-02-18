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
'''Setup easy access from a client object to one or more network addresses.

The goal is to bring a set of network services together for general use
by a client object, i.e. the client expresses the need to use network services
at addresses "a", "b" and "c". This module arranges for delivery of the *object*
addresses for the remote objects at those network addresses.

The overall strategy is to accept a description of the desired connections
and to create a FSM that performs all the network operations, eventually
delivering a notification that all requested services are connected. The
client can then forge ahead without regard to the fact that the addresses
refer to object spread around the network.

Progress is reported to the client and used to update a local variable. The
setattr() function is used to assign the acquired network addresses to
attributes of the local variable, i.e. it becomes possible to

    self.send(Hey(), self.connected.reception)

Where "Hey()" is some application message, "connected" is the name of the local
variable and "reception" is the name of an acquired remote object address.

The connection machinery does things like automated retries and implementing
a sense of "all parties have successfully connected". Once that state is
achieved any abandonment by a remote service results in a complete teardown.
'''
__docformat__ = 'restructuredtext'

import ansar.create as ar
from .socketry import *
from .transporting import *
from .plumbing import *
from .networking import *

__all__ = [
	'ConnectingFlags',
	'SchedulingTimer',
	'GetReadyTimer',
	'GetConnected',
	'ConnectionUpdate',
	'ConnectToAddress',
]

ConnectingFlags = ar.Enumeration(
	CONNECTED=0x01,				# At least one present.
	READY=0x02,					# All present.
	GLARING=0x04,				# Scheduled attempts.
	PENDING=0x08,				# Pending response to connect().
	WORKING=(0x08 | 0x04),		# Pending or an attempt is scheduled.
	ADDED=0x10,
	LOST=0x20,
	EMPTY=0x40
)

# Dedicated timers.
class SchedulingTimer(object): pass
class GetReadyTimer(object): pass

ar.bind(SchedulingTimer)
ar.bind(GetReadyTimer)

# The local variable (e.g. a member of a FSM) that automates
# some interactions with the ConnectEngine and records the
# acquired addresses as attribute.
class GetConnected(object):
	def __init__(self, **kv):
		self.plan = kv
		for k in kv.keys():
			setattr(self, k, None)	# Fill with blanks,

	def create(self, owner, seconds=None, keep_connected=False):
		a = owner.create(ConnectEngine, self.plan, seconds, keep_connected)
		return a

	def update(self, message):
		if message.status & ConnectingFlags.ADDED:
			setattr(self, message.tag, message.address)
		elif message.status & ConnectingFlags.LOST:
			setattr(self, message.tag, None)
		return message.status

#
#
class ConnectionUpdate(object):
	def __init__(self, status=None, tag=None, address=None):
		self.status = status
		self.tag = tag
		self.address = address

CONNECTION_UPDATE_SCHEMA = {
	'status': ar.Integer8(),
	'tag': ar.Integer8(),
	'address': ar.Address(),
}

ar.bind(ConnectionUpdate, object_schema=CONNECTION_UPDATE_SCHEMA)

#
#
class INITIAL: pass
class CONNECTING: pass
class RUNNING: pass
class CLOSING: pass

class ConnectEngine(ar.Point, ar.StateMachine):
	def __init__(self, plan, seconds, keep_connected):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.plan = plan
		self.seconds = seconds
		self.keep_connected = keep_connected

		self.started = None
		self.attempts = 0
		self.pending = set()
		self.tagged = {}
		self.glaring = {}
		self.closing = None
		self.due = None

	def reschedule(self, tag):
		g = self.glaring.get(tag, None)
		if g is None:
			h = self.plan[tag][0].host
			s = local_private_public(h)
			r = ip_retry(s)
			g = [ar.smart_intervals(r), None]
			self.glaring[tag] = g

		try:
			p = next(g[0])
		except StopIteration:
			self.glaring.pop(tag, None)
			return False
	
		due = ar.clock_now() + p
		g[1] = due
		if self.due is None or due < self.due:
			self.start(SchedulingTimer, p)
			self.due = due
		return True

	def status(self):
		c = ConnectingFlags.CONNECTED if self.tagged else 0
		r = ConnectingFlags.READY if len(self.tagged) == len(self.plan) else 0
		g = ConnectingFlags.GLARING if self.due is not None else 0
		p = ConnectingFlags.PENDING if self.pending else 0
		e = 0 if self.tagged else ConnectingFlags.EMPTY

		return c | r | g | p | e

def ConnectEngine_INITIAL_Start(self, message):
	self.started = ar.world_now()

	if self.seconds is not None:
		self.start(GetReadyTimer, self.seconds)

	for k, v in self.plan.items():
		connect(self, v[0], tag=k)
		self.attempts += 1
		self.pending.add(k)

	return CONNECTING

def ConnectEngine_CONNECTING_Connected(self, message):
	t = message.tag
	self.tagged[t] = message
	self.pending.discard(t)
	self.glaring.pop(t, None)
	s = self.status() | ConnectingFlags.ADDED
	self.send(ConnectionUpdate(status=s, tag=t, address=self.return_address), self.parent_address)

	if s & ConnectingFlags.READY:
		return RUNNING

	return CONNECTING

def ConnectEngine_CONNECTING_NotConnected(self, message):
	t = message.tag
	self.pending.discard(t)
	self.tagged.pop(t, None)
	if self.reschedule(t):
		return CONNECTING

	self.cancel(SchedulingTimer)
	self.cancel(GetReadyTimer)

	self.closing = ar.Exhausted(message, attempts=self.attempts, started=self.started)
	if not self.tagged:
		self.complete(self.closing)

	for k, v in self.tagged.items():
		self.send(Close(), v.remote_address)
	return CLOSING

def ConnectEngine_CONNECTING_Abandoned(self, message):
	t = message.tag
	self.tagged.pop(t, None)
	s = self.status() | ConnectingFlags.LOST
	self.send(ConnectionUpdate(status=s, tag=t, address=self.return_address), self.parent_address)

	# Sticky connections are allowed to come and
	# go, even while still connecting.
	if self.keep_connected:
		if self.reschedule(t):
			return CONNECTING

	self.cancel(SchedulingTimer)
	self.cancel(GetReadyTimer)

	self.closing = message
	if not self.tagged:
		self.complete(message)

	for k, v in self.tagged.items():
		self.send(Close(), v.remote_address)
	return CLOSING

def ConnectEngine_CONNECTING_Closed(self, message):
	t = message.tag
	self.tagged.pop(t, None)
	s = self.status() | ConnectingFlags.LOST
	self.send(ConnectionUpdate(status=s, tag=t, address=self.return_address), self.parent_address)

	self.cancel(SchedulingTimer)
	self.cancel(GetReadyTimer)

	self.closing = message
	if not self.tagged:
		self.complete(message)

	for k, v in self.tagged.items():
		self.send(Close(), v.remote_address)
	return CLOSING

def ConnectEngine_CONNECTING_SchedulingTimer(self, message):
	self.due = None
	n = ar.clock_now() + 0.25
	expired = [k for k, v in self.glaring.items() if v[1] is not None and v[1] < n]
	for e in expired:
		connect(self, self.plan[e][0], tag=e)
		self.attempts += 1
		self.pending.add(e)
		self.glaring[e][1] = None	# Not longer part of timer calculations.

	due = None
	for k, v in self.glaring.items():
		d = v[1]
		if d is None:
			continue
		if due is None or d < due:
			due = d
	if due:
		p = due - ar.clock_now()
		self.trace(f'Schedule status check in {p} seconds')
		self.start(SchedulingTimer, p)
		self.due = due

	return CONNECTING

def ConnectEngine_CONNECTING_Unknown(self, message):
	self.forward(message, self.parent_address, self.return_address)
	return CONNECTING

def ConnectEngine_CONNECTING_Stop(self, message):
	self.cancel(SchedulingTimer)
	self.cancel(GetReadyTimer)

	self.closing = ar.Aborted()
	if not self.tagged:
		self.complete(self.closing)

	for k, v in self.tagged.items():
		self.send(Close(), v.remote_address)
	return CLOSING

def ConnectEngine_CONNECTING_GetReadyTimer(self, message):
	self.cancel(SchedulingTimer)

	to = ar.TimedOut(message)
	self.closing = ar.Exhausted(to, attempts=self.attempts, started=self.started)
	if not self.tagged:
		self.complete(self.closing)

	for k, v in self.tagged.items():
		self.send(Close(), v.remote_address)
	return CLOSING

# RUNNING
def ConnectEngine_RUNNING_Abandoned(self, message):
	t = message.tag
	self.tagged.pop(t, None)
	s = self.status() | ConnectingFlags.LOST
	self.send(ConnectionUpdate(status=s, tag=t, address=self.return_address), self.parent_address)

	if self.keep_connected:
		if self.reschedule(t):
			return CONNECTING

	self.closing = message
	if not self.tagged:
		self.complete(message)

	for k, v in self.tagged.items():
		self.send(Close(), v.remote_address)
	return CLOSING

def ConnectEngine_RUNNING_Closed(self, message):
	t = message.tag
	a = self.tagged.pop(t, None)
	s = self.status() | ConnectingFlags.LOST
	self.send(ConnectionUpdate(status=s, tag=t, address=self.return_address), self.parent_address)

	if self.keep_connected:
		if self.reschedule(t):
			return CONNECTING

	self.closing = message
	if not self.tagged:
		self.complete(message)

	for k, v in self.tagged.items():
		self.send(Close(), v.remote_address)
	return CLOSING

def ConnectEngine_RUNNING_Unknown(self, message):
	self.forward(message, self.parent_address, self.return_address)
	return CONNECTING

def ConnectEngine_RUNNING_Stop(self, message):
	self.closing = ar.Aborted()
	for k, v in self.tagged.items():
		self.send(Close(), v.remote_address)
	return CLOSING

# CLOSING
def ConnectEngine_CLOSING_Abandoned(self, message):
	t = message.tag
	self.tagged.pop(t, None)
	s = self.status() | ConnectingFlags.LOST
	self.send(ConnectionUpdate(status=s, tag=t, address=self.return_address), self.parent_address)

	if not self.tagged:
		self.complete(self.closing)
	return CLOSING

def ConnectEngine_CLOSING_Closed(self, message):
	t = message.tag
	a = self.tagged.pop(t, None)
	s = self.status() | ConnectingFlags.LOST
	self.send(ConnectionUpdate(status=s, tag=t, address=self.return_address), self.parent_address)

	if not self.tagged:
		self.complete(self.closing)
	return CLOSING

CONNECT_ENGINE_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	CONNECTING: (
		(Connected, NotConnected, Abandoned, Closed, SchedulingTimer, GetReadyTimer, ar.Unknown, ar.Stop), ()
	),
	RUNNING: (
		(Abandoned, Closed, ar.Unknown, ar.Stop), ()
	),
	CLOSING: (
		(Abandoned, Closed), ()
	),
}

ar.bind(ConnectEngine, CONNECT_ENGINE_DISPATCH)


# Dedicated timers.
class GlareTimer(object): pass

ar.bind(GlareTimer)

#
#
class PENDING: pass
class CONNECTED: pass
class GLARING: pass

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


