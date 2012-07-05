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

from Products.ZenUtils.Ext import DirectRouter, DirectResponse
from Products import Zuul
from Products.ZenModel.ZenossSecurity import ZEN_MANAGE_DMD

# Keeps this backward compatible with Zenoss 3.
try:
    from Products.ZenMessaging.audit import audit
except:
    def audit(*args,**kwargs):
        pass


class oVirtRouter(DirectRouter):
    def _getFacade(self):
        return Zuul.getFacade('oVirt', self.context)

    def add_ovirt(self, url, username, domain, password, collector='localhost'):
        # Check the permissions on the context
        context = self.context.dmd.Devices.oVirt
        if not Zuul.checkPermission(ZEN_MANAGE_DMD, context):
           message = "Insufficient privileges to add an oVirt infrastructure"
           audit('UI.oVirt.Login', url=url)
           return DirectResponse.fail(message)

        facade = self._getFacade()
        success, message = facade.add_ovirt(url, username, domain, password, collector)

        if success:
            audit('UI.oVirt.Add', url=url, username=username, domain=domain,
                  password=password, collector=collector, jobId=message)
            return DirectResponse.succeed(jobId=message)
        else:
            return DirectResponse.fail(message)
