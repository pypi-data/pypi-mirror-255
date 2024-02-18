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

""".

.
"""
__docformat__ = 'restructuredtext'

import ansar.connect as ar

__all__ = [
	'Login',
	'PII',
	'CONTACT_TYPE',
	'CONTACT_TYPE',
	'EmailAddress',
	'PhoneNumber',
	'CloudAccount',
	'AccountFrame',
	'AccountDeveloper',
	'AccountOwner',
	'AccountDirectory',
	'DirectoryFrame',
	'DirectoryAccess',
	'DirectoryLookup',
	'DirectoryRedirect',
	'DirectoryAssignment',
	'YourDirectory',
	'RelayLookup',
	'RelayRedirect',
	'RelayAssignment',
	'YourRelay',
	'CloseRelay',
	'DirectoryDevice',
	'DB_SHARED_SCHEMA',
]

# Base types.
# Need for secure access to cloud.
class Login(object):
	def __init__(self, login_id=None, login_email=None, login_secret=None):
		self.login_id = login_id
		self.login_email = login_email
		self.login_secret = login_secret

# Actual person who needs access
class PII(object):
	def __init__(self, family_name=None, given_name=None, nick_name=None, honorific=None):
		self.family_name = family_name
		self.given_name = given_name
		self.nick_name = nick_name
		self.honorific = honorific

CONTACT_TYPE = ar.Enumeration(PERSONAL=0, BUSINESS=1, HOME=2, OTHER=3)
CONTACT_DEVICE = ar.Enumeration(MOBILE=0, FIXED_LINE=1)

# Contact details collected as necessary.
class EmailAddress(object):
	def __init__(self, email_type=None, email_address=None):
		self.email_type = email_type
		self.email_address = email_address

class PhoneNumber(object):
	def __init__(self, phone_type=None, phone_device=None, phone_number=None):
		self.phone_type = phone_type
		self.phone_device = phone_device
		self.phone_number = phone_number

# An account in the cloud.
# Directories, developers and devices hang
# under this object.
class CloudAccount(Login, PII):
	def __init__(self, login_id=None, login_email=None, login_secret=None,
			family_name=None, given_name=None, nick_name=None, honorific=None,
			technical_contact=None, financial_contact=None, administrative_contact=None,
			resource_control=None):
		Login.__init__(self, login_id=login_id, login_email=login_email, login_secret=login_secret)
		PII.__init__(self, family_name=family_name, given_name=given_name, nick_name=nick_name, honorific=honorific)
		self.technical_contact = technical_contact or ar.default_vector()
		self.financial_contact = financial_contact or ar.default_vector()
		self.administrative_contact = administrative_contact or ar.default_vector()
		self.resource_control = resource_control or ar.default_vector()

class AccountFrame(object):
	def __init__(self, account=None,
			directory_table=None, device_table=None, developer_table=None):
		self.account = account or CloudAccount()
		self.directory_table = directory_table or ar.default_map()
		self.device_table = device_table or ar.default_map()
		self.developer_table = developer_table or ar.default_map()

# An account creates and maintains zero or more directories.
class AccountDirectory(object):
	def __init__(self, directory_id=None, account_id=None, directory_name=None, directory_routes=1, message_rate=None, byte_rate=None):
		self.directory_id = directory_id
		self.account_id = account_id
		self.directory_name = directory_name
		self.directory_routes = directory_routes
		self.message_rate = message_rate
		self.byte_rate = byte_rate

class DirectoryFrame(object):
	def __init__(self, directory=None, device_table=None):
		self.directory = directory or AccountDirectory()
		self.device_table = device_table or ar.default_map()

class DirectoryAccess(object):
	def __init__(self, access_ipp=None, account_id=None, directory_id=None):
		self.access_ipp = access_ipp or ar.HostPort()
		self.account_id = account_id
		self.directory_id = directory_id

class DirectoryLookup(object):
	def __init__(self, account_id=None, directory_id=None):
		self.account_id = account_id
		self.directory_id = directory_id

class DirectoryRedirect(object):
	def __init__(self, redirect_ipp=None, directory_id=None, assignment_token=None):
		self.redirect_ipp = redirect_ipp or ar.HostPort()
		self.directory_id = directory_id
		self.assignment_token = assignment_token

class DirectoryAssignment(object):
	def __init__(self, directory_id=None, assignment_token=None):
		self.directory_id = directory_id
		self.assignment_token = assignment_token

class YourDirectory(object):
	def __init__(self, address=None):
		self.address = address

#
#
class RelayLookup(object):
	def __init__(self, relay_id=None, directory_id=None):
		self.relay_id = relay_id
		self.directory_id = directory_id

class RelayRedirect(object):
	def __init__(self, redirect_ipp=None, relay_id=None, assignment_token=None):
		self.redirect_ipp = redirect_ipp or ar.HostPort()
		self.relay_id = relay_id
		self.assignment_token = assignment_token

class RelayAssignment(object):
	def __init__(self, relay_id=None, assignment_token=None):
		self.relay_id = relay_id
		self.assignment_token = assignment_token

class YourRelay(object):
	def __init__(self, address=None):
		self.address = address

