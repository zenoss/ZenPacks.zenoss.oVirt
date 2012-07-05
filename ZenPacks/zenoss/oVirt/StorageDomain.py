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


class StorageDomain(BaseComponent):
    meta_type = portal_type = "oVirtStorageDomain"

    _relations = Device._relations + (
        ('datacenter', ToManyCont(ToOne, 
             'ZenPacks.zenoss.oVirt.DataCenter.DataCenter', 
             'storageDomain')
              ),

        ('storageIso', ToOne(ToManyCont, 
             'ZenPacks.zenoss.oVirt.StorageIso.StorageIso', 
             'storageDomain')
              ),

        ('storageVms', ToOne(ToManyCont, 
             'ZenPacks.zenoss.oVirt.StorageVms.Storagevms', 
             'storageDomain')
              ),
        )

    def device(self):
        return self.datacenter().device()
