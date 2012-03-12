######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

__doc__ = """ovirtloader
Loader for the oVirt ZenPack
"""

import logging
log = logging.getLogger('zen.oVirtLoader')

from zope.interface import implements

from Products.Zuul import getFacade
from Products.ZenModel.interfaces import IDeviceLoader


class OVirtLoader(object):
    implements(IDeviceLoader)
    
    def load_device(self, dmd, id, host, port,
                          username, domain, password,
                          collector='localhost'):
        facade = getFacade('oVirt', dmd)
        facade.addOVirtInfrastructure(id, host, port,
                                      username, domain, password,
                                      collector)

