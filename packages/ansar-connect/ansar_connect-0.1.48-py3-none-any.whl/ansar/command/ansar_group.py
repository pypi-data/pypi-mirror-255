# Author: Scott Woods <scott.18.group@gmail.com.com>
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

__all__ = [
	'main',
]

import os
import ansar.connect as ar

#
#
class INITIAL: pass
class OPENING: pass
class RUNNING: pass
class PAUSED: pass
class CLEARING: pass
class RETURNING: pass

NO_RETRY = ar.RetryIntervals(step_limit=0)
GROUP_LISTEN = 'group'

def series(retry):
	if retry.step_limit == 0:
		return None
	if retry.first_steps or retry.regular_steps:
		return retry
	return None

#
#
class Group(ar.Point, ar.StateMachine):
	def __init__(self, settings):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.settings = settings
		self.group_roles = None			# Names of processes to be maintained.
		self.main_role = None
		self.group_start = None			# Moment the first process was started.
		self.directory_ipp = None
		self.return_value = {}			# Most recent completion value.
		self.get_return = None
		self.exhausted = set()
		self.restart_interval = {}		# Active iterators returning seconds.
		self.auto_restart = {}			# When to restart.
		self.due = None					# Time of nearest restart.
		self.auto_resume = set()		# Processes terminated during PAUSED.

	def restart(self, roles):
		hr = ar.object_role()
		hb = hr.home

		# Look for retry objects that will return a non-zero
		# length sequence of intervals.
		port = self.directory_ipp.port
		if port is not None:
			settings = [f'--group-port={port}']
		else:
			settings = None

		# Start the given list of roles. Remember any roles that
		# are no longer present.
		absentee = []
		for r in roles:
			if not hb.role_exists(r):
				absentee.append(r)
				self.trace(f'Role "{r}" not found, deleted during pause?')
				continue
			cr = hb.open_role(r, None, None, ar.NodeProperties())
			forwarding = r == self.main_role and self.settings.forwarding
			retry = series(cr.properties.retry) or series(hr.properties.retry) or NO_RETRY

			settings = [f'--group-port={port}']
			a = self.create(ar.Process, cr.properties.executable,
				forwarding=forwarding,
				home_path=hb.home_path, role_name=r, subrole=False,
				group_pid=os.getpid(),
				settings=settings)
			self.assign(a, [r, retry])

		# If the home/roles have changed underneath this group, there are
		# two options. Terminate immediately or acknowledge and continue.
		# This version follows the latter strategy, discarding any roles
		# that have disappeared.
		if absentee:
			self.group_roles = [r for r in self.group_roles if r not in absentee]

	def cancel_restarts(self):
		self.cancel(ar.T1)
		self.restart_interval = {}
		self.auto_restart = {}
		self.due = None

	def returned(self, value):
		d = self.debrief()
		if d is None:
			return [None, None]

		r, retry = d
		self.return_value[r] = value

		try:
			i = self.restart_interval[r]
		except KeyError:
			i = ar.smart_intervals(retry)
			self.restart_interval[r] = i

		try:
			s = next(i)
		except StopIteration:
			self.exhausted.add(r)
			self.restart_interval.pop(r, None)
			self.auto_restart.pop(r, None)
			if isinstance(value, ar.Faulted):
				self.trace(f'Role "{r}" exhausted, {value}')
			else:
				self.trace(f'Role "{r}" exhausted')
			return r, None
		
		return r, s

	def next_restart(self):
		lo = None
		for r, t in self.auto_restart.items():
			if lo is None or t < lo:
				lo = t
		return lo

	def end_run(self):
		if self.get_return:
			value = self.get_return()
		else:
			hb = ar.object_role().home

			stop = ar.world_now()
			delta = stop - self.group_start
			value = ar.GroupRun(home=hb.home_path,
				role=self.group_roles,
				start=self.group_start,
				stop=stop,
				seconds=delta.total_seconds(),
				completed=self.return_value)

		self.complete(value)

# FSM begins here.
#
def Group_INITIAL_Start(self, message):
	hr = ar.object_role()
	csv = self.settings.roles
	if not csv:
		self.complete(ar.Ack())		# Noop session. Fill in the group role.

	self.group_roles = csv.split(',')

	connect_above = self.settings.connect_above		# Defined in settings.
	accept_below = ar.LocalPort(0)					# Ephemeral listen.

	self.main_role = self.settings.main_role
	if self.main_role and self.settings.forwarding:
		hb = hr.home
		if hb.role_exists(self.main_role):
			tr = hb.open_role(self.main_role, None, None, ar.NodeProperties())
			if series(hr.properties.retry) or series(tr.properties.retry):
				r = ar.Rejected(forwarding_retry=(f'main role "{self.main_role}" is configured to retry', 'not supported'))
				self.complete(r)

	a = self.create(ar.ServiceDirectory, ar.ScopeOfService.GROUP, connect_above, accept_below)
	self.assign(a, None)
	return OPENING

