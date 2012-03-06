######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

__doc__ = """OvirtModelerPlugin
Performs modeling of oVirt compatible systems.
"""

from string import Template
from xml.etree import ElementTree

from zope.interface import implements

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin

from ZenPacks.zenoss.Liberator.GenericModelerPlugin import GenericModelerPlugin
from ZenPacks.zenoss.Liberator.interfaces import IGenericModelerPlugin
from ZenPacks.zenoss.Liberator.TableHelper import TableSet


class ModelerPlugin(GenericModelerPlugin, PythonPlugin):
    implements(IGenericModelerPlugin)

    def process(self, device, results, log):
        log.debug("Results for %s/%s: %s", self.name(), device.id, results)

        resultXml = results[1]
        doc = ElementTree.fromstring(resultXml)
        relmaps = self.processComponent(doc, self.compdef, log, resultXml)

        log.debug(repr(relmaps))
        #return None
        return relmaps

    def processComponent(self, xmldoc, compdef, log, resultXml):
        def makeId(row):
            # The id field in the resulting XML is a guid
            return compdef.id + "_" + self.prepId(row.attrib['id'])

        #import pdb;pdb.set_trace()

        rm = self.relMap()
        for virtualElement in xmldoc:
            # Setup the object map
            om = self.objectMap()
            om.id = makeId(virtualElement)
            #om.guid = virtualElement.attrib['id']
            #om.href = virtualElement.attrib['href']
            om.title = virtualElement.find('name').text

            om.meta_type = "GenericComponent_" + compdef.id
            om.component_type = compdef.id

            # These are the attribute tags defined in the component XML
            om.setAttributes = {}
            for attribute in compdef.attributes:
                xpath = attribute.get("xpath", None)
                query = attribute.get("valueQuery", None)
                value = None
                node = virtualElement.find(xpath) if xpath else virtualElement
                if node is None:
                    log.warn("Unable to find xpath %s in %s", xpath, resultXml)
                    continue

                if query:
                    try:
                        value = eval(query, { 'here':node, } )
                    except Exception, ex:
                        log.error("Unable to evaluate XML node %s with statement: %s", 
                                  resultXml, query)
                        import pdb;pdb.set_trace()
                        continue

                else:
                    attrib = node.get(attribute['id'])
                    if attrib is not None:
                        value = attrib.text
                    else:
                        log.warn("Unable to find %s element in %s",
                                 attribute['id'], resultXml)
                        import pdb;pdb.set_trace()
                        continue
                om.setAttributes[attribute['id']] = value
            log.info("Found %s: %s", compdef.id,  om.title)
            rm.append(om)
        return rm

    def cruft(self, blue):
        for row in blue:
            if compdef.parentRelation:
                parentQuery = Template(compdef.parentRelation).substitute(row)
                parentRow = tables.query(parentQuery)
                if not parentRow:
                    log.warn("Found possible subcomponent at %s/%s, but could not find a parent.",
                        compdef.primaryTable, row['snmpindex'])
                    continue
                om.parentSnmpindex = parentRow['snmpindex']
                om.modname = "ZenPacks.zenoss.Liberator.GenericSubcomponent"

        sorted_subcomp_relmaps = {}
        for subcompdef in compdef.subcomponents:
            subcomp_relmaps = self.processComponent(tables, subcompdef, log)
            for subcomp_relmap in subcomp_relmaps:
                for subcomp_objmap in subcomp_relmap:
                    parentRow = tables.query("python:%s['snmpindex']['%s']" % (compdef.primaryTable, subcomp_objmap.parentSnmpindex))
                    subcomp_objmap.compname = "genericComponents/" + makeId(parentRow)
                    sorted_subcomp_relmaps.setdefault(subcomp_objmap.compname, RelationshipMap(
                        compname=subcomp_objmap.compname,
                        relname="subcomponents",
                        modname="ZenPacks.zenoss.Liberator.GenericSubcomponent")).append(subcomp_objmap)
        relmaps = [rm]
        relmaps.extend(sorted_subcomp_relmaps.values())
        return relmaps

