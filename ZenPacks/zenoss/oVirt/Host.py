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


class Host(BaseComponent):
    meta_type = portal_type = "oVirtHost"

    address = None
    status_state = None
    status_detail = None
    statistics_url = None

    _properties = BaseComponent._properties + (
                {'id': 'address', 'type': 'string', 'mode': 'w'},
                {'id': 'status_state', 'type': 'string', 'mode': 'w'},
                {'id': 'status_detail', 'type': 'string', 'mode': 'w'},
                {'id': 'statistics_url', 'type': 'string', 'mode': 'w'},
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
        )

    def device(self):
        return self.cluster().device()
