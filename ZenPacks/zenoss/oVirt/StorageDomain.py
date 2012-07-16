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

from Products.ZenRelations.RelSchema import ToManyCont, ToOne, ToMany
from ZenPacks.zenoss.oVirt import BaseComponent


class StorageDomain(BaseComponent):
    meta_type = portal_type = "oVirtStorageDomain"

    storage_type = None

    _properties = BaseComponent._properties + (
        {'id': 'storage_type', 'type': 'string', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
        ('system', ToOne(ToManyCont,
             'ZenPacks.zenoss.oVirt.System.System',
             'storagedomains')
              ),

       ('disks', ToManyCont(ToOne,
             'ZenPacks.zenoss.oVirt.Disk.Disk',
             'storagedomains')
              ),

        ('datacenter', ToOne(ToMany,
             'ZenPacks.zenoss.oVirt.DataCenter.DataCenter',
             'storagedomains')
              ),

        )

    def device(self):
        return self.system().device()

    def setDatacenterId(self, datacenter_id):
        print "Setting datacenter %s for %s" % (datacenter_id, self)
        datacenter = self.system().datacenters._getOb(datacenter_id, None)
        if not datacenter:
            return

        # Check if the relationship already exists.
        if self.id in datacenter.storagedomains.objectIds():
            return

        self.datacenter.addRelation(datacenter)

        # We assume we cannot move a storage domain from one datacenter to another.
        # Since we assume that we are making a simplification by not removing the relation.

    def getDatacenterId(self):
        if self.datacenter():
            return self.datacenter().id
        else:
            return ''
