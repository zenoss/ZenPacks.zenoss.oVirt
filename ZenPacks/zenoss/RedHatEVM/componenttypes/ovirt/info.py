######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

import logging
log = logging.getLogger("zen.GenericComponentInfo")

from Products.Zuul.infos import ProxyProperty


class OvirtGenericComponentInfo(object):

    def __init__(self, obj):
        super(OvirtGenericComponentInfo, self).__init__()
        self._object = obj

