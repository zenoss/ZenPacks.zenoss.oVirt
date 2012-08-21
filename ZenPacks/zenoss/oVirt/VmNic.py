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

from Products.ZenRelations.RelSchema import ToManyCont, ToMany, ToOne

from ZenPacks.zenoss.oVirt import BaseComponent
from Products.Zuul.catalog.events import IndexingEvent
from zope.event import notify


class VmNic(BaseComponent):
    meta_type = portal_type = "oVirtVmNic"

    interface = None
    mac = None

    _properties = BaseComponent._properties + (
        {'id': 'interface', 'type': 'string', 'mode': 'w'},
        {'id': 'mac', 'type': 'string', 'mode': 'w'},
    )

    _relations = BaseComponent._relations + (
        ('vm', ToOne(ToManyCont,
             'ZenPacks.zenoss.oVirt.Vm.Vm',
             'nics')
              ),
        )

    def device(self):
        return self.vm().device()

    def getIconPath(self):
        return '/++resource++ovirt/img/network.png'
