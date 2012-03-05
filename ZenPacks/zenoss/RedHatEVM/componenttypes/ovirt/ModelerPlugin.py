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

        doc = ElementTree.fromstring(results)

        tables = TableSet(tabledata)

        relmaps = self.processComponent(tables, self.compdef, log)

        log.debug(repr(relmaps))
        return relmaps

    def processComponent(self, tables, compdef, log):
        def makeId(row):
            return compdef.id + "_" + self.prepId(row[compdef.idField])
        rm = self.relMap()

        # Iterate over each row in the primary table
        for row in tables.query("/" + compdef.primaryTable + "/snmpindex").values():
            # Setup the object map
            om = self.objectMap()
            om.snmpindex = row['snmpindex']
            om.title = str(row[compdef.idField])
            om.id = makeId(row)
            om.meta_type = "GenericComponent_" + compdef.id
            om.component_type = compdef.id
            om.setAttributes = {}
            if compdef.parentRelation:
                parentQuery = Template(compdef.parentRelation).substitute(row)
                parentRow = tables.query(parentQuery)
                if not parentRow:
                    log.warn("Found possible subcomponent at %s/%s, but could not find a parent.",
                        compdef.primaryTable, row['snmpindex'])
                    continue
                om.parentSnmpindex = parentRow['snmpindex']
                om.modname = "ZenPacks.zenoss.Liberator.GenericSubcomponent"

            # These are the attribute tags defined in the component XML
            for attribute in compdef.attributes:
                query = attribute.get("valueQuery", None)
                value = None
                if query:
                    query = Template(query).substitute(row)
                    value = tables.query(query)
                else:
                    value = row.get(attribute['id'], None)
                om.setAttributes[attribute['id']] = value
            log.info("Found %s: %s", compdef.id,  om.title)
            rm.append(om)

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

