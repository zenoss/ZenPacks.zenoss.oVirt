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

import logging
LOG = logging.getLogger('zen.oVirt')

import os

import Globals

from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenUtils.Utils import zenPath, unused

#Used by the BaseComponent Class
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE

from Products.ZenRelations.zPropertyCategory import setzPropertyCategory

unused(Globals)


# Used by zenchkschema to validate consistency of relationships.
productNames = (
    'System',
    'DataCenter',
    'StorageDomain',
    'Cluster',
    'Host',
    'HostNic',
    'Vm',
    'VmNic',
    'VmDisk',
    )


# Add categories to our contributed zProperties.
setzPropertyCategory('zOVirtUrl', 'oVirt')
setzPropertyCategory('zOVirtUser', 'oVirt')
setzPropertyCategory('zOVirtPassword', 'oVirt')
setzPropertyCategory('zOVirtDomain', 'oVirt')


class BaseComponent(DeviceComponent, ManagedEntity):
    """
    Abstract base class to avoid repeating boilerplate code in all of the
    DeviceComponent subclasses in this zenpack.
    """

    # Disambiguate multi-inheritence.
    _relations = ManagedEntity._relations

    # This makes the "Templates" component display available.
    factory_type_information = ({
        'actions': ({
            'id': 'perfConf',
            'name': 'Template',
            'action': 'objTemplates',
            'permissions': (ZEN_CHANGE_DEVICE,),
            },),
        },)

    # Query for events by id instead of name. (Zenoss 3 compatibility)
    event_key = "ComponentId"


class ZenPack(ZenPackBase):
    packZProperties = [
        ('zOVirtUrl', '', 'string'),
        ('zOVirtUser', 'admin', 'string'),
        ('zOVirtPassword', '', 'password'),
        ('zOVirtDomain', 'internal', 'string'),
    ]
