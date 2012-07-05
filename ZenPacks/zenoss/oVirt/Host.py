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


class Host(BaseComponent):
    meta_type = portal_type = "oVirtHost"

    address = None
    status_state = None
    status_storage_detail = None
    port = None
    host_type = None
    storage_manager = None
    storage_manager_priority = None
    power_management_enabled = None
    power_management_port = None
    power_management_secure = None
    ksm = None
    transparent_hugepages = None
    iscsi_initiator = None
    cpu_cores = None
    cpu_sockets = None
    cpu_name = None
    cpu_speed = None
    memory = None
    summary_active = None
    summary_migrating = None
    summary_total = None

    _properties = BaseComponent._properties + (
                {'id': 'description', 'type': 'string', 'mode': 'w'},
    )

    _relations = Device._relations + (
        ('cluster', ToManyCont(ToOne, 
             'ZenPacks.zenoss.oVirt.Cluster.Cluster',
             'host')
              ),
        )

    def device(self):
        return self.cluster().device()
