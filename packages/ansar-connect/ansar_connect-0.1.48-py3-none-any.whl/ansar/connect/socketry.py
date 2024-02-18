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

import queue as sq
import threading as thr
import errno
import socket
import select
import re
import ansar.create as ar

from copy import copy

__all__ = [
	'HostPort',
	'LocalPort',
	'ScopeOfIP',
	'local_private_public',
	'Blob',
	'CreateFrame',
	'ListenForStream',
	'ConnectStream',
	'StopListening',
	'Listening',
	'Accepted',
	'Connected',
	'NotListening',
	'NotAccepted',
	'NotConnected',
	'Close',
	'Closed',
	'Abandoned',
	'SocketSelect',
	'SocketChannel',
]

#
#
LOCAL_HOST = '127.0.0.1'

class HostPort(object):
	def __init__(self, host=None, port=None):
		self.host = host
		self.port = port
	
	def __str__(self):
		return f'{self.host}:{self.port}'

	def inet(self):
		return (self.host, self.port)

class LocalPort(HostPort):
	def __init__(self, port=None):
		HostPort.__init__(self, LOCAL_HOST, port)

HOST_PORT_SCHEMA = {
	'host': str,
	'port': int,
}

ar.bind(HostPort, object_schema=HOST_PORT_SCHEMA)
ar.bind(LocalPort, object_schema=HOST_PORT_SCHEMA)

#
#
DOTTED_IP = re.compile(r'(\d+)\.(\d+)\.(\d+)\.(\d+)')
ScopeOfIP = ar.Enumeration(OTHER=0, LOCAL=1, PRIVATE=2, PUBLIC=3)

def local_private_public(ip):
	m = DOTTED_IP.match(ip)
	if m is None:
		return ScopeOfIP.OTHER
	# Have complete verification of dotted layout
	b0 = int(m.groups()[0])
	b1 = int(m.groups()[1])

	# Not dotted -------- None
	# 127.x.x.x --------- 0, localhost
	# 10.x.x.x ---------- 1, private
	# 192.168.x.x ------- 1, private
	# 172.[16-31].x.x --- 1, private
	# else -------------- 2, public

	if b0 == 127:
		return ScopeOfIP.LOCAL
	elif b0 == 10:
		return ScopeOfIP.PRIVATE
	elif b0 == 192 and b1 == 168:
		return ScopeOfIP.PRIVATE
	elif b0 == 172 and (b1 > 15 and b1 < 32):
		return ScopeOfIP.PRIVATE
	return ScopeOfIP.PUBLIC

#
#
class Blob(object):
    def __init__(self, block=None):
        self.block = block

ar.bind(Blob, object_schema={'block': ar.Block()})

#
#
class CreateFrame(object):
	def __init__(self, object_type, *args, **kw):
		self.object_type = object_type
		self.args = args
		self.kw = kw

# Control messages sent to the sockets thread
# via the control channel.
class ListenForStream(object):
	def __init__(self, requested_ipp=None, create_session=None, tag=None, upgrade=None):
		self.requested_ipp = requested_ipp or HostPort()
		self.create_session = create_session
		self.tag = tag
		self.upgrade = upgrade

class ConnectStream(object):
	def __init__(self, requested_ipp=None, create_session=None, tag=None, upgrade=None):
		self.requested_ipp = requested_ipp or HostPort()
		self.create_session = create_session
		self.tag = tag
		self.upgrade = upgrade

class StopListening(object):
	def __init__(self, listening_ipp=None):
		self.listening_ipp = listening_ipp or HostPort()

# Update messages from sockets thread to app.
class Listening(object):
	def __init__(self, requested_ipp=None, listening_ipp=None, tag=None):
		self.requested_ipp = requested_ipp or HostPort()
		self.listening_ipp = listening_ipp or HostPort()
		self.tag = tag

class Accepted(object):
	def __init__(self, listening_ipp=None, accepted_ipp=None, remote_address=None, opened_at=None, tag=None):
		self.listening_ipp = listening_ipp or HostPort()
		self.accepted_ipp = accepted_ipp or HostPort()
		self.remote_address = remote_address
		self.opened_at = opened_at
		self.tag = tag

class Connected(object):
	def __init__(self, requested_ipp=None, connected_ipp=None, remote_address=None, opened_at=None, tag=None):
		self.requested_ipp = requested_ipp or HostPort()
		self.connected_ipp = connected_ipp or HostPort()
		self.remote_address = remote_address
		self.opened_at = opened_at
		self.tag = tag

class NotListening(ar.Faulted):
	def __init__(self, requested_ipp=None, error_code=0, error_text=None, tag=None):
		cannot = f'cannot listen at "{requested_ipp}"'
		reason = error_text
		ar.Faulted.__init__(self, cannot, reason, exit_code=error_code)
		self.requested_ipp = requested_ipp or HostPort()
		self.error_code = error_code
		self.error_text = error_text
		self.tag = tag

