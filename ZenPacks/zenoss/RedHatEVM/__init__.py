######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

import Globals

from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenUtils.Utils import unused

unused(Globals)


class ZenPack(ZenPackBase):

     packZProperties = [
         ('zOVirtServerName', '', 'string'),
         ('zOVirtUser', 'admin', 'string'),
         ('zOVirtPassword', '', 'password'),
         ('zOVirtDomain', 'internal', 'string'),
         ('zOVirtPort', 8080, 'int'),
         #('zOVirtProtocol', 'http', 'string'),
         ]

