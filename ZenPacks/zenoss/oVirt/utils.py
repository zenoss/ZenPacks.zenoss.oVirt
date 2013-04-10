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


def add_local_lib_path():
    """Helper to add the ZenPack's lib directory to PYTHONPATH."""
    import os
    import site

    site.addsitedir(os.path.join(os.path.dirname(__file__), 'lib'))

add_local_lib_path()
import txovirt

def icon_for(device, icon):
    """Return the icon path for device and icon.

    This allows RHEV icons to be used when the oVirt system is a RHEV product
    and oVirt icons to be used when it isn't.

    """

    icon_template = '/++resource++ovirt/img/%%s-%s.png' % icon

    if 'oVirt' in device.os.getProductName():
        return icon_template % 'ovirt'

    return icon_template % 'rhev'

def createClient(config):
    '''return a client object based on the passed in parameters'''
    ds0 = config.datasources[0]
    client = txovirt.Client(
        ds0.zOVirtUrl,
        ds0.zOVirtUser,
        ds0.zOVirtDomain,
        ds0.zOVirtPassword)
    return client

def eventKey(config):
    '''Given a config, return an appropriate eventKey.'''
    ds0 = config.datasources[0]
    return '%s|%s' % (ds0.plugin_classname, ds0.cycletime)
