###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2012, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

from Products.ZenRelations.RelSchema import ToManyCont, ToOne

from ZenPacks.zenoss.oVirt import BaseComponent


class HostNic(BaseComponent):
    meta_type = portal_type = "oVirtHostNic"

    mac = None
    ip = None
    netmask = None
    gateway = None
    status = None
    speed = None

    _properties = BaseComponent._properties + (
        {'id': 'ip', 'type': 'string', 'mode': 'w'},
        {'id': 'netmask', 'type': 'string', 'mode': 'w'},
        {'id': 'gateway', 'type': 'string', 'mode': 'w'},
        {'id': 'status', 'type': 'string', 'mode': 'w'},
        {'id': 'mac', 'type': 'string', 'mode': 'w'},
        {'id': 'speed', 'type': 'string', 'mode': 'w'},
    )

    _relations = BaseComponent._relations + (
        ('host', ToOne(ToManyCont,
             'ZenPacks.zenoss.oVirt.Host.Host',
             'nics')
              ),
        )

    def device(self):
        return self.host().device()