class NotAccepted(ar.Faulted):
	def __init__(self, listening_ipp=None, error_code=0, error_text=None, tag=None):
		cannot = f'cannot accept at "{listening_ipp}"'
		reason = error_text
		ar.Faulted.__init__(self, cannot, reason, exit_code=error_code)
		self.listening_ipp = listening_ipp or HostPort()
		self.error_code = error_code
		self.error_text = error_text
		self.tag = tag

class NotConnected(ar.Faulted):
	def __init__(self, requested_ipp=None, error_code=0, error_text=None, tag=None):
		cannot = f'cannot connect to "{requested_ipp}"'
		reason = error_text
		ar.Faulted.__init__(self, cannot, reason, exit_code=error_code)
		#self.condition = cannot
		#self.explanation = reason
		#self.exit_code = error_code
		self.requested_ipp = requested_ipp or HostPort()
		self.error_code = error_code
		self.error_text = error_text
		self.tag = tag

CONTROL_SCHEMA = {
	'requested_ipp': ar.UserDefined(HostPort),
	'controller_address': ar.Address(),
	'remote_address': ar.Address(),
	'tag': str,
	'opened_at': ar.WorldTime(),
	'upgrade': ar.Type(),
	'create_session': ar.Type(),
	'connected_ipp': ar.UserDefined(HostPort),
	'listening_ipp': ar.UserDefined(HostPort),
	'accepted_ipp': ar.UserDefined(HostPort),
	'error_code': ar.Integer4,
	'error_text': str,
}

ar.bind(ListenForStream, object_schema=CONTROL_SCHEMA)
ar.bind(ConnectStream, object_schema=CONTROL_SCHEMA)
ar.bind(StopListening, object_schema=CONTROL_SCHEMA)
ar.bind(Listening, object_schema=CONTROL_SCHEMA)
ar.bind(Accepted, object_schema=CONTROL_SCHEMA)
ar.bind(Connected, object_schema=CONTROL_SCHEMA)
ar.bind(NotListening, object_schema=CONTROL_SCHEMA)
ar.bind(NotAccepted, object_schema=CONTROL_SCHEMA)
ar.bind(NotConnected, object_schema=CONTROL_SCHEMA)

# Session termination messages. Handshake between app
# and sockets thread to cleanly terminate a connection.
class Close(object):
	def __init__(self, value=None):
		self.value = value

class Closed(object):
	def __init__(self, value=None, opened_at=None, closed_at=None, tag=None):
		self.value = value
		self.opened_at = opened_at
		self.closed_at = closed_at
		self.tag = tag

class Abandoned(object):
	def __init__(self, opened_at=None, closed_at=None, tag=None):
		self.opened_at = opened_at
		self.closed_at = closed_at
		self.tag = tag

ENDING_SCHEMA = {
	'value': ar.Any,
	'tag': str,
	'opened_at': ar.WorldTime(),
	'closed_at': ar.WorldTime(),
}

ar.bind(Close, object_schema=ENDING_SCHEMA, copy_before_sending=False)
ar.bind(Closed, object_schema=ENDING_SCHEMA, copy_before_sending=False)
ar.bind(Abandoned, object_schema=ENDING_SCHEMA, copy_before_sending=False)

class Shutdown(object):
	def __init__(self, s=None, value=False):
		self.s = s
		self.value = value

class Bump(object):
	def __init__(self, s=None):
		self.s = s

QUEUE_SCHEMA = {
	's': ar.Any,
	'value': ar.Any,
	'stream': ar.Any,
}

ar.bind(Shutdown, object_schema=QUEUE_SCHEMA, copy_before_sending=False)
ar.bind(Bump, object_schema=QUEUE_SCHEMA, copy_before_sending=False)

# Classes representing open sockets for one reason or another;
# - ControlChannel.... accepted end of backdoor into sockets loop.
# - TcpServer ........ an active listen
# - TcpClient ........ an active connect
# - TcpStream ........ established transport, child of listen or connect

class ControlChannel(object):
	def __init__(self, s):
		self.s = s

class TcpServer(object):
	def __init__(self, s, request, listening, controller_address, upgrade):
		self.s = s
		self.request = request
		self.listening = listening
		self.controller_address = controller_address
		self.upgrade = upgrade

class TcpClient(object):
	def __init__(self, s, request, connected, controller_address, upgrade):
		self.s = s
		self.request = request
		self.connected = connected
		self.controller_address = controller_address
		self.upgrade = upgrade

# Underlying network constraints.
#
TCP_RECV = 1024
TCP_SEND = 1024
UDP_RECV = 4096
UDP_SEND = 4096

# Security/reliability behaviours.
#
NUMBER_OF_DIGITS = 7
GIANT_FRAME = 1048576

