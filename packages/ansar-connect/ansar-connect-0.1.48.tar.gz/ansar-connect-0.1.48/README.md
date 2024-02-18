# ansar-connect

The **ansar-connect** library implements sophisticated asynchronous network messaging. It builds
on the features of the `ansar-encode <https://pypi.org/project/ansar-encode>`_
and `ansar-create <https://pypi.org/project/ansar-create>`_ libraries to integrate network
messaging into the asynchronous model of execution. The result of this approach is that sending
a message across a network is no different to sending a message between any two async objects.
There is also complete "portability" of messages - an application data object read from the disk
using **ansar.encode** can immediately be sent across a network, with zero additional effort.

This essential messaging capability is combined with the multi-process capabilities
of **ansar.create**, to deliver practical, distributed computing. Designs for software
solutions can now consider;

* multi-process compositions that run on a host,
* compositions of processes distributed across a LAN,
* and compositions where processes may be anywhere on the Internet.

Smaller projects will use this library to deliver multi-process solutions on a single host.
The library will arrange for all the network messaging that binds the processes together,
into a single operational unit.

The most ambitious projects will involve processes spread across the Internet, e.g. between
desktop PCs at different branches of an organization, or between head-office servers and mobile
personnel on laptops, or between those same servers and SBCs operating as weather stations. As
long as there is a reasonably up-to-date Python runtime (>=3.10) and Internet connectivity, this
library will arrange for full, asynchronous messaging between any 2 members of a composition.

## Features

- Implements full-duplex, network messaging over asynchronous sockets.
- Inherits the complete type-sophistication of **ansar.encode**.
- Seamlessly extends the async model of operation to span local and wide-area networks.
