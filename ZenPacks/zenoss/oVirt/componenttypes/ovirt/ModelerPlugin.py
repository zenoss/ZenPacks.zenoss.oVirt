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

from ZenPacks.zenoss.Liberator.GenericModelerPlugin import GenericModelerPlugin
from ZenPacks.zenoss.Liberator.interfaces import IGenericModelerPlugin


class ModelerPlugin(GenericModelerPlugin, PythonPlugin):
    implements(IGenericModelerPlugin)

    def process(self, device, results, log):
        log.debug("Results for %s/%s: %s", self.name(), device.id, results)

        resultXml = results[1]
        try:
            doc = ElementTree.fromstring(resultXml)
        except Exception:
            log.error("Received invalid XML from modeler code -- skipping %s",
                      self.name())
            return None

        relmaps = self.processComponent(doc, self.compdef, log, resultXml)

        log.debug(repr(relmaps))
        return [relmaps]

    def processComponent(self, xmldoc, compdef, log, resultXml):
        def makeId(row):
            # The id field in the resulting XML is a guid
            return compdef.id + "_" + self.prepId(row.attrib['id'])

        rm = self.relMap()
        for virtualElement in xmldoc:
            # Setup the object map
            om = self.objectMap()
            om.id = makeId(virtualElement)
            om.title = virtualElement.find('name').text

            om.meta_type = "GenericComponent_" + compdef.id
            om.component_type = compdef.id

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

