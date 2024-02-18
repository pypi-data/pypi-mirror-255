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
'''.

.
'''

import ansar.connect as ar

# Create an account.
class SignUp(object):
	def __init__(self, login_email=None, login_secret=None,
			family_name=None, given_name=None, nick_name=None, honorific=None,
			directory_name=None, developer_email=None, device_name=None):
		self.login_email = login_email
		self.login_secret = login_secret
		self.family_name = family_name
		self.given_name = given_name
		self.nick_name = nick_name
		self.honorific = honorific
		self.directory_name = directory_name
		self.developer_email = developer_email
		self.device_name = device_name

#
class ExportAccount(object):
	def __init__(self, login_id=None, login_email=None, login_secret=None):
		self.login_id = login_id
		self.login_email = login_email
		self.login_secret = login_secret

#
class AccountInformation(object):
	def __init__(self, account=None, directory_table=None, device_table=None, developer_table=None):
		self.account = account or ar.CloudAccount()
		self.directory_table = directory_table or ar.default_map()
		self.device_table = device_table or ar.default_map()
		self.developer_table = developer_table or ar.default_map()

#
class ExportDevice(object):
	def __init__(self, device_id=None):
		self.device_id = device_id

#
class DeviceAccess(object):
	def __init__(self, device_id=None, login_secret=None):
		self.device_id = device_id
		self.login_secret = login_secret

SHARED_SCHEMA = {
	"account": ar.UserDefined(ar.CloudAccount),
	"directory_table": ar.MapOf(ar.UUID,ar.UserDefined(ar.AccountDirectory)),
	"device_table": ar.MapOf(ar.UUID,ar.UserDefined(ar.DirectoryDevice)),
	"developer_table": ar.MapOf(ar.UUID,ar.UserDefined(ar.AccountDeveloper)),
	"directory_name": str,
	"developer_email": str,
	"device_name": str,
	"login_id": ar.UUID,
	"login_email": str,
	"login_secret": str,
	"family_name": str,
	"given_name": str,
	"nick_name": str,
	"honorific": str,
	"device_id": ar.UUID,
	"developer_id": ar.UUID,
	"connect_token": str,
	"technical_contact": ar.VectorOf(ar.Any()),
	"financial_contact": ar.VectorOf(ar.Any()),
	"administrative_contact": ar.VectorOf(ar.Any()),
	"directory": ar.UserDefined(ar.AccountDirectory),
	"operational_ipp": ar.UserDefined(ar.HostPort),
	"directory_id": ar.UUID,
	"access_token": ar.UUID,
	"resource_id": int,
}

ar.bind(SignUp, object_schema=SHARED_SCHEMA)
ar.bind(ExportAccount, object_schema=SHARED_SCHEMA)
ar.bind(AccountInformation, object_schema=SHARED_SCHEMA)
ar.bind(ExportDevice, object_schema=SHARED_SCHEMA)
ar.bind(DeviceAccess, object_schema=SHARED_SCHEMA)
