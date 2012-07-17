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
        datacenter = self.context.datacenter()
        if datacenter:
            paths.extend(relPath(datacenter, 'system'))
        return paths
