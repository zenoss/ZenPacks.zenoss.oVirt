######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

import logging

from zope.interface import implements

from ZenPacks.zenoss.Liberator.GenericComponentManager import (
    GenericComponentDefinition, BadXmlDefinitionFileException,
    GenericComponentAttributeDefinition,
)
from ZenPacks.zenoss.Liberator.interfaces import IGenericComponentDefinition
from ZenPacks.zenoss.oVirt.datasources.OVirtDataSource import OVirtDataSource
from .interfaces import IOVirtGenericComponentInfo
 
log = logging.getLogger("zen.liberator.OVirtComponentDefinition")


class ComponentDefinition(GenericComponentDefinition):
    implements(IGenericComponentDefinition)

    definition_type = "ovirt"
    iinfoClass = IOVirtGenericComponentInfo

    virtualElement = ''

    _properties = GenericComponentDefinition._properties + (
        {'id':'virtualElement', 'type':'string', 'mode':'rw'},
    )

    def parseNode(self, componentNode):
        self.virtualElement = componentNode.get('virtualElement')

        docNode = componentNode.find("documentation")
        if docNode is not None:
            self.documentation = docNode.text
            self.documentationType = docNode.get('type', '')

        for attributeNode in componentNode.findall("attribute"):
            attributeId = attributeNode.get("name")
            if not attributeId:
                raise BadXmlDefinitionFileException("name attribute not defined on attribute element (line %d)" % attributeNode.lineno);
            attribute = self.getOrAdd(self, GenericComponentAttributeDefinition, attributeId)
            attribute._parseNode(attributeNode)

    def addDataPoint(self, template, perfNode):
        perfId = perfNode.get("name")
        if perfId is not None:
            msg = "The name attribute is not defined on perf element (line %d)" % perfNode.lineno
            raise BadXmlDefinitionFileException(msg)

        ds = getattr(template.datasources, perfId, None)
        if ds is None or not isinstance(ds, OVirtDataSource):
            ds = template.manage_addRRDDataSource(perfId, dsOption='OVirtDataSource.oVirt')
        dp = getattr(ds.datapoints, perfId, None)
        if dp is None:
            dp = ds.manage_addRRDDataPoint(id=perfId)
        dp.rrdtype = perfNode.get("rrdType", "GAUGE")

        if not dp.description:
            # NB: This will not be viewable directly in the 3.x UI
            # Look for a 'description' element in the XML first
            desc = perfNode.get("description")
            ds.description = desc
            dp.description = desc

        return dp

    def getTableMaps(self):
        components = [table.getTableMap() for table in self.objectValues("GenericComponentTableDefinition")]
        subcomponents = [subcomp.getTableMaps() for subcomp in self.objectValues("GenericComponentDefinition")]
        # sum(someListOfLists, []) -> flattens list of lists
        return components + sum(subcomponents, [])

    def validate(self, componentNode):
        super(ComponentDefinition, self).validate(componentNode)

