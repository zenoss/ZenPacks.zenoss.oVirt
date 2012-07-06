###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2012 Zenoss Inc.
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

from twisted.internet.defer import DeferredList

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap

from ZenPacks.zenoss.oVirt.utils import add_local_lib_path
add_local_lib_path()

import txovirt


class oVirt(PythonPlugin):
    deviceProperties = PythonPlugin.deviceProperties + (
        'zOVirtUrl',
        'zOVirtUser',
        'zOVirtPassword'
        'zOVirtDomain',
    )

    def _combine(self, results):
        """Combines all responses within results into a single data structure"""
        all_data = {}
        for success, result in results:
            if not success:
                LOG.error("API Error: %s", result.getErrorMessage())
                return None
            #all_data.update(result)
        return all_data

    def collect(self,device,unused):
        """Collect model-related information using the txovirt library."""

        if not device.zOVirtUrl:
            LOG.error('zOVirtUrl is not set. Not discovering')
            return None
        
        if not device.zOVirtUser:
            LOG.error('zOVirtUser is not set. Not discovering')
            return None
        
        if not device.zOVirtDomain:
            LOG.error('zOVirtDomain is not set. Not discovering')
            return None
        
        if not device.zOVirtPassword:
            LOG.error('zOVirtPassord is not set. Not discovering')
            return None

        client = txovirt.Client(
             device.zOVirtUrl,
             device.zOVirtUser,
             device.zOVirtDomain,
             device.zOVirtPassword)
        
        d = DeferredList((
             client.request('clusters'),
           ), consumeErrors=False).addCallback(self._combine)
       
    def process(self, device, results, unused):
        maps = []

        response_types = (
            'datacenters', 'clusters'
        )
        print "ffffff..f.ff.f.f..f.ff.f.f..f.ff"

        


