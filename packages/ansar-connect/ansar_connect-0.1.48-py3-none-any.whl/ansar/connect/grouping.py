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
__docformat__ = 'restructuredtext'

import ansar.create as ar
from .socketry import *
from .transporting import *
from .plumbing import *
from .networking import *

__all__ = [
	'GroupTable',
	'GroupUpdate',
	'ObjectGroup',
]

# The specification.
class GroupTable(object):
	def __init__(self, **member_frame):
		if 'member_frame' in member_frame or 'create' in member_frame or 'update' in member_frame:
			raise ValueError('names of members would hide GroupTable methods')
		self.member_frame = member_frame

	def create(self, owner, seconds=None, session=None):
		for k in self.member_frame.keys():
			setattr(self, k, None)	# Fill with blanks.
		a = owner.create(ObjectGroup, self.member_frame, seconds=seconds, session=session)
		return a

	def update(self, message):
		if message.key in self.member_frame:
			setattr(self, message.key, message.address)

# Runtime image.
class GroupUpdate(object):
	def __init__(self, key=None, address=None):
		self.key = key
		self.address = address

UPDATE_GROUP_SCHEMA = {
	'key': ar.Unicode(),
	'address': ar.Address(),
}

ar.bind(GroupUpdate, object_schema=UPDATE_GROUP_SCHEMA)

# Dedicated timers.
class GroupTimer(object): pass

ar.bind(GroupTimer)

class Group: pass

#
#
class INITIAL: pass
class PENDING: pass
class READY: pass
class CLEARING: pass

class ObjectGroup(ar.Point, ar.StateMachine):
	def __init__(self, table, seconds=None, session=None):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.table = table							# Rows of CreateFrames.
		self.seconds = seconds
		self.session = session
		self.created = None

		self.ready = Group()

#
#
def ObjectGroup_INITIAL_Start(self, message):
	if not self.table:
		self.complete(ar.Faulted('empty table', 'a group with no members has nothing to do'))

	if self.seconds is not None:
		self.start(GroupTimer, self.seconds)

	for k, v in self.table.items():
		setattr(self.ready, k, None)
		a = self.create(v.object_type, *v.args, **v.kw)
		self.assign(a, k)
	
	return PENDING

#
#
def ObjectGroup_PENDING_UseAddress(self, message):
	k = self.progress()
	if k is None:
		self.warning(f'Unknown sender {self.return_address}')
		return PENDING

	a = getattr(self.ready, k, None)
	if a:
		self.warning(f'Table entry "{k}" already on record (ignored)')
		return PENDING

	setattr(self.ready, k, message.address)
	def ready():
		for k, v in self.table.items():
			a = getattr(self.ready, k, None)
			if a is None:
				return False
		return True

	r = ready()
	if not self.session:
		self.send(GroupUpdate(k, message.address), self.parent_address)
		if r: 
			self.send(ar.Ready(), self.parent_address)
			return READY
		return PENDING

	if r:
		c = self.session
		a = self.create(c.object_type, self.ready, *c.args, **c.kw)
		self.assign(a, 1)
		self.created = a
		return READY

	return PENDING

def ObjectGroup_PENDING_NoAddress(self, message):
	k = self.progress()
	if k is None:
		self.warning(f'Unknown sender {self.return_address}')
		return PENDING

	a = getattr(self.ready, k, None)
	if a is None:
		self.warning(f'Table entry "{k}" was not on record')
		return PENDING

	setattr(self.ready, k, None)

	if not self.session:
		self.send(GroupUpdate(k, None), self.parent_address)

	return PENDING

def ObjectGroup_PENDING_Completed(self, message):
	k = self.debrief()
	if k is None:
		self.warning(f'Unknown sender {self.return_address}')
		return PENDING

	if k != 1:
		a = getattr(self.ready, k, None)

		if not self.session and a:
			self.send(GroupUpdate(k, None), self.parent_address)

	if self.working():
		self.closing = message.value
		self.abort()
		return CLEARING

	self.complete(message.value)

def ObjectGroup_PENDING_GroupTimer(self, message):
	self.closing = ar.TimedOut(message)
	self.abort()
	return CLEARING

def ObjectGroup_PENDING_Stop(self, message):
	self.closing = ar.Aborted()
	self.abort()
	return CLEARING

#
#
def ObjectGroup_READY_NoAddress(self, message):
	k = self.progress()
	if k is None:
		self.warning(f'Unknown sender {self.return_address}')
		return READY

	a = getattr(self.ready, k, None)
	if a is None:
		self.warning(f'Table entry "{k}" was not on record')
		return READY

	if not self.session:
		self.send(GroupUpdate(k, None), self.parent_address)
		self.send(ar.NotReady(), self.parent_address)
		return PENDING

	if self.working():
		self.closing = message
		self.abort()
		return CLEARING

	self.complete(message)

def ObjectGroup_READY_Completed(self, message):
	k = self.debrief()
	if k is None:
		self.warning(f'Unknown address {self.return_address}')
		return PENDING

	if k != 1:
		a = getattr(self.ready, k, None)
		if a is None:
			self.warning(f'Table entry "{k}" was not on record')

		if not self.session:
			self.send(GroupUpdate(k, None), self.parent_address)

	if self.working():
		self.closing = message.value
		self.abort()
		return CLEARING

	self.complete(None)

def ObjectGroup_READY_Unknown(self, message):
	if self.created:
		self.forward(message, self.created, self.return_address)
	else:
		self.forward(message, self.parent_address, self.return_address)
	return READY

def ObjectGroup_READY_Stop(self, message):
	self.closing = ar.Aborted()
	self.abort()
	return CLEARING

#
#
def ObjectGroup_CLEARING_Completed(self, message):
	k = self.debrief()
	if k is None:
		self.warning(f'Unknown address {self.return_address}')
		return CLEARING

	if not self.session:
		self.send(GroupUpdate(k, None), self.parent_address)

	if self.working():
		return CLEARING

	self.complete(self.closing)


OBJECT_GROUP_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	PENDING: (
		(UseAddress, NoAddress, ar.Completed, GroupTimer, ar.Stop), ()
	),
	READY: (
		(NoAddress, ar.Completed, ar.Unknown, ar.Stop), ()
	),
	CLEARING: (
		(ar.Completed,), ()
	),
}

ar.bind(ObjectGroup, OBJECT_GROUP_DISPATCH)