#
#
class Header(object):
	def __init__(self, to_address=None, return_address=None, tunnel=False):
		self.to_address = to_address
		self.return_address = return_address
		self.tunnel = tunnel

HEADING_SCHEMA = {
	"to_address": ar.TargetAddress(),
	"return_address": ar.Address(),
	"tunnel": ar.Boolean(),
}

ar.bind(Header, object_schema=HEADING_SCHEMA)

HEADING = ar.UserDefined(Header)
SPACE = ar.VectorOf(ar.Address())

#
#
class Relay(object):
	def __init__(self, block=None, space=None):
		self.block = block
		self.space = space

RELAY_SCHEMA = {
	"block": ar.Block(),
	"space": ar.VectorOf(ar.Address()),
}

ar.bind(Relay, object_schema=RELAY_SCHEMA)

class StreamingIn(object):
	def __init__(self):
		self.analysis_state = 1
		self.size_digits = bytearray()
		self.jump_size = 0
		self.byte_header = bytearray()
		self.byte_body = bytearray()
		self.byte_space = bytearray()
		self.byte_part = self.byte_header

		def s1(c):
			if c in b'0123456789':
				nd = len(self.size_digits)
				if nd < NUMBER_OF_DIGITS:
					self.size_digits += c
					return 1
				raise OverflowError(f'unlikely frame size with {nd} digits')
			elif c == b'\n':
				d = self.size_digits.decode('utf-8')
				self.jump_size = int(d)
				if self.jump_size > GIANT_FRAME:
					raise OverflowError(f'oversize frame of {self.jump_size} bytes')
				elif self.jump_size == 0:
					return 3
				return 2
			d = c.decode('utf8')
			raise ValueError(f'frame with unexpected byte {d} in digits')

		def s2(c):
			self.byte_part += c
			self.jump_size -= 1
			if self.jump_size == 0:
				return 3
			return 2

		def s3(c):
			if c == b'\n':
				return 0
			d = c.decode('utf8')
			raise ValueError(f'unexpected byte {d} at end-of-frame')

		self.shift = {
			1: s1,
			2: s2,
			3: s3,
		}

	def header_body(self, received):
		r = len(received)
		for i in range(r):
			c = received[i:i+1]
			next = self.shift[self.analysis_state](c)
			if next:
				self.analysis_state = next
				continue
			if self.byte_part is self.byte_header:
				self.analysis_state = 1
				self.size_digits.clear()
				self.jump_size = 0
				self.byte_part = self.byte_body
				continue
			if self.byte_part is self.byte_body:
				self.analysis_state = 1
				self.size_digits.clear()
				self.jump_size = 0
				self.byte_part = self.byte_space
				continue
			yield self.byte_header, self.byte_body, self.byte_space
			self.analysis_state = 1
			self.size_digits.clear()
			self.jump_size = 0
			# Ownership passed with yield. Make new
			# ones.
			self.byte_header = bytearray()
			self.byte_body = bytearray()
			self.byte_space = bytearray()
			self.byte_part = self.byte_header

class StreamingOut(object):
	def __init__(self):
		self.pending = []		   # Messages not yet in the loop.
		self.lock = thr.RLock()	 # Safe sharing and empty detection.
		self.messages_to_encode = ar.deque()

	def put(self, m, t, r):
		try:
			self.lock.acquire()
			empty = len(self.pending) == 0
			t3 = (m, t, r)
			self.pending.append(t3)
		finally:
			self.lock.release()
		return empty

	def drain(self, a):
		try:
			self.lock.acquire()
			count = len(self.pending)
			a.extend(self.pending)
			self.pending = []
		finally:
			self.lock.release()
		return count

	def best_block(self, encoded_bytes, codec):
		while len(encoded_bytes) < TCP_SEND:
			if len(self.messages_to_encode) == 0:
				added = self.drain(self.messages_to_encode)
				if added == 0:
					break
			m, t, r = self.messages_to_encode.popleft()
			f = isinstance(m, Blob)
			h = Header(t, r, f)
			e = codec.encode(h, HEADING)
			e = e.encode('utf-8')
			n = len(e)
			encoded_bytes += str(n).encode('ascii')
			encoded_bytes += b'\n'
			encoded_bytes += e
			encoded_bytes += b'\n'
			if f:
				e = m.block
				n = len(e)
				encoded_bytes += str(n).encode('ascii')
				encoded_bytes += b'\n'
				encoded_bytes += e
				encoded_bytes += b'\n'
				# Tunnel block contains no addresses
				# Could just assign '[]' (an empty JSON list)
				s = codec.encode([], SPACE)
			elif isinstance(m, Relay):
				e = m.block
				n = len(e)
				encoded_bytes += str(n).encode('ascii')
				encoded_bytes += b'\n'
				encoded_bytes += e
				encoded_bytes += b'\n'
				s = codec.encode(m.space, SPACE)
			else:
				space = []
				e = codec.encode(m, ar.Any(), space=space)
				e = e.encode('utf-8')
				n = len(e)
				encoded_bytes += str(n).encode('ascii')
				encoded_bytes += b'\n'
				encoded_bytes += e
				encoded_bytes += b'\n'
				s = codec.encode(space, SPACE)
			s = s.encode('utf-8')
			n = len(s)
			encoded_bytes += str(n).encode('ascii')
			encoded_bytes += b'\n'
			encoded_bytes += s
			encoded_bytes += b'\n'
		return len(encoded_bytes)

