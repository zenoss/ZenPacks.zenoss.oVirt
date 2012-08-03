######################################################################
#
# Copyright 2012 Zenoss, Inc. All Rights Reserved.
#
######################################################################

from Products.Zuul.catalog.paths import (
    DefaultPathReporter,
    relPath,
    )


class VmDiskPathReporter(DefaultPathReporter):
    def getPaths(self):
        paths = super(VmDiskPathReporter, self).getPaths()
        vm = self.context.vm()
        if vm:
            paths.extend(relPath(vm, 'cluster'))
        return paths


class StorageDomainPathReporter(DefaultPathReporter):
    def getPaths(self):
        paths = super(StorageDomainPathReporter, self).getPaths()
        datacenters = self.context.datacenter()
        for datacenter in datacenters:
            paths.extend(relPath(datacenter, 'system'))
        return paths


class DataCenterPathReporter(DefaultPathReporter):
    def getPaths(self):
        paths = super(DataCenterPathReporter, self).getPaths()
        storagedomains = self.context.storagedomains()
        for storagedomain in storagedomains:
            paths.extend(relPath(storagedomain, 'system'))
        return paths


class HostPathReporter(DefaultPathReporter):
    def getPaths(self):
        paths = super(HostPathReporter, self).getPaths()
        vms = self.context.vms()
        for vm in vms:
            paths.extend(relPath(vm, 'cluster'))
        return paths

class VmPathReporter(DefaultPathReporter):
    def getPaths(self):
        paths = super(VmPathReporter, self).getPaths()
        host = self.context.host()
        if host:
            paths.extend(relPath(host, 'cluster'))
        return paths
