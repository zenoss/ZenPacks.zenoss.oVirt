######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

__doc__ = """catalog utilities
Make a search catalog to speed up device-to-guest searches
"""

import logging
log = logging.getLogger("zen.makesearchcatalog")

from Products.ZCatalog.ZCatalog import manage_addZCatalog
from Products.ZCatalog.Catalog import CatalogError

from Products.Zuul.interfaces import ICatalogTool
from Products.ZenUtils.Search import makeCaseInsensitiveKeywordIndex, \
    makeCaseInsensitiveFieldIndex


catalogName = 'oVirtGuestSearch'

indices = [
   ('id', makeCaseInsensitiveFieldIndex('id')),
   ('macAddresses', makeCaseInsensitiveKeywordIndex('macAddresses')),
]

def makeGuestSearchCatalog(dmd, relativePath, catalogName, indices):
    """
    Create or recreate an index with appropriate indices.
    """
    try:
        org = dmd.Devices.getObjByPath(relativePath)
    except KeyError:
        log.error("Unable to create catalog %s because /Devices/%s does not exist",
                  catalogName, relativePath)
        return

    if not hasattr(org, catalogName):
        log.info('Creating %s catalog', catalogName)
        manage_addZCatalog(org, catalogName, catalogName)

    # Add the indices
    cat = org._getOb(catalogName)._catalog
    for indexEntry in indices:
        try:
            cat.addIndex( *indexEntry )
        except CatalogError:
            # Index already exists
            pass

