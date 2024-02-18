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

__all__ = [
	'connect',
	'listen',
	'stop_listen',
]

sockets = None
channel = None

def create_sockets(root):
	global sockets, channel
	sockets = root.create(SocketSelect)
	channel = root.select(SocketChannel)

def stop_sockets(root):
	global sockets, channel
	channel.send(ar.Stop(), root.address)
	root.select(ar.Completed)

ar.AddOn(create_sockets, stop_sockets)

#
#
def connect(self, requested_ipp, session=None, tag=None):
	global sockets, channel
	channel.send(ConnectStream(requested_ipp, session, tag), self.address)

#
#
def listen(self, requested_ipp, session=None, tag=None):
	global sockets, channel
	channel.send(ListenForStream(requested_ipp, session, tag), self.address)

#
#
def stop_listen(self, requested_ipp):
	global sockets, channel
	channel.send(StopListening(requested_ipp), self.address)
