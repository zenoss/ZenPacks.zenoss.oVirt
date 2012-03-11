##########################################################################
#
#   Copyright 2012 Zenoss, Inc. All Rights Reserved.
#
##########################################################################


# You will also need to add an IRRDDataSourceInfo subinterface to control how
# the user interface for configuring this datasource is drawn. This interface
# is typically defined in ../interfaces.py. You will then need to define a
# RRDDataSourceInfo subclass to control how your datasource gets serialized
# for passing through the API. This info adapter class is typically defined in
# ../info.py.

from Products.ZenModel.RRDDataSource import RRDDataSource
from Products.ZenModel.ZenPackPersistence import ZenPackPersistence


class OVirtDataSource(ZenPackPersistence, RRDDataSource):

    ZENPACKID = 'ZenPacks.zenoss.oVirt'

    sourcetypes = ('oVirt',)
    sourcetype = sourcetypes[0]

    eventClass = '/oVirt'
    component = "${here/href}"

