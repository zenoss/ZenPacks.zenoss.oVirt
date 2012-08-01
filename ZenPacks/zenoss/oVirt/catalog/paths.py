######################################################################
#
# Copyright 2012 Zenoss, Inc. All Rights Reserved.
#
######################################################################

from Products.Zuul.catalog.paths import (
    DefaultPathReporter,
    relPath,
    )


class DiskPathReporter(DefaultPathReporter):
    def getPaths(self):
        paths = super(DiskPathReporter, self).getPaths()
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
