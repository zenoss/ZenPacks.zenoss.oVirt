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


class Cluster(BaseComponent):
    meta_type = portal_type = "oVirtCluster"

    #networks
    #permissions
    cpu = None
    memory_overcommit = None
    transparent_hugepages = None
    version_major = None
    version_minor = None
    on_error = None
    description = None

    _properties = BaseComponent._properties + (
        {'id': 'description', 'type': 'string', 'mode': 'w'},
        {'id': 'cpu', 'type': 'string', 'mode': 'w'},
        {'id': 'memory_overcommit', 'type': 'string', 'mode': 'w'},
        {'id': 'transparent_hugepages', 'type': 'string', 'mode': 'w'},
        {'id': 'version_major', 'type': 'string', 'mode': 'w'},
        {'id': 'version_minor', 'type': 'string', 'mode': 'w'},
        {'id': 'on_error', 'type': 'string', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
        ('datacenter', ToOne(ToManyCont,
             'ZenPacks.zenoss.oVirt.DataCenter.DataCenter',
             'clusters')
              ),

        ('hosts', ToManyCont(ToOne,
             'ZenPacks.zenoss.oVirt.Host.Host',
             'cluster')
              ),

        ('vms', ToManyCont(ToOne,
             'ZenPacks.zenoss.oVirt.Vm.Vm',
             'cluster')
              ),

        )

    def device(self):
        return self.datacenter().device()

    def getIconPath(self):
        return '/++resource++ovirt/img/cluster.png'
