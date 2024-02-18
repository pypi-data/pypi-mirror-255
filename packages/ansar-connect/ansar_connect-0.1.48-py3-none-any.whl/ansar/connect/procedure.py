# Author: Scott Woods <scott.18.ansar@gmail.com.com>
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
	'BlankSettings',
	'procedure_blank',
]

import sys
import os
import stat
import signal
import errno
import datetime
import calendar
import tempfile
import uuid
import re
import ansar.create as ar

# Per-command arguments as required.
# e.g. command-line parameters specific to create.
class BlankSettings(object):
	def __init__(self,
			home_path=None,
			redirect_bin=None,
			redirect_lock=None,
			redirect_settings=None,
			redirect_logs=None,
			redirect_resource=None,
			redirect_tmp=None,
			redirect_model=None
			):
		self.home_path = home_path
		self.redirect_bin = redirect_bin
		self.redirect_lock = redirect_lock
		self.redirect_settings = redirect_settings
		self.redirect_logs = redirect_logs
		self.redirect_resource = redirect_resource
		self.redirect_tmp = redirect_tmp
		self.redirect_model = redirect_model

BLANK_SETTINGS_SCHEMA = {
	'home_path': ar.Unicode(),
	'redirect_bin': ar.Unicode(),
	'redirect_lock': ar.Unicode(),
	'redirect_settings': ar.Unicode(),
	'redirect_logs': ar.Unicode(),
	'redirect_resource': ar.Unicode(),
	'redirect_tmp': ar.Unicode(),
	'redirect_model': ar.Unicode(),
}

ar.bind(BlankSettings, object_schema=BLANK_SETTINGS_SCHEMA)

#
#
def procedure_blank(self, blank):
	return None
