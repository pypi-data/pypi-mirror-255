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

"""Tools and runtime for asynchronous programming.

Repo: git@github.com:mr-ansar/ansar-connect.git
Branch: main
Commit: 4541102fb4dc474cafe7d218b06be0cd13e70717
Version: 0.1.47 (2024-02-10@12:56:38+NZDT)
"""

from ansar.create import *

#bind = bind_any
#create = create_object

from .socketry import HostPort, LocalPort
from .socketry import ScopeOfIP, local_private_public
from .socketry import Blob, CreateFrame
from .socketry import Listening, NotListening, Accepted, NotAccepted, StopListening
from .socketry import Connected, NotConnected
from .socketry import Close, Closed, Abandoned
from .transporting import listen, connect, stop_listen

from .plumbing import RETRY_LOCAL, RETRY_PRIVATE, RETRY_PUBLIC
from .plumbing import ip_retry
from .plumbing import ConnectService, ServiceUp, ServiceDown, ServiceNotUp
from .plumbing import AcceptClient

from .directory import ScopeOfService
from .directory import publish, subscribe
from .directory import clear, retract
from .directory import key_service
from .directory import Published, NotPublished, Subscribed
from .directory import Available, NotAvailable, Delivered, NotDelivered
from .directory import Clear, Cleared, Dropped
from .directory import ServiceDirectory
from .directory import RouteByRelay, InboundByRelay, OpenLoop

from .networking import UseAddress, NoAddress, ConnectToAddress
from .grouping import GroupTable, GroupUpdate, ObjectGroup, GroupTimer

from .node import NodeSettings, node_settings
from .node import node_passing, sub_node_passing
from .node import create_node, NodeProperties

from .tagging import ConnectingFlags, SchedulingTimer, GetReadyTimer
from .tagging import GetConnected, ConnectEngine, ConnectionUpdate

from .model import CONTACT_TYPE, CONTACT_DEVICE
from .model import EmailAddress, PhoneNumber
from .model import Login, PII
from .model import CloudAccount, AccountFrame, DirectoryDevice, AccountDeveloper, AccountOwner
from .model import AccountDirectory, DirectoryFrame, DirectoryAccess
from .model import DirectoryLookup, DirectoryRedirect, DirectoryAssignment, YourDirectory
from .model import RelayLookup, RelayRedirect, RelayAssignment, YourRelay, CloseRelay

from .instant import InstantLookup, YourInstant

from .foh import SignUp, ExportAccount
from .foh import AccountInformation
from .foh import ExportDevice, DeviceAccess
