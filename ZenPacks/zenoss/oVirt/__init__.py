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
from Products.ZenUtils.Utils import unused

#Used by the BaseComponent Class
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE

unused(Globals)

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

    # Query for events by id instead of name.
    event_key = "ComponentId"

    def getIconPath(self):
        return '/++resource++ovirt/img/ovirt.png'


class ZenPack(ZenPackBase):
    packZProperties = [
        ('zOVirtUrl', '', 'string'),
        ('zOVirtUser', 'admin', 'string'),
        ('zOVirtPassword', '', 'password'),
        ('zOVirtDomain', 'internal', 'string'),
    ]

    # Placeholder for future plugin installation
    _plugins = ()

    def install(self, app):
        super(ZenPack, self).install(app)
        self.symlink_plugins()

    def remove(self, app, leaveObjects=False):
        if not leaveObjects:
            self.remove_plugin_symlinks()

        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)

    def symlink_plugins(self):
        libexec = os.path.join(os.environ.get('ZENHOME'), 'libexec')
        if not os.path.isdir(libexec):
            # Stack installs might not have a $ZENHOME/libexec directory.
            os.mkdir(libexec)

        for plugin in self._plugins:
            LOG.info('Linking %s plugin into $ZENHOME/libexec/', plugin)
            plugin_path = zenPath('libexec', plugin)
            os.system('ln -sf "%s" "%s"' % (self.path(plugin), plugin_path))
            os.system('chmod 0755 %s' % plugin_path)

    def remove_plugin_symlinks(self):
        for plugin in self._plugins:
            LOG.info('Removing %s link from $ZENHOME/libexec/', plugin)
            os.system('rm -f "%s"' % zenPath('libexec', plugin))