def Group_OPENING_HostPort(self, message):
	self.directory_ipp = message
	self.group_start = ar.world_now()
	self.restart(self.group_roles)
	return RUNNING

def Group_OPENING_Completed(self, message):
	value = message.value
	if not isinstance(value, ar.Faulted):
		t = ar.tof(value)
		value = ar.Failed(group_directory=(None, f'internal directory terminated with a "{t}"'))
	self.complete(value)

def Group_OPENING_Stop(self, message):
	self.abort()
	return CLEARING

def Group_RUNNING_Completed(self, message):
	r, s = self.returned(message.value)

	def get():
		return message.value

	if r is None:					# Directory has stopped.
		self.cancel_restarts()		# Simplify termination.
		self.get_return = get
		if self.working():
			self.abort()
			return CLEARING
		self.end_run()

	if s is None:							# No retry.
		if r == self.main_role:				# Forced termination of others.
			self.cancel_restarts()			# Why would there be restarts
			self.abort()					# At least the directory.
			return RETURNING

		if self.working() > 1 or len(self.auto_restart) > 0:
			return RUNNING

		self.abort()		# Directory.
		return CLEARING

	self.trace(f'Restart in {s} seconds')
	
	t = ar.clock_now() + s
	if self.due is None or t < self.due:
		self.due = t
		self.start(ar.T1, s)
	self.auto_restart[r] = t

	return RUNNING

def Group_RUNNING_T1(self, message):
	hb = ar.object_role().home
	c = ar.clock_now() + 0.25
	
	expired = [r for r, p in self.auto_restart.items() if p < c]
	for r in expired:
		self.auto_restart.pop(r, None)
	self.restart(expired)

	t = self.next_restart()
	if t is None:
		self.due = None
	else:
		self.due = t
		s = t - ar.clock_now()
		self.start(ar.T1, s)

	return RUNNING

def Group_RUNNING_Resume(self, message):
	if not self.exhausted:
		self.trace('Nothing to resume')
		return RUNNING
	self.restart(self.exhausted)
	self.exhausted = set()
	return RUNNING

def Group_RUNNING_Pause(self, message):
	# Move pending retries to paused for a restart
	# when the pause is lifted. 
	self.auto_resume = set(self.auto_restart.keys())

	self.cancel_restarts()
	return PAUSED

def Group_RUNNING_Stop(self, message):
	self.abort()
	return CLEARING

def Group_PAUSED_Completed(self, message):
	r, _ = self.returned(message.value)

	def get():
		return message.value

	if r is None:
		self.get_return = get
		if self.working():
			self.abort()
			return CLEARING
		self.end_run()

	self.auto_resume.add(r)

	if r == self.main_role:
		if self.working():
			self.abort()
			return RETURNING
		self.complete(message.value)

	return PAUSED

def Group_PAUSED_Resume(self, message):
	hb = ar.object_role().home

	self.restart(self.auto_resume)
	self.auto_resume = set()
	return RUNNING

def Group_PAUSED_Stop(self, message):
	def get():
		return message.value

	if self.abort():
		return CLEARING

	self.end_run()

def Group_CLEARING_Completed(self, message):
	d = self.debrief()
	if d is not None:
		r, retry = d
		self.return_value[r] = message.value

	if self.working():
		return CLEARING

	self.end_run()

def Group_RETURNING_Completed(self, message):
	r, _ = self.returned(message.value)

	if self.working():
		return RETURNING

	value = self.return_value[self.main_role]
	self.complete(value)

GROUP_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	OPENING: (
		(ar.HostPort, ar.Completed, ar.Stop), ()
	),
	RUNNING: (
		(ar.Completed, ar.T1, ar.Resume, ar.Pause, ar.Stop), ()
	),
	PAUSED: (
		(ar.Completed, ar.Resume, ar.Stop), ()
	),
	CLEARING: (
		(ar.Completed,), ()
	),
	RETURNING: (
		(ar.Completed,), ()
	),
}

ar.bind(Group, GROUP_DISPATCH)

class Settings(object):
	def __init__(self, connect_above=None, roles=None, main_role=None, forwarding=False):
		self.connect_above = connect_above or ar.HostPort()
		self.roles = roles
		self.main_role = main_role
		self.forwarding = forwarding

SETTINGS_SCHEMA = {
	'connect_above': ar.Any(),
	'roles': ar.Unicode(),
	'main_role': ar.Unicode(),
	'forwarding': ar.Boolean(),
}

ar.bind(Settings, object_schema=SETTINGS_SCHEMA)

factory_settings = Settings()

# Entry point for packaging. The
# $ ansar-group command starts here.
def main():
	ar.create_node(Group, factory_settings=factory_settings, scope=ar.ScopeOfService.GROUP)

# The standard entry point. Needed for IDEs
# and debugger sessions.
if __name__ == '__main__':
	main()
