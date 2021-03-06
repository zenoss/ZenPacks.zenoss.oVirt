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

from Products.ZenModel.Device import Device
from Products.ZenRelations.RelSchema import ToManyCont, ToOne

from ZenPacks.zenoss.oVirt.utils import icon_for


class System(Device):
    meta_type = portal_type = "oVirtSystem"

    _relations = Device._relations + (
        ('datacenters', ToManyCont(ToOne, 'ZenPacks.zenoss.oVirt.DataCenter.DataCenter', 'system')),
        ('storagedomains', ToManyCont(ToOne, 'ZenPacks.zenoss.oVirt.StorageDomain.StorageDomain', 'system')),
        )

    def getIconPath(self):
        return icon_for(self, 'system')