class TcpStream(StreamingIn, StreamingOut):
	def __init__(self, parent, controller_address, upgrade, opened_at, tag):
		StreamingIn.__init__(self)
		StreamingOut.__init__(self)
		self.parent = parent
		self.controller_address = controller_address
		self.remote_address = None
		self.upgrade = upgrade
		self.opened_at = opened_at
		self.tag = tag
		self.closing = False
		self.value = None
		self.codec = None
		self.encoded_bytes = bytearray()

	def routing(self, return_proxy, local_termination, remote_address):
		# Define addresses for message forwarding.
		# return_proxy ........ address that response should go back to.
		# local_termination ... address of default target, actor or session.
		# remote_address ...... source address of connection updates, session or proxy.
		self.codec = ar.CodecJson(return_proxy=return_proxy, local_termination=local_termination)
		self.remote_address = remote_address

	def receive_and_route(self, received, sockets):
		for h, b_, a in self.header_body(received):
			s = h.decode('utf-8')
			header, v = self.codec.decode(s, HEADING)
			if v is not None:
				raise ValueError(f'header with unexpected versioning "{v}"')
			s = a.decode('utf-8')
			space, v = self.codec.decode(s, SPACE)

			if header.tunnel:
				sockets.forward(Blob(b_), header.to_address, header.return_address)
				continue
			elif len(header.to_address) > 1:
				sockets.forward(Relay(b_, space), header.to_address, header.return_address)
				continue

			s = b_.decode('utf-8')
			body, v = self.codec.decode(s, ar.Any(), space=space)
			if v is not None:
				if not self.upgrade:
					raise ValueError(f'body version "{v}" and no upgrade')
				body = self.upgrade(body, v)
			sockets.forward(body, header.to_address, header.return_address)

	def send_a_block(self, s):
		t = self.best_block(self.encoded_bytes, self.codec)
		if t == 0:
			return False
		n = t if t <= TCP_SEND else TCP_SEND
		chunk = self.encoded_bytes[:n]
		n = s.send(chunk)
		if n:
			self.encoded_bytes = self.encoded_bytes[n:]
			return True
		return False

#
#
class INITIAL: pass
class NORMAL: pass

class SocketProxy(ar.Point, ar.StateMachine):
	def __init__(self, s, channel, stream):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.s = s
		self.channel = channel
		self.stream = stream

SOCKET_DOWN = (errno.ECONNRESET, errno.EHOSTDOWN, errno.ENETDOWN, errno.ENETRESET)

def SocketProxy_INITIAL_Start(self, message):
	return NORMAL

def SocketProxy_NORMAL_Unknown(self, message):
	empty = self.stream.put(message, self.to_address, self.return_address)
	if empty:
		self.channel.send(Bump(self.s), self.address)
	return NORMAL

def SocketProxy_NORMAL_Close(self, message):
	self.channel.send(Shutdown(self.s, message.value), self.address)
	self.complete()

def SocketProxy_NORMAL_Stop(self, message):
	self.complete()

TCP_PROXY_DISPATCH = {
	INITIAL: (
		(ar.Start,),
		()
	),
	NORMAL: (
		(ar.Unknown, Close, ar.Stop),
		()
	),
}

ar.bind(SocketProxy, TCP_PROXY_DISPATCH)

# Signals from the network represented
# as distinct classes - for dispatching.
class ReceiveBlock: pass
class ReadyToSend: pass
class BrokenTransport: pass

# CONTROL CHANNEL
# First two functions are for handling the 1-byte events
# coming across the control socket.
def ControlChannel_ReceiveBlock(self, control, s):
	s.recv(1)					   # Consume the bump.
	mr = self.pending.get()	# Message and account.

	# This second jump is to simulate the common handling of control
	# channel events and select events.
	c = type(mr[0])
	try:
		f = select_table[(ControlChannel, c)]
	except KeyError:
		self.fault('Unknown signal received at control channel (%s).' % (c.__name__,))
		return
	f(self, control, mr)

def ControlChannel_BrokenTransport(self, control, s):
	self.fault('The control channel to the selector is broken.')
	self.clear(s, ControlChannel)

