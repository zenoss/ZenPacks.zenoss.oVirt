######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

__doc__ = """OvirtModelerPlugin
Performs modeling of oVirt compatible systems.
"""

from xml.etree import ElementTree

from zope.interface import implements

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import RelationshipMap

from ZenPacks.zenoss.Liberator.GenericModelerPlugin import GenericModelerPlugin
from ZenPacks.zenoss.Liberator.interfaces import IGenericModelerPlugin


class ModelerPlugin(GenericModelerPlugin, PythonPlugin):
    """
    Note that this modeler plugin does *NOT* receive all of the information
    all at once to go through components.  Subcomponents are retrieved
    after this processing and then are processed separately.
    """
    implements(IGenericModelerPlugin)

    def process(self, device, xmldoc, log):
        log.debug("Processing %s/%s", device.id, self.name())

        relmaps = self.processComponent(xmldoc, self.compdef, log)

        log.debug(repr(relmaps))
        return [relmaps]

    def processComponent(self, xmldoc, compdef, log):
        def makeId(row):
            # The id field in the resulting XML is a guid
            return compdef.id + "_" + self.prepId(row.attrib['id'])

        rm = self.relMap()
        for virtualElement in xmldoc:
            # Setup the object map
            om = self.objectMap()
            om.id = makeId(virtualElement)

            # Some subcomponents don't have the 'name' field
            title = virtualElement.find('name')
            if title is not None:
                om.title = title.text
            else:
                title = virtualElement.find('description')
                om.title = title.text if title is not None else om.id

            om.meta_type = "GenericComponent_" + compdef.id
            om.component_type = compdef.id

            if compdef.parentRelation:
                href = virtualElement.attrib['href']
                parentRow = href.split('/%s' % compdef.parentRelation)[0]
                # Owww.  Yes, we should rename this....
                om.parentSnmpindex = parentRow.split('/')[-1]
                om.modname = "ZenPacks.zenoss.Liberator.GenericSubcomponent"

            # These are the attribute tags defined in the component XML
            om.setAttributes = {}
            for attribute in compdef.attributes:
                query = attribute.get("valueQuery", None)
                value = None
                node = virtualElement
                if query:
                    try:
                        value = eval(query, { 'here':node, } )
                    except Exception:
                        # Note: The REST API may not fill out all fields
                        log.debug("Unable to evaluate XML node for %s with statement: %s", 
                                  attribute['id'], query)
                        continue

                else:
                    attrib = node.get(attribute['id'])
                    if attrib is not None:
                        value = attrib.text
                    else:
                        # Note: The REST API may not fill out all fields
                        log.debug("Unable to find %s element for %s",
                                 attribute['id'], attribute['id'])
                        continue
                om.setAttributes[attribute['id']] = value
            log.info("Found %s: %s", compdef.id,  om.title)
            rm.append(om)
        return rm

    def processSubComponents(self, xmldoc, subcompdef, log):
        def makeId(row):
            # The id field in the resulting XML is a guid
            return self.compdef.id + "_" + self.prepId(row)

        relmaps = {}
        subcomp_relmap = self.processComponent(xmldoc, subcompdef, log)
        for subcomp_objmap in subcomp_relmap:
            parentRow = subcomp_objmap.parentSnmpindex
            subcomp_objmap.compname = "genericComponents/" + makeId(parentRow)
            relmaps.setdefault(subcomp_objmap.compname, RelationshipMap(
                compname=subcomp_objmap.compname,
                relname="subcomponents",
                modname="ZenPacks.zenoss.Liberator.GenericSubcomponent")).append(subcomp_objmap)
        return [relmaps.values()]

