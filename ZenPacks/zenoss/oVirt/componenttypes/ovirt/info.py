######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

import logging
log = logging.getLogger("zen.GenericComponentInfo")

from Products.Zuul.infos import ProxyProperty


class OVirtGenericComponentInfo(object):

    def __init__(self, obj):
        super(OVirtGenericComponentInfo, self).__init__()
        self._object = obj

