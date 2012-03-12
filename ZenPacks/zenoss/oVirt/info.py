######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

from zope.interface import implements

from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.template import RRDDataSourceInfo

from ZenPacks.zenoss.oVirt.interfaces import IOVirtDataSourceInfo


class OVirtDataSourceInfo(RRDDataSourceInfo):
    implements(IOVirtDataSourceInfo)

    url = ProxyProperty('url')

    @property
    def testable(self):
        # FIXME: This datasource is not testable.
        return False

