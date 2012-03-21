##########################################################################
#
#   Copyright 2012 Zenoss, Inc. All Rights Reserved.
#
##########################################################################

from Products.ZenModel.RRDDataSource import RRDDataSource
from Products.ZenModel.ZenPackPersistence import ZenPackPersistence


class OVirtDataSource(ZenPackPersistence, RRDDataSource):

    ZENPACKID = 'ZenPacks.zenoss.oVirt'

    sourcetypes = ('oVirt',)
    sourcetype = sourcetypes[0]

    eventClass = '/oVirt'
    component = "${here/attributes/href}"

    url = "${here/attributes/href}/statistics"

    _properties = RRDDataSource._properties + (
        {'id': 'url', 'type': 'string'},
        )

