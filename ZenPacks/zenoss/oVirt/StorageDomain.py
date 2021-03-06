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

from zope.event import notify

from Products.ZenRelations.RelSchema import ToManyCont, ToOne, ToMany
from Products.Zuul.catalog.events import IndexingEvent

from ZenPacks.zenoss.oVirt import BaseComponent
from ZenPacks.zenoss.oVirt.utils import icon_for


class StorageDomain(BaseComponent):
    meta_type = portal_type = "oVirtStorageDomain"

    storagedomain_type = None
    storage_type = None
    storage_format = None
    status = None

    _properties = BaseComponent._properties + (
        {'id': 'storagedomain_type', 'type': 'string', 'mode': 'w'},
        {'id': 'storage_type', 'type': 'string', 'mode': 'w'},
        {'id': 'storage_format', 'type': 'string', 'mode': 'w'},
        {'id': 'status', 'type': 'string', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
       ('system', ToOne(ToManyCont,
             'ZenPacks.zenoss.oVirt.System.System',
             'storagedomains')
              ),

       ('disks', ToManyCont(ToOne,
             'ZenPacks.zenoss.oVirt.VmDisk.VmDisk',
             'storagedomains')
              ),

       ('datacenters', ToMany(ToMany,
             'ZenPacks.zenoss.oVirt.DataCenter.DataCenter',
             'storagedomains')
              ),
        )

    def device(self):
        return self.system()

    def setDatacenterId(self, ids):
        new_ids = set(ids)
        current_ids = set(x.id for x in self.datacenters())

        for id_ in new_ids.symmetric_difference(current_ids):
            datacenter = self.device().datacenters._getOb(id_)
            if datacenter:
                if id_ in new_ids:
                    self.datacenters.addRelation(datacenter)
                else:
                    self.datacenters.removeRelation(datacenter)
                notify(IndexingEvent(datacenter, 'path', False))

    def getDatacenterId(self):
        return sorted([x.id for x in self.datacenters()])

    def getIconPath(self):
        return icon_for(self.device(), 'storage-domain')
