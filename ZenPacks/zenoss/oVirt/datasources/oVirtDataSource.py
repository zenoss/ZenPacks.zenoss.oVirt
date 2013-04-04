##############################################################################
#
# Copyright (C) Zenoss, Inc. 2012, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
log = logging.getLogger('zen.oVirt')

from zope.component import adapts
from zope.interface import implements

from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.utils import ZuulMessageFactory as _t

from AccessControl import ClassSecurityInfo
from Products.ZenModel.ZenossSecurity import ZEN_MANAGE_DMD


from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSource, PythonDataSourceInfo, IPythonDataSourceInfo


class oVirtDataSource(PythonDataSource):
    """Datasource used to capture datapoints from oVirt providers."""

    ZENPACKID = 'ZenPacks.zenoss.oVirt'

    sourcetypes = ('oVirt',)
    sourcetype = sourcetypes[0]
    security = ClassSecurityInfo()
    plugin_classname = 'ZenPacks.zenoss.oVirt.datasource_plugins.oVirtDataSourcePlugin.oVirtDataSourcePlugin'

    zapicall = ''
    instance_uuid = '${here/zapi_uuid}'
    instance = ''
    xpath = '${here/zapi_perf_xpath}'
    delay = 0

    def getDescription(self):
        return self.zapicall

    _properties = PythonDataSource._properties + (
        {'id': 'zapicall', 'type': 'string'},
        {'id': 'instance_uuid', 'type': 'string'},
        {'id': 'instance', 'type': 'string'},
        {'id': 'xpath', 'type': 'string'},
        {'id': 'delay', 'type': 'string'},
    )

    '''
    def addDataPoints(self):
        """Abstract hook method, to be overridden in derived classes."""
        pass

    security.declareProtected(ZEN_MANAGE_DMD, 'manage_addRRDDataPoint')

    def manage_addRRDDataPoint(self, id, REQUEST=None):
        """make a RRDDataPoint"""
        if not id:
            return self.callZenScreen(REQUEST)
        #from Products.ZenModel.RRDDataPoint import RRDDataPoint
        from ..datapoints.oVirtDataPoint import oVirtDataPoint as RRDDataPoint
        dp = RRDDataPoint(id)
        self.datapoints._setObject(dp.id, dp)
        dp = self.datapoints._getOb(dp.id)
        if REQUEST:
            if dp:
                url = '%s/datapoints/%s' % (self.getPrimaryUrlPath(), dp.id)
                REQUEST['RESPONSE'].redirect(url)
            return self.callZenScreen(REQUEST)
        return dp
    '''

class IoVirtDataSourceInfo(IPythonDataSourceInfo):
    """ Info adapter """
    zapicall = schema.TextLine(title=_t(u'ZAPI Call'))
    instance_uuid = schema.TextLine(title=_t(u'Instance uuid'))
    instance = schema.TextLine(title=_t(u'Instance'))
    xpath = schema.TextLine(title=_t(u'Xpath'))
    delay = schema.TextLine(title=_t(u'Delay'))


class oVirtDataSourceInfo(PythonDataSourceInfo):
    implements(IoVirtDataSourceInfo)
    adapts(oVirtDataSource)

    zapicall = ProxyProperty('zapicall')
    delay = ProxyProperty('delay')
    instance_uuid = ProxyProperty('instance_uuid')
    instance = ProxyProperty('instance')
    xpath = ProxyProperty('xpath')
