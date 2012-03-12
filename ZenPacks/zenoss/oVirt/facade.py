######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################


import logging
log = logging.getLogger('zen.oVirtFacade')

from zope.interface import implements
import transaction

from Products.Zuul.facades import ZuulFacade
from Products.Zuul.utils import ZuulMessageFactory as _t
from Products.ZenModel.Exceptions import DeviceExistsError
from Products.ZenModel.Device import manage_createDevice
from Products.Jobber.jobs import ShellCommandJob

from ZenPacks.zenoss.oVirt.interfaces import IOVirtFacade


class OVirtFacade(ZuulFacade):
    implements(IOVirtFacade)

    def addOVirtEndpoint(self, id, host, port,
                                username, domain, password,
                                collector='localhost'):

        zProps = dict(zOVirtServerName=host,
                      zOVirtPort=port,
                      zOVirtUser=username,
                      zOVirtDomain=domain,
                      zOVirtPassword=password)

        try:
            manage_createDevice(self._dmd, id, devicePath='/oVirt',
                                  performanceMonitor=collector,
                                  zProperties=zProps)
        except DeviceExistsError:
            return False, _t("A device named %s already exists.") % id

        transaction.commit()

        perfConf = self._dmd.Monitors.getPerformanceMonitor(collector)
        cmd = perfConf.getCollectorCommand('zengenericmodeler')
        cmd.extend(
            ['run', '-d', id , '--monitor', collector]
        )
        jobStatus = self._dmd.JobManager.addJob(ShellCommandJob, cmd=cmd)
        return True, jobStatus.id

