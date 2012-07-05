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


class DataCenter(BaseComponent):
    meta_type = portal_type = "oVirtDataCenter"

    description = None
    storage_type = None
    storage_format = None
    version_major = None
    version_minor = None
    status = None

    _properties = BaseComponent._properties + (
        {'id': 'description', 'type': 'string', 'mode': 'w'},
        {'id': 'storage_type', 'type': 'string', 'mode': 'w'},
        {'id': 'storage_format', 'type': 'string', 'mode': 'w'},
        {'id': 'version_major', 'type': 'string', 'mode': 'w'},
        {'id': 'version_minor', 'type': 'string', 'mode': 'w'},
        {'id': 'status', 'type': 'string', 'mode': 'w'},
    )

    _relations = Device._relations + (
        ('system', ToOne(ToManyCont, 
             'ZenPacks.zenoss.oVirt.System.System', 
             'datacenters')
              ),

        ('cluster', ToManyCont(ToOne, 
             'ZenPacks.zenoss.oVirt.Cluster.Cluster', 
             'datacenter')
              ),

        ('storageDomain', ToManyCont(ToOne, 
             'ZenPacks.zenoss.oVirt.StorageDomain.StorageDomain', 
             'datacenter')
              ),

        )

    def device(self):
        return self.system()