class CloseRelay(object):
	def __init__(self, redirect=None):
		self.redirect = redirect or RelayRedirect()

# Services are published and clients subscribe to services
# on a wan.
class DirectoryDevice(Login):
	def __init__(self, device_id=None, directory_id=None, device_name=None):
		self.device_id = device_id
		self.directory_id = directory_id
		self.device_name = device_name

# Developers control and monitor wans for
# an account.
class AccountDeveloper(Login, PII):
	def __init__(self, login_id=None, login_email=None, login_secret=None,
			family_name=None, given_name=None, nick_name=None, honorific=None,
			account_id=None):
		Login.__init__(self, login_id=login_id, login_email=login_email, login_secret=login_secret)
		PII.__init__(self, family_name=family_name, given_name=given_name, nick_name=nick_name, honorific=honorific)
		self.account_id = account_id

# Devops access to manage the cloud service.
class AccountOwner(Login, PII):
	def __init__(self, login_id=None, login_email=None, login_secret=None,
			family_name=None, given_name=None, nick_name=None, honorific=None):
		Login.__init__(self, login_id=login_id, login_email=login_email, login_secret=login_secret)
		PII.__init__(self, family_name=family_name, given_name=given_name, nick_name=nick_name, honorific=honorific)

DB_SHARED_SCHEMA = {
	"login_id": ar.UUID,
	"login_email": str,
	"login_name": str,
	"login_secret": str,
	"family_name": str,
	"given_name": str,
	"nick_name": str,
	"honorific": str,
	"email_type": CONTACT_TYPE,
	"email_address": str,
	"phone_type": CONTACT_TYPE,
	"phone_device": CONTACT_DEVICE,
	"phone_number": str,
	"technical_contact": ar.VectorOf(ar.Any()),
	"financial_contact": ar.VectorOf(ar.Any()),
	"administrative_contact": ar.VectorOf(ar.Any()),
	"resource_control": ar.VectorOf(ar.Any()),
	"directory_id": ar.UUID,
	"account_id": ar.UUID,
	"directory_name": str,
	"directory_routes": int,
	"message_rate": int,
	"byte_rate": int,
	"device_id": ar.UUID,
	"device_name": str,
	"relay_id": ar.UUID,
	"connect_token": ar.UUID,
	"message_count": int,
	"expiry_date": ar.WorldTime,
	"access_ipp": ar.UserDefined(ar.HostPort),
	"redirect_ipp": ar.UserDefined(ar.HostPort),
	"assignment_token": ar.UUID,
	"address": ar.Address,
	"relay_id": ar.UUID,
	#"redirect": ar.UserDefined(RelayRedirect),
}

TABLE_SCHEMA = {
	"directory_table": ar.MapOf(ar.UUID,ar.UserDefined(AccountDirectory)),
	"device_table": ar.MapOf(ar.UUID,ar.UserDefined(DirectoryDevice)),
	"developer_table": ar.MapOf(ar.UUID,ar.UserDefined(AccountDeveloper)),
}

ar.bind(EmailAddress, object_schema=DB_SHARED_SCHEMA)
ar.bind(PhoneNumber, object_schema=DB_SHARED_SCHEMA)
ar.bind(CloudAccount, object_schema=DB_SHARED_SCHEMA)
ar.bind(AccountDirectory, object_schema=DB_SHARED_SCHEMA)
ar.bind(DirectoryAccess, object_schema=DB_SHARED_SCHEMA)
ar.bind(DirectoryLookup, object_schema=DB_SHARED_SCHEMA)
ar.bind(DirectoryAssignment, object_schema=DB_SHARED_SCHEMA)
ar.bind(YourDirectory, object_schema=DB_SHARED_SCHEMA)
ar.bind(DirectoryDevice, object_schema=DB_SHARED_SCHEMA)
ar.bind(DirectoryRedirect, object_schema=DB_SHARED_SCHEMA)
ar.bind(RelayLookup, object_schema=DB_SHARED_SCHEMA)
ar.bind(RelayRedirect, object_schema=DB_SHARED_SCHEMA)
ar.bind(RelayAssignment, object_schema=DB_SHARED_SCHEMA)
ar.bind(YourRelay, object_schema=DB_SHARED_SCHEMA)
ar.bind(AccountDeveloper, object_schema=DB_SHARED_SCHEMA)
ar.bind(AccountOwner, object_schema=DB_SHARED_SCHEMA)

CLOSE_RELAY_SCHEMA = {
	"redirect": ar.UserDefined(RelayRedirect),
}

ar.bind(CloseRelay, object_schema=CLOSE_RELAY_SCHEMA)

SCHEMA = {}
SCHEMA.update(DB_SHARED_SCHEMA)
SCHEMA.update(TABLE_SCHEMA)
ar.bind(AccountFrame, object_schema=SCHEMA)
ar.bind(DirectoryFrame, object_schema=SCHEMA)

#
#
class DeviceRead(object):
	def __init__(self, device_id=None):
		self.device_id = device_id

API_SCHEMA = {
	"device_id": ar.UUID,
}

ar.bind(DeviceRead, object_schema=API_SCHEMA)
