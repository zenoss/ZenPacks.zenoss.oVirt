######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

from Products.ZenModel.Device import Device as BaseDevice
from Products.ZenRelations.RelSchema import ToManyCont, ToOne


class Device(BaseDevice):
    meta_type = portal_type = 'Device'