# The rest of them handle the simulated receive of the
# actual message.
def ControlChannel_ListenForStream(self, control, mr):
	m, r = mr
	requested_ipp = m.requested_ipp
	try:
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error as e:
		self.send(NotListening(requested_ipp, e.errno, str(e), m.tag), r)
		return

	def server_not_listening(e):
		server.close()
		self.send(NotListening(requested_ipp, e.errno, str(e), m.tag), r)

	try:
		server.setblocking(False)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server.bind(requested_ipp.inet())
		server.listen(5)
	except socket.herror as e:
		server_not_listening(e)
		return
	except socket.gaierror as e:
		server_not_listening(e)
		return
	except socket.error as e:
		server_not_listening(e)
		return
	except OverflowError as e:
		server.close()
		self.send(NotListening(requested_ipp, 0, str(e), m.tag), r)
		return

	hap = server.getsockname()

	self.trace('Listening on "%s"(%d), requested "%s"(%d)' %
		(hap[0], hap[1],
		requested_ipp.host, requested_ipp.port))

	listening = Listening(requested_ipp, HostPort(hap[0], hap[1]), m.tag)

	self.networking[server] = TcpServer(server, m, listening, r, m.upgrade)
	self.receiving.append(server)
	self.faulting.append(server)

	self.send(listening, r)

def no_ending(value, parent, address):
	pass

def close_ending(proxy):
	def ending(value, parent, address):
		ar.send_a_message(Close(value), proxy, address)
	return ending

def open_stream(self, parent, s, opened_at):
	controller_address = parent.controller_address

	stream = TcpStream(parent, controller_address, parent.upgrade, opened_at, parent.request.tag)
	proxy_address = self.create(SocketProxy, s, self.channel, stream, object_ending=no_ending)

	cs = parent.request.create_session
	if cs:
		# Create the ending function that swaps the Completed message to the parent for a
		# Close message to the proxy.

		ending = close_ending(proxy_address)
		session_address = self.create(cs.object_type, *cs.args,
			controller_address=controller_address, remote_address=proxy_address,
			object_ending=ending,
			**cs.kw)
		stream.routing(proxy_address, session_address, session_address)
	else:
		stream.routing(proxy_address, controller_address, proxy_address)

	self.networking[s] = stream
	return stream, proxy_address

def ControlChannel_ConnectStream(self, control, mr):
	m, r = mr
	requested_ipp = m.requested_ipp
	try:
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client.setblocking(False)
	except socket.error as e:
		self.send(NotConnected(requested_ipp, e.errno, str(e), m.tag), r)
		return

	def client_not_connected(e):
		client.close()
		self.send(NotConnected(requested_ipp, e.errno, str(e), m.tag), r)

	try:
		e = client.connect_ex(requested_ipp.inet())
		if e:
			# Connect request cannot complete. Check for codes indicating
			# async issue. If not it's a real error.
			if e not in (errno.EINPROGRESS, errno.EWOULDBLOCK, errno.EAGAIN):
				client.close()
				self.send(NotConnected(requested_ipp, e, 'Connect incomplete and no pending indication.', m.tag), r)
				return

			# Build a transient "session" that just exists to catch
			# an initial, either send or fault (a receive is treated
			# as an error). True session is constructed on receiving
			# a "normal" send event.
			pending = TcpClient(client, m, None, r, m.upgrade)

			self.networking[client] = pending
			self.receiving.append(client)
			self.sending.append(client)
			self.faulting.append(client)
			return

	except socket.herror as e:
		client_not_connected(e)
		return
	except socket.gaierror as e:
		client_not_connected(e)
		return
	except socket.error as e:
		client_not_connected(e)
		return
	except OverflowError as e:
		client.close()
		self.send(NotConnected(requested_ipp, 0, str(e), m.tag), r)
		return

	hap = client.getsockname()

	self.trace('Connected to "%s"(%d), at local address "%s"(%d)' %
					(requested_ipp.host, requested_ipp.port,
					hap[0], hap[1]))

	connected = Connected(requested_ipp=m.requested_ipp,
		connected_ipp=HostPort(hap[0], hap[1]),
		opened_at=ar.world_now(),
		tag=m.tag)

	parent = TcpClient(client, m, connected, r, m.upgrade)
	stream, proxy_address = open_stream(self, parent, client, connected.opened_at)
	connected.remote_address = proxy_address

	self.networking[client] = stream
	self.receiving.append(client)
	self.sending.append(client)
	self.faulting.append(client)

	self.forward(connected, r, stream.remote_address)

def ControlChannel_StopListening(self, control, mr):
	m, r = mr
	listening_ipp = m.listening_ipp
	def server(t):
		if not isinstance(t, TcpServer):
			return False
		h = t.listening.listening_ipp.host == listening_ipp.host
		p = t.listening.listening_ipp.port == listening_ipp.port
		return h and p

	# Find server belonging to sender
	# and clear from engine.
	sockets = [k for k, v in self.networking.items() if server(v)]
	if len(sockets) == 1:
		self.clear(sockets[0], TcpServer)
		text = 'stopped "%s"(%d)' % (listening_ipp.host, listening_ipp.port)
	else:
		text = 'not listening to "%s"(%d)' % (listening_ipp.host, listening_ipp.port)
	self.send(NotListening(listening_ipp, 0, text), r)

