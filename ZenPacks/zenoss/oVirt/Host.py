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


class Host(BaseComponent):
    meta_type = portal_type = "oVirtHost"

    address = None
    status_state = None
    status_detail = None
    memory = None
    cpu_sockets = None
    cpu_cores = None
    cpu_name = None
    cpu_speed = None
    storage_manager = None

    _properties = BaseComponent._properties + (
        {'id': 'address', 'type': 'string', 'mode': 'w'},
        {'id': 'status_state', 'type': 'string', 'mode': 'w'},
        {'id': 'status_detail', 'type': 'string', 'mode': 'w'},
        {'id': 'memory', 'type': 'string', 'mode': 'w'},
        {'id': 'cpu_sockets', 'type': 'string', 'mode': 'w'},
        {'id': 'cpu_cores', 'type': 'string', 'mode': 'w'},
        {'id': 'cpu_name', 'type': 'string', 'mode': 'w'},
        {'id': 'cpu_speed', 'type': 'string', 'mode': 'w'},
        {'id': 'storage_manager', 'type': 'string', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
        ('cluster', ToOne(ToManyCont,
             'ZenPacks.zenoss.oVirt.Cluster.Cluster',
             'hosts')
              ),

        ('nics', ToManyCont(ToOne,
             'ZenPacks.zenoss.oVirt.HostNic.HostNic',
             'host')
              ),

        ('vms', ToMany(ToOne,
             'ZenPacks.zenoss.oVirt.Vm.Vm',
             'host')
              ),
        )

    def device(self):
        return self.cluster().device()

    def managed_device(self):
        macAddress = [nic.mac for nic in self.nics()]
        if not macAddress:
            return None

        cat = self.dmd.ZenLinkManager._getCatalog(layer=2)
        if cat is not None:
            for nic in self.nics():
                if not nic.mac:
                    continue

                # Use the first nic on a device, if we modelled the vm
                # this nic should already exist
                brains = cat(macaddress=nic.mac)
                if brains:
                    for brain in brains:
                        device = brain.getObject().device()
                        if device:
                            return device

        return None
