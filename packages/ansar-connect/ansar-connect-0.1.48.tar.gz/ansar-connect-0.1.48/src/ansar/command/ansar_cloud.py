# Author: Scott Woods <scott.18.ansar@gmail.com.com>
# MIT License
#
# Copyright (c) 2022 Scott Woods
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

"""Utility to maintain the operational folders and files of standard components.

Starts with the process-as-an-async-object abstraction and takes it to
the next level. There is a new abstraction that manages a collection
of one or more processes. A complete runtime environment is provided for
each process, i.e. a place for temporary files and persisted files, and
a per-process configuration. Once configured to satisfy requirements a
process can be started and stopped repeatedly using single commands.
"""
__docformat__ = 'restructuredtext'

import sys
import ansar.connect as ar
from ansar.connect.model import *
from ansar.connect.foh import *

#
#
class SignUpArgs(object):
	def __init__(self, login_email=None, login_secret=None,
			family_name=None, given_name=None, nick_name=None, honorific=None,
			directory_name=None, developer_email=None, device_name=None):
		self.login_email=login_email
		self.login_secret=login_secret
		self.family_name=family_name
		self.given_name=given_name
		self.nick_name=nick_name
		self.honorific=honorific
		self.directory_name = directory_name
		self.developer_email = developer_email
		self.device_name = device_name

SIGN_UP_ARGS_SCHEMA = {
	"login_email": str,
	"login_secret": str,
	"family_name": str,
	"given_name": str,
	"nick_name": str,
	"honorific": str,
	"directory_name": str,
	"developer_email": str,
	"device_name": str,
}

ar.bind(SignUpArgs, object_schema=SIGN_UP_ARGS_SCHEMA)

def sign_up(self, foh, ca, w):
	su = SignUp(login_email=ca.login_email, login_secret=ca.login_secret,
		family_name=ca.family_name, given_name=ca.given_name, nick_name=ca.nick_name, honorific=ca.honorific,
		directory_name=ca.directory_name, developer_email=ca.developer_email, device_name=ca.device_name)
	self.send(su, foh)
	m = self.select(AccountFrame, ar.Faulted, ar.Stop, seconds=3.0)
	if isinstance(m, AccountFrame):
		pass
	elif isinstance(m, ar.Faulted):
		return m
	else:
		return ar.Aborted()

	settings = ar.command_settings()
	if settings is None:
		return ar.Nak()

	settings.login_email = m.account.login_email
	settings.login_secret = m.account.login_secret
	settings.directory_table = m.directory_table
	settings.developer_table = m.developer_table
	settings.device_table = m.device_table

	ar.store_settings(settings)

	return ar.Ack()

#
#
def list_account(self, foh, la, w):
	settings = ar.command_settings()
	if settings is None or settings.login_email is None:
		return ar.Nak()

	dt = settings.directory_table
	vt = settings.developer_table
	et = settings.device_table

	print(f'Login email: {settings.login_email}')

	print(f'Directory ({len(dt)}):')
	for k, v in dt.items():
		print(f'\tDirectory name: {v.directory_name}')
		print(f'\tDirectory id: {v.directory_id}')
		print(f'\tAccount id: {v.account_id}')

	print(f'Developer: ({len(vt)}):')
	for k, v in vt.items():
		print(f'\tDeveloper email: {v.login_email}')
		print(f'\tDeveloper id: {v.login_id}')

	print(f'Device: ({len(et)}):')
	for k, v in et.items():
		print(f'\tDevice name: {v.device_name}')
		print(f'\tDevice id: {v.device_id}')

	return 0

#
#
class DirectoryAccessArgs(object):
	def __init__(self, directory_name=None, directory_id=None):
		self.directory_name = directory_name
		self.directory_id = directory_id

DIRECTORY_ACCESS_ARGS_SCHEMA = {
	"directory_id": ar.UUID,
	"directory_name": str,
}

ar.bind(DirectoryAccessArgs, object_schema=DIRECTORY_ACCESS_ARGS_SCHEMA)

def find(dt, name):
	for k, v in dt.items():
		if v.directory_name == name:
			return v
	return None

def directory_access(self, foh, ca, w):
	settings = ar.command_settings()
	if settings is None or settings.directory_table is None:
		return 0
	dt = settings.directory_table
	if ca.directory_id:
		d = dt.get(ca.directory_id, None)
		if d is None:
			return -1
	elif ca.directory_name:
		d = find(dt, ca.directory_name)
		if d is None:
			return -1
	else:
		return -1
	access = DirectoryAccess(access_ipp=settings.foh_ipp, account_id=d.account_id, directory_id=d.directory_id)

	return access