def ControlChannel_Stop(self, control, mr):
	m, r = mr
	def soc(p): # Server or client.
		return isinstance(p, (TcpServer, TcpClient))

	# Clear any servers and clients. Not
	# accepting or connecting any more.
	sockets = [k for k, v in self.networking.items() if soc(v)]
	for s in sockets:
		self.clear(s)

	# Only streams left. Except control channel. Sigh.
	# Kick off a proper teardown and wait until the handshaking
	# is done and there is nothing left to do.
	for k, v in self.networking.items():
		if isinstance(v, TcpStream):
			self.send(Close(), v.remote_address)

	self.running = False

def ControlChannel_Bump(self, control, mr):
	m, r = mr
	if m.s.fileno() < 0:
		# Catches the situation where the socket has been abandoned
		# by the remote and the notification to the proxy arrives behind
		# the bump.
		return
	try:
		self.sending.index(m.s)
		return
	except ValueError:
		pass
	self.sending.append(m.s)

def ControlChannel_Shutdown(self, control, mr):
	m, r = mr
	try:
		stream = self.networking[m.s]
	except KeyError:
		# Already cleared by Abandoned codepath.
		return
	stream.closing = True
	stream.value = m.value
	m.s.shutdown(socket.SHUT_RD)

# Dispatch of socket signals;
# - ReceiveBlock ...... there are bytes to recv
# - ReadyToSend ....... an opportunity to send
# - BrokenTransport ... error on socket
# and server/client/connection;
# - TcpServer ......... listen waiting to accept
# - TcpClient ......... partial connect
# - TcpStream ......... established connection

def TcpServer_ReceiveBlock(self, server, s):
	listening = server.listening
	try:
		accepted, hap = s.accept()
		accepted.setblocking(False)
	except socket.error as e:
		self.send(NotAccepted(listening.requested_ipp, e.errno, str(e), listening.tag), server.controller_address)
		return

	self.trace( 'Accepted "%s"(%d), server at "%s"(%d)' %
				   (hap[0], hap[1],
				   listening.listening_ipp.host, listening.listening_ipp.port))

	opened_at = ar.world_now()
	stream, proxy_address = open_stream(self, server, accepted, opened_at)
	self.receiving.append(accepted)
	self.sending.append(accepted)
	self.faulting.append(accepted)

	accepted = Accepted(listening_ipp=listening.listening_ipp,
		accepted_ipp=HostPort(hap[0], hap[1]),
		remote_address=stream.remote_address,
		opened_at=opened_at,
		tag=listening.tag)

	self.forward(accepted, server.controller_address, stream.remote_address)

def TcpServer_BrokenTransport(self, server, s):
	listening = server.listening
	self.send(NotListening(listening.listening_ipp, 0, "signaled by networking subsystem"), server.controller_address)
	self.clear(s, TcpServer)

# TCP CLIENT
# A placeholder for the eventual outbound stream.
def TcpClient_ReceiveBlock(self, selector, s):
	client = s
	# NOT NEEDED IN TcpStream_ReceiveBlock SO....
	#self.sending.remove(client)

	request = selector.request
	hap = client.getsockname()
	# CANNOT BUILD A STREAM AND IMMEDIATELY TEAR IT DOWN ON AN EXCEPTION.
	# THIS WILL MAY CREATE A SESSION OBJECT WHEN THERE IS NO REMOTE AND MAY
	# NEVER BE. DO IT AFTER A SUCCESSFUL RECV().
	#connected = Connected(requested_ipp=request.requested_ipp,
	#	connected_ipp=HostPort(hap[0], hap[1]),
	#	opened_at=ar.world_now(),
	#	tag=request.tag)
	#selector.connected = connected

	#stream, proxy_address = open_stream(self, selector, client, connected.opened_at)
	#connected.remote_address = proxy_address

	try:
		scrap = s.recv(TCP_RECV)

		# No exception. New stream.
		connected = Connected(requested_ipp=request.requested_ipp,
			connected_ipp=HostPort(hap[0], hap[1]),
			opened_at=ar.world_now(),
			tag=request.tag)

		selector.connected = connected
		stream, proxy_address = open_stream(self, selector, client, connected.opened_at)
		connected.remote_address = proxy_address

		self.trace( 'Connected to "%s"(%d), at local address "%s"(%d)' %
					   (request.requested_ipp.host, request.requested_ipp.port,
					   hap[0], hap[1]))

		self.forward(connected, stream.controller_address, stream.remote_address)

		if not scrap:
			# Immediate shutdown. Need to
			# generate the full set of messages.
			#self.clear(s, TcpStream)
			return

		try:
			stream.receive_and_route(scrap, self)
		except (ar.CodecFailed, OverflowError, ValueError) as e:
			value = ar.Faulted(condition='cannot start inbound', explanation=str(e))
			close_session(stream, value, s)
		return

	except socket.error as e:
		self.send(NotConnected(request.requested_ipp, e.errno, str(e), request.tag), selector.controller_address)
		self.clear(s, TcpClient)
		#self.send(NotConnected(request.requested_ipp, e.errno, str(e), request.tag), stream.controller_address)
		#self.send(ar.Stop(), stream.remote_address)
		#self.clear(s, TcpStream)
		return

