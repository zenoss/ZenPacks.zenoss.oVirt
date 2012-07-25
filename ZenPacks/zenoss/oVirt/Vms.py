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


class Vms(BaseComponent):
    meta_type = portal_type = "oVirtVms"

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
             'ZenPacks.zenoss.oVirt.Disk.Disk',
             'vm')
              ),

        ('nics', ToManyCont(ToOne,
             'ZenPacks.zenoss.oVirt.VmNic.VmNic',
             'vm')
              ),
        )

    def device(self):
        return self.cluster().device()
