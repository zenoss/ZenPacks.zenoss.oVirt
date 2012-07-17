######################################################################
#
# Copyright 2012 Zenoss, Inc. All Rights Reserved.
#
######################################################################

from Products.Zuul.catalog.paths import (
    DefaultPathReporter,
    InterfacePathReporter as BaseInterfacePathReporter,
    relPath,
    )

#class StorageDomainPathReporter(BaseInterfacePathReporter):
#    def getPaths(self):
#        paths = super(InterfacePathReporter, self).getPaths()
#
#        datacenter = self.context.datacenter()
#        if datacenter:
#            paths.extend(relPath(datacenter, 'system'))
