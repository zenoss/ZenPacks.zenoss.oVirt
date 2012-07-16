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


class Disk(BaseComponent):
    meta_type = portal_type = "oVirtVmDisk"

    _relations = BaseComponent._relations + (
        ('storagedomains', ToOne(ToManyCont,
             'ZenPacks.zenoss.oVirt.StorageDomain.StorageDomain',
             'disks')
              ),

        ('vm', ToOne(ToMany,
             'ZenPacks.zenoss.oVirt.Vms.Vms',
             'disks')
              ),
        )

    def device(self):
        return self.storagedomains().device()

    def setVmId(self, vm_id):
        print "Setting vm %s for %s" % (vm_id, self)
        for component in self.device().getDeviceComponents():
            if component.id == vm_id:
                vm = component

        if not vm:
            return

        # Check if the relationship already exists.
        if self.id in vm.disks.objectIds():
            return

        self.vm.addRelation(vm)

        # Do we need to remove this relation?


    def getVmId(self):
        if self.vm():
            return self.vm().id
        else:
            return ''
