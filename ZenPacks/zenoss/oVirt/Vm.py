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

from Products.ZenRelations.RelSchema import ToManyCont, ToMany, ToOne
from Products.Zuul.catalog.events import IndexingEvent

from ZenPacks.zenoss.oVirt import BaseComponent
from ZenPacks.zenoss.oVirt.utils import icon_for


class Vm(BaseComponent):
    meta_type = portal_type = "oVirtVm"

    vm_type = None
    state = None
    memory = None
    cpu_cores = None
    cpu_sockets = None
    os_type = None
    os_boot = None
    start_time = None
    creation_time = None
    affinity = None
    memory_policy_guaranteed = None

    _properties = BaseComponent._properties + (
        {'id': 'vm_type', 'type': 'string', 'mode': 'w'},
        {'id': 'state', 'type': 'string', 'mode': 'w'},
        {'id': 'memory', 'type': 'string', 'mode': 'w'},
        {'id': 'cpu_cores', 'type': 'string', 'mode': 'w'},
        {'id': 'cpu_sockets', 'type': 'string', 'mode': 'w'},
        {'id': 'os_type', 'type': 'string', 'mode': 'w'},
        {'id': 'os_boot', 'type': 'string', 'mode': 'w'},
        {'id': 'start_time', 'type': 'string', 'mode': 'w'},
        {'id': 'creation_time', 'type': 'string', 'mode': 'w'},
        {'id': 'affinity', 'type': 'string', 'mode': 'w'},
        {'id': 'memory_policy_guaranteed', 'type': 'string', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
        ('cluster', ToOne(ToManyCont,
             'ZenPacks.zenoss.oVirt.Cluster.Cluster',
             'vms')
              ),

        ('disks', ToMany(ToOne,
             'ZenPacks.zenoss.oVirt.VmDisk.VmDisk',
             'vm')
              ),

        ('host', ToOne(ToMany,
             'ZenPacks.zenoss.oVirt.Host.Host',
             'vms')
              ),

        ('nics', ToManyCont(ToOne,
             'ZenPacks.zenoss.oVirt.VmNic.VmNic',
             'vm')
              ),
        )

    def setHostId(self, id):
        for host in self.cluster().hosts():
            if id == host.id:
                self.host.addRelation(host)
                notify(IndexingEvent(host, 'path', False))
                return

    def getHostId(self):
        host = self.host()
        if host:
            return host.id

    def guest(self):
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

    def device(self):
        return self.cluster().device()

    def getIconPath(self):
        if self.vm_type and 'server' in self.vm_type.lower():
            return icon_for(self.device(), 'virtual-server')
        else:
            return icon_for(self.device(), 'virtual-desktop')