#
#
class AccountLoginArgs(object):
	def __init__(self, login_email=None, login_secret=None):
		self.login_email=login_email
		self.login_secret=login_secret

ACCOUNT_LOGIN_SCHEMA = {
	"login_email": str,
	"login_secret": str,
}

ar.bind(AccountLoginArgs, object_schema=ACCOUNT_LOGIN_SCHEMA)


def account_login(self, foh, a, w):
	al = AccountLogin(login_email=a.login_email, login_secret=a.login_secret)
	self.send(al, foh)
	m = self.select(CloudAccount, ar.Faulted, ar.Stop)
	if isinstance(m, CloudAccount):
		account = m
	elif isinstance(m, ar.Faulted):
		return m
	else:
		return ar.Aborted()

	m = self.select(AccountInformation, ar.Faulted, ar.Stop)
	if isinstance(m, AccountInformation):
		pass
	elif isinstance(m, ar.Faulted):
		return m
	else:
		return ar.Aborted()

	settings = ar.command_settings()
	settings.directory_table = m.directory_table
	settings.developer_table = m.developer_table
	settings.device_table = m.device_table

	ar.store_settings(settings)

	return ar.Ack()

#
#
class DeviceAccessArgs(object):
	def __init__(self, device_id=None, login_secret=None):
		self.device_id = device_id
		self.login_secret = login_secret

DEVICE_ACCESS_SCHEMA = {
	"device_id": ar.UUID,
	"login_secret": str,
}

ar.bind(DeviceAccessArgs, object_schema=DEVICE_ACCESS_SCHEMA)

#
#
def device_access(self, foh, a, w):
	da = DeviceAccess(device_id=a.device_id, login_secret=a.login_secret)
	self.send(da, foh)
	m = self.select(ar.DirectoryDevice, ar.Faulted, ar.Stop)
	if isinstance(m, ar.DirectoryDevice):
		device = m
	elif isinstance(m, ar.Faulted):
		return m
	else:
		return ar.Aborted()

	m = self.select(ar.AccountDirectory, ar.Faulted, ar.Stop)
	if isinstance(m, ar.AccountDirectory):
		wan = m
	elif isinstance(m, ar.Faulted):
		return m
	else:
		return ar.Aborted()

	m = self.select(ar.DirectoryAccess, ar.Faulted, ar.Stop)
	if isinstance(m, ar.DirectoryAccess):
		access = m
	elif isinstance(m, ar.Faulted):
		return m
	else:
		return ar.Aborted()

	return access

#
#
class DeveloperLoginArgs(object):
	def __init__(self, login_email=None, login_secret=None):
		self.login_email=login_email
		self.login_secret=login_secret

ACCOUNT_LOGIN_SCHEMA = {
	"login_email": str,
	"login_secret": str,
}

ar.bind(DeveloperLoginArgs, object_schema=ACCOUNT_LOGIN_SCHEMA)


def developer_login(self, foh, a, w):
	al = DeveloperLogin(login_email=a.login_email, login_secret=a.login_secret)
	self.send(al, foh)
	m = self.select(CloudAccount, ar.Faulted, ar.Stop)
	if isinstance(m, CloudAccount):
		account = m
	elif isinstance(m, ar.Faulted):
		return m
	else:
		return ar.Aborted()

	m = self.select(AccountInformation, ar.Faulted, ar.Stop)
	if isinstance(m, AccountInformation):
		pass
	elif isinstance(m, ar.Faulted):
		return m
	else:
		return ar.Aborted()
	return m

# Bring all the functions together as a table that
# uses the function name, i.e. f.__name__ as a key.
table = ar.jump_table(
	(sign_up, SignUpArgs()),
	(list_account, None),
	(directory_access, DirectoryAccessArgs()),
	(account_login, AccountLoginArgs()),
	(device_access, DeviceAccessArgs()),
	(developer_login, DeveloperLoginArgs()),
)

def get_host():
    """Retrieve the name of this executable. Return a string."""
    a0 = sys.argv[0]
    bp = ar.breakpath(a0)
    bp1 = bp[1]
    return bp1

def cannot(line, newline=True, **kv):
    """Place an error diagnostic on stderr, including the executable name."""
    if kv:
        t = line.format(**kv)
    else:
        t = line

    h = get_host()
    sys.stderr.write(h)
    sys.stderr.write(': ')
    sys.stderr.write(t)
    if newline:
        sys.stderr.write('\n')

