######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

from twisted.spread import pb

from zope.interface import implements

from ZenPacks.zenoss.Liberator.services.LiberatorService import ComponentConfig
from ZenPacks.zenoss.Liberator.interfaces import IGenericServiceConfig


class ServiceConfig(pb.Copyable, pb.RemoteCopy, ComponentConfig):
    implements(IGenericServiceConfig)

    def __init__(self, component):
        ComponentConfig.__init__(self, component)
        self.virtualElement = component.virtualElement

pb.setUnjellyableForClass(ServiceConfig, ServiceConfig)