def TcpClient_ReadyToSend(self, selector, s):
	client = s
	#self.sending.remove(client)

	request = selector.request
	hap = client.getsockname()
	connected = Connected(requested_ipp=request.requested_ipp,
		connected_ipp=HostPort(hap[0], hap[1]),
		opened_at=ar.world_now(),
		tag=request.tag)
	selector.connected = connected

	self.trace( 'Connected to "%s"(%d), at local address "%s"(%d)' %
				   (request.requested_ipp.host, request.requested_ipp.port,
				   hap[0], hap[1]))

	stream, proxy_address = open_stream(self, selector, client, connected.opened_at)
	connected.remote_address = proxy_address
	#receiving.append( client)
	#self.faulting.append( client)

	self.forward(connected, stream.controller_address, stream.remote_address)

def TcpClient_BrokenTransport(self, selector, s):
	text = 'fault on pending connect, unreachable, no service at that address or blocked'
	self.send(NotConnected(selector.requested_ipp, 0, text, selector.tag), selector.controller_address)
	self.clear(s, TcpClient)

def close_session(stream, value, s):
	stream.closing = True
	stream.value = value
	s.shutdown(socket.SHUT_RDWR)

def end_of_session(self, stream, s):
	if stream.closing:
		c = Closed(value=stream.value,
			opened_at=stream.opened_at,
			closed_at=ar.world_now(),
			tag=stream.tag)
		self.forward(c, stream.controller_address, stream.remote_address)
	else:
		self.send(ar.Stop(), stream.remote_address)
		a = Abandoned(opened_at=stream.opened_at,
			closed_at=ar.world_now(),
			tag=stream.tag)
		self.forward(a, stream.controller_address, stream.remote_address)
	self.clear(s, TcpStream)

def TcpStream_ReadyToSend(self, stream, s):
	try:
		if stream.send_a_block(s):
			return
	except (ar.CodecFailed, OverflowError, ValueError) as e:
		value = ar.Faulted(condition='cannot stream outbound', explanation=str(e))
		self.warning(str(value))
		close_session(stream, value, s)
		return
	try:
		self.sending.remove(s)
	except KeyError:
		pass

# A network transport for the purpose of exchanging
# messages between machines.

def TcpStream_ReceiveBlock(self, stream, s):
	try:
		scrap = s.recv(TCP_RECV)
		if not scrap:
			end_of_session(self, stream, s)
			return

		try:
			stream.receive_and_route(scrap, self)
		except (ar.CodecFailed, OverflowError, ValueError) as e:
			value = ar.Faulted(condition='cannot stream inbound', explanation=str(e))
			self.warning(str(value))
			close_session(stream, value, s)
		return

	except socket.error as e:
		if e.errno == errno.ECONNREFUSED:
			self.fault('Unexpected connection refused')
		elif e.errno not in SOCKET_DOWN:
			self.fault('Unexpected socket termination [%d] %s' % (e.errno, e.strerror))
		end_of_session(self, stream, s)
		return

def TcpStream_BrokenTransport(self, selector, s):
	end_of_session(self, selector, s)

#
#
def control_channel():
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setblocking(False)
	server.bind(("127.0.0.1", 0))
	server.listen(1)

	server_address = server.getsockname()

	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.setblocking(False)
	e = client.connect_ex(server_address)

	readable, writable, exceptional = select.select([server], [], [server])
	if not readable:
		client.close()
		server.close()
		raise RuntimeError('Forming control channel, select has not received connect notification.')

	accepted, client_address = server.accept()
	accepted.setblocking(False)

	accept_address = accepted.getsockname()

	return server, accepted, client

def control_close(lac):
	# Close the listen and the connect. Accepted
	# will be closed by SocketSelect.
	lac[2].close()
	lac[0].close()

#
#
BUMP = b'X'

class SocketChannel(object):
	def __init__(self, pending=None, client=None):
		'''
		This is the per-object client end of the control
		channel into the network I/O loop.
		'''
		self.pending = pending
		self.client = client

	def send(self, message, address):
		self.pending.put((message, address))
		buffered = self.client.send(BUMP)
		if buffered != 1:
			raise RuntimeError('Control channel not accepting commands.')