# CLI access to the cloud service.
FOH = 'front-of-house'

def ansar_cloud(self, settings):
	# Break down the command line.
	sub_function, sub_settings, word = ar.command_words()
	if sub_function is None:
		return 0

	# Everything lined up for execution of
	# the selected sub-command.
	code = 0
	name = sub_function.__name__.rstrip('_')
	try:
		# Open communication with the
		# service.
		a = self.create(ar.ConnectService, settings.foh_ipp, FOH)
		self.assign(a, FOH)

		while True:
			m = self.select(ar.ServiceUp, ar.ServiceNotUp, ar.Stop)
			if isinstance(m, ar.ServiceUp):
				break
			elif isinstance(m, ar.ServiceNotUp):
				self.warning(f'no connection to ansar cloud ({m.not_connected.error_text})')
			else:
				return ar.Aborted()

		# Connected to the cloud.
		foh = self.return_address
		code = sub_function(self, foh, sub_settings, word)

	except ValueError as e:
		cannot('cannot perform "{sub}" command, {error}', sub=name, error=str(e))
		code = 1
	except OSError as e:
		cannot('cannot perform "{sub}" command, {error}', sub=name, error=str(e))
		code = 1
	finally:
		# Finished with the cloud. Clean up.
		self.abort()
		while self.working():
			m = self.select(ar.Completed)
			d = self.debrief()

	return code

ar.bind(ansar_cloud)

def word_else(i, w, d):
	if i < len(w):
		return w[i]
	return d

#
#
def sub_parameters(specific_settings):
	if specific_settings is not None:
		a = ar.object_settings.__art__.value.keys()		# Framework values.
		b = specific_settings.__art__.value.keys()	  # Application.
		c = set(a) & set(b)
		if len(c) > 0:
			j = ', '.join(c)
			raise ValueError('collision in settings names - {collisions}'.format(collisions=j))

	executable, ls1, sub, ls2, word = ar.sub_args()
	x1, r1 = ar.extract_args(ar.object_settings, ls1, specific_settings)
	ar.arg_values(ar.object_settings, x1)

	# Support for the concept of a noop pass, just for the
	# framework.
	def no_sub_required(s):
		return s.help or s.dump_settings or s.dump_input

	sub_settings = None
	if sub is not None:
		try:
			sub_function, sub_settings = table[sub]
		except KeyError:
			raise ValueError('unknown sub-command "{sub}"'.format(sub=sub))

		if sub_settings:
			x2, r2 = ar.extract_args(sub_settings, ls2, None)
			ar.arg_values(sub_settings, x2)
		else:
			r2 = ls2
	elif no_sub_required(ar.object_settings):
		# Give framework a chance to complete some
		# admin operation.
		sub_function = None
		r2 = ({}, {})
	else:
		raise ValueError('no-op command')

	bundle = (sub_function,		# The sub-command function.
		sub_settings,			# Remainder from ls2, i.e. for passing to sub-component
		word)					# Non-flag arguments.

	return executable, bundle, r1

# Persistent settings for the command-line tool.
class Settings(object):
	def __init__(self, foh_ipp=None, login_email=None, login_secret=None, directory_table=None, device_table=None, developer_table=None):
		self.foh_ipp = foh_ipp or ar.HostPort()
		self.login_email = login_email
		self.login_secret = login_secret
		self.directory_table = directory_table or ar.default_map()
		self.device_table = device_table or ar.default_map()
		self.developer_table = developer_table or ar.default_map()

SETTINGS_SCHEMA = {
	'foh_ipp': ar.UserDefined(ar.HostPort),
	"login_email": str,
	"login_secret": str,
	"directory_table": ar.MapOf(ar.UUID(),ar.UserDefined(AccountDirectory)),
	"device_table": ar.MapOf(ar.UUID(),ar.UserDefined(DirectoryDevice)),
	"developer_table": ar.MapOf(ar.UUID(),ar.UserDefined(AccountDeveloper)),
}

ar.bind(Settings, object_schema=SETTINGS_SCHEMA)

#
#
compiled_defaults=Settings(foh_ipp=ar.HostPort('192.168.1.26', 5022))

def main():
	ar.create_object(ansar_cloud, factory_settings=compiled_defaults, parameter_passing=sub_parameters)

# The standard entry point. Needed for IDEs
# and debugger sessions.
if __name__ == '__main__':
	main()
