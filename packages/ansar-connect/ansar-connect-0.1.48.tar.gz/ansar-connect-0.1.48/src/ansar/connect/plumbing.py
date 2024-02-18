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

__all__ = [
	'RETRY_LOCAL',
	'RETRY_PRIVATE',
	'RETRY_PUBLIC',
	'ip_retry',
	'ConnectService',
	'AcceptClient',
	'ServiceUp',
	'ServiceDown',
	'ServiceNotUp',
]

# Reasonable intervals between connection attempts for
# the different scopes of address.
RETRY_LOCAL = ar.RetryIntervals(first_steps=[2.0, 4.0], regular_steps=8.0, step_limit=None, randomized=0.25, truncated=0.5)
RETRY_PRIVATE = ar.RetryIntervals(first_steps=[4.0, 8.0], regular_steps=16.0, step_limit=None, randomized=0.25, truncated=0.5)
RETRY_PUBLIC = ar.RetryIntervals(first_steps=[8.0, 16.0, 32.0], regular_steps=64.0, step_limit=None, randomized=0.25, truncated=0.5)

def ip_retry(s):
	if s == ScopeOfIP.OTHER:	# Not a dotted IP.
		return RETRY_PUBLIC

	if s == ScopeOfIP.LOCAL:		# Local - 127.
		return RETRY_LOCAL
	elif s == ScopeOfIP.PRIVATE:	# Private - 192.168.
		return RETRY_PRIVATE

	return RETRY_PUBLIC				# Domains?

#
#
class ServiceUp(object):
	def __init__(self, connected=None):
		self.connected = connected

class ServiceDown(object):
	def __init__(self, ended=None):
		self.ended = ended

class ServiceNotUp(object):
	def __init__(self, not_connected=None):
		self.not_connected = not_connected or NotConnected()

SHARED_SCHEMA = {
	"connected": ar.UserDefined(Connected),
	"ended": ar.Any(),
	"not_connected": ar.UserDefined(NotConnected),
}

ar.bind(ServiceUp, object_schema=SHARED_SCHEMA)
ar.bind(ServiceDown, object_schema=SHARED_SCHEMA)
ar.bind(ServiceNotUp, object_schema=SHARED_SCHEMA)

#
#
class INITIAL: pass
class CONNECTING: pass
class ESTABLISHED: pass
class PAUSING: pass
class CLOSING: pass
class STARTING: pass

class ConnectService(ar.Point, ar.StateMachine):
	def __init__(self, remote_ipp, tag, retry=None):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.remote_ipp = remote_ipp
		self.tag = tag

		if retry is None:
			s = local_private_public(remote_ipp.host)
			retry = ip_retry(s)

		self.retry = retry
		self.remote = None

def ConnectService_INITIAL_Start(self, message):
	self.intervals = iter(ar.smart_intervals(self.retry))
	connect(self, self.remote_ipp, session=None, tag=self.tag)
	return CONNECTING

def ConnectService_CONNECTING_Connected(self, message):
	self.remote = self.return_address
	self.forward(ServiceUp(message), self.parent_address, self.remote)
	return ESTABLISHED

def ConnectService_CONNECTING_NotConnected(self, message):
	seconds = next(self.intervals)
	self.send(ServiceNotUp(message), self.parent_address)
	self.start(ar.T1, seconds)
	return PAUSING

def ConnectService_CONNECTING_Stop(self, message):
	self.complete(ar.Aborted())

def ConnectService_ESTABLISHED_Unknown(self, message):
	self.forward(message, self.parent_address, self.remote)
	return ESTABLISHED

def ConnectService_ESTABLISHED_Closed(self, message):
	self.forward(ServiceDown(message), self.parent_address, self.remote)
	self.complete(message.value)

def ConnectService_ESTABLISHED_Abandoned(self, message):
	self.forward(ServiceDown(message), self.parent_address, self.remote)
	self.intervals = iter(ar.smart_intervals(self.retry))
	seconds = next(self.intervals)
	self.start(ar.T1, seconds)
	return PAUSING

def ConnectService_ESTABLISHED_Stop(self, message):
	self.send(Close(), self.remote)
	self.start(ar.T2, 3.0)
	return CLOSING

def ConnectService_CLOSING_Closed(self, message):
	self.complete(ar.Aborted())

