######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

from Products import Zuul
from Products.ZenUtils.Ext import DirectRouter, DirectResponse
from Products.ZenMessaging.audit import audit
from Products.ZenModel.ZenossSecurity import ZEN_MANAGE_DMD


class OVirtRouter(DirectRouter):

    def _getFacade(self):
        return Zuul.getFacade('ovirt', self.context)

    def addOVirtEndpoint(self, id, host, port,
                               username, domain, password,
                               collector='localhost'):
        # check permission on the context
        context = self.context.dmd.Devices.oVirt
        if not Zuul.checkPermission(ZEN_MANAGE_DMD, context):
            message = "Insufficient privileges to add an oVirt infrastructure"
            audit('UI.oVirt.Login', id=id)
            return DirectResponse.fail(message)

        facade = self._getFacade()
        success, message = facade.addOVirtEndpoint(id, host, port,username,
                                        domain, password, collector)
        if success:
            audit('UI.oVirt.Add', id=id, host=host, port=port,
                  username=username, domain=domain, collector=collector, jobId=message)
            return DirectResponse.succeed(jobId=message)
        else:
            return DirectResponse.fail(message)