# Damn. Sent from sockets thread to creator. They
# need it to inject messages into loop.
SOCKET_CHANNEL_SCHEMA = {
	'pending': ar.Any,
	'client': ar.Any,
}

ar.bind(SocketChannel, object_schema=SOCKET_CHANNEL_SCHEMA, copy_before_sending=False)

#
#
select_table = {
	# Handling of inbound control messages.
	(ControlChannel, ReceiveBlock):	 ControlChannel_ReceiveBlock,		# Signals down the control channel.
	(ControlChannel, BrokenTransport):  ControlChannel_BrokenTransport,

	# Made to look as if the select thread can actually receive
	# sockets signals and application messages. Called from above.
	(ControlChannel, ListenForStream):  ControlChannel_ListenForStream,		# Process signals to sockets.
	(ControlChannel, ConnectStream):	ControlChannel_ConnectStream,
	(ControlChannel, Shutdown):		 ControlChannel_Shutdown,
	(ControlChannel, Bump):			 ControlChannel_Bump,
	(ControlChannel, StopListening):	ControlChannel_StopListening,
	(ControlChannel, ar.Stop):		  ControlChannel_Stop,

	# Operational sockets
	(TcpServer,	ReceiveBlock):	   TcpServer_ReceiveBlock,			# Accept inbound connections.
	(TcpServer,	BrokenTransport):	TcpServer_BrokenTransport,

	(TcpClient,   ReceiveBlock):		TcpClient_ReceiveBlock,			# Deferred connections.
	(TcpClient,   ReadyToSend):		 TcpClient_ReadyToSend,
	(TcpClient,   BrokenTransport):	 TcpClient_BrokenTransport,

	(TcpStream,   ReceiveBlock):		TcpStream_ReceiveBlock,
	(TcpStream,   ReadyToSend):		 TcpStream_ReadyToSend,
	(TcpStream,   BrokenTransport):	 TcpStream_BrokenTransport,
}

class SocketSelect(ar.Threaded, ar.Stateless):
	def __init__(self):
		ar.Threaded.__init__(self)
		ar.Stateless.__init__(self)

		# Construct the control channel and access object.
		self.pending = sq.Queue()
		self.lac = control_channel()
		self.channel = SocketChannel(self.pending, self.lac[2])

		# Load control details into socket tables.
		self.listening = self.lac[0]
		self.accepted = self.lac[1]
		self.networking = {
			self.accepted: ControlChannel(self.accepted),	# Receives 1-byte BUMPs.
		}

		# Active socket lists for select.
		self.receiving = [self.accepted]
		self.sending = []
		self.faulting = self.receiving + self.sending

		# Live.
		self.running = True

	def clear(self, s, expected=None):
		# Remove the specified socket from operations.
		try:
			t = self.networking[s]
		except KeyError:
			self.warning('Attempt to remove unknown socket')
			return None

		if expected and not isinstance(t, expected):
			self.warning('Unexpected networking object "%s" (expecting "%s")' % (t.__class__.__name__, expected.__name__))
			return None

		del self.networking[s]
		try:
			self.receiving.remove(s)
		except ValueError:
			pass
		try:
			self.sending.remove(s)
		except ValueError:
			pass
		try:
			self.faulting.remove(s)
		except ValueError:
			pass
		s.close()
		return t

def SocketSelect_Start(self, message):
	# Provide channel details to parent for access
	# by application.
	self.send(self.channel, self.parent_address)

	def clean_sockets():
		self.receiving = [s for s in self.receiving if s.fileno() > -1]
		self.sending = [s for s in self.receiving if s.fileno() > -1]
		self.faulting = [s for s in self.receiving if s.fileno() > -1]

	while self.running or len(self.networking) > 1:
		R, S, F = select.select(self.receiving, self.sending, self.faulting)

		# IF FAILS
		# for every socket in every list --- select([sock],[],[],0)
		# to find which one has failed.

		for r in R:
			try:
				a = self.networking[r]
				c = a.__class__
				j = select_table[(c, ReceiveBlock)]
			except KeyError:
				continue
			except ValueError:
				#clean_sockets()
				continue
			j(self, a, r)

		for s in S:
			try:
				a = self.networking[s]
				c = a.__class__
				j = select_table[(c, ReadyToSend)]
			except KeyError:
				continue
			except ValueError:
				#clean_sockets()
				continue
			j(self, a, s)

		for f in F:
			try:
				a = self.networking[f]
				c = a.__class__
				j = select_table[(c, BrokenTransport)]
			except KeyError:
				continue
			except ValueError:
				#clean_sockets()
				continue
			j(self, a, f)

	control_close(self.lac)
	self.complete()

ar.bind(SocketSelect, (ar.Start,))