def ConnectService_CLOSING_Abandoned(self, message):
	self.complete(ar.Aborted())

def ConnectService_CLOSING_T2(self, message):
	self.complete(ar.Aborted())

def ConnectService_PAUSING_T1(self, message):
	connect(self, self.remote_ipp, session=None, tag=self.tag)
	return CONNECTING

def ConnectService_PAUSING_Stop(self, message):
	self.complete(ar.Aborted())

CONNECT_SERVICE_DISPATCH = {
	INITIAL: (
		(ar.Start,),
		()
	),
	CONNECTING: (
		(Connected, NotConnected, ar.Stop),
		()
	),
	ESTABLISHED: (
		(ar.Unknown, Closed, Abandoned, ar.Stop),
		()
	),
	CLOSING: (
		(Closed, Abandoned, ar.T2),
		()
	),
	PAUSING: (
		(ar.T1, ar.Stop),
		()
	),
}

ar.bind(ConnectService, CONNECT_SERVICE_DISPATCH)

#
#
class AcceptClient(ar.Point, ar.StateMachine):
	def __init__(self, local_ipp, local_id, retry=None):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.local_ipp = local_ipp
		self.local_id = local_id

		if retry is None:
			s = local_private_public(local_ipp.host)
			retry = ip_retry(s)

		self.retry = retry
		self.listening = None
		self.local = {}
		self.closing = 0

def AcceptClient_INITIAL_Start(self, message):
	self.intervals = iter(ar.smart_intervals(self.retry))
	listen(self, self.local_ipp, tag=self.local_id)
	return STARTING

def AcceptClient_STARTING_Listening(self, message):
	self.listening = message
	self.send(message, self.parent_address)
	return ESTABLISHED

def AcceptClient_STARTING_NotListening(self, message):
	seconds = next(self.intervals)
	self.send(message, self.parent_address)
	self.start(ar.T1, seconds)
	return PAUSING

def AcceptClient_STARTING_Stop(self, message):
	self.complete(ar.Aborted())

def AcceptClient_ESTABLISHED_Accepted(self, message):
	self.local[self.return_address] = message
	self.forward(message, self.parent_address, self.return_address)
	return ESTABLISHED

def AcceptClient_ESTABLISHED_Unknown(self, message):
	self.forward(message, self.parent_address, self.return_address)
	return ESTABLISHED

def AcceptClient_ESTABLISHED_Abandoned(self, message):
	accepted = self.local.pop(self.return_address, None)
	if accepted:
		self.forward(message, self.parent_address, self.return_address)
	return ESTABLISHED

def AcceptClient_ESTABLISHED_Closed(self, message):
	AcceptClient_ESTABLISHED_Abandoned(self, message)
	return ESTABLISHED

def AcceptClient_ESTABLISHED_Stop(self, message):
	self.closing = len(self.local)
	if self.closing == 0:
		self.complete(ar.Aborted())

	c = Close()
	for a in self.local.keys():
		self.send(c, a)
	self.start(ar.T2, 3.0)
	return CLOSING

def AcceptClient_CLOSING_Closed(self, message):
	# !!!!!!!!!!!!!
	# self.forward(message, self.parent_address, self.return_address)
	self.closing -= 1
	if self.closing > 0:
		return CLOSING
	self.complete(ar.Aborted())

def AcceptClient_CLOSING_Abandoned(self, message):
	self.closing -= 1
	if self.closing > 0:
		return CLOSING
	self.complete(ar.Aborted())

def AcceptClient_CLOSING_T2(self, message):
	self.complete(ar.Aborted())

def AcceptClient_PAUSING_T1(self, message):
	listen(self, self.local_ipp, tag=self.local_id)
	return STARTING

def AcceptClient_PAUSING_Stop(self, message):
	self.complete(ar.Aborted())

ACCEPT_CLIENT_DISPATCH = {
	INITIAL: (
		(ar.Start,),
		()
	),
	STARTING: (
		(Listening, NotListening, ar.Stop),
		()
	),
	ESTABLISHED: (
		(Accepted, ar.Unknown, Abandoned, Closed, ar.Stop),
		()
	),
	CLOSING: (
		(Closed, Abandoned, ar.T2),
		()
	),
	PAUSING: (
		(ar.T1, ar.Stop),
		()
	),
}

ar.bind(AcceptClient, ACCEPT_CLIENT_DISPATCH)
