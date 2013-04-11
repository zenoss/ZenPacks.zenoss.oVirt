##############################################################################
#
# Copyright (C) Zenoss, Inc. 2012, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
log = logging.getLogger('zen.oVirtDataPoint')

from zope.component import adapts
from zope.interface import implements

from Products.Zuul.interfaces.template import IDataPointInfo
from Products.Zuul.infos.template import DataPointInfo
from Products.ZenModel.RRDDataPoint import RRDDataPoint

from Products.Zuul.form import schema
from Products.Zuul.utils import ZuulMessageFactory as _t
from Products.Zuul.infos import ProxyProperty


class oVirtDataPoint(RRDDataPoint):
    """Datasource used to capture datapoints from NetApp providers."""
    xpath = ""
    rpn = ""

    _properties = RRDDataPoint._properties + (
        {'id': 'xpath', 'type': 'string', 'mode': 'w'},
        {'id': 'rpn', 'type': 'string', 'mode': 'w'},
    )


class IoVirtDataPointInfo(IDataPointInfo):
    """ Info adapter """
    xpath = schema.TextLine(
        title=_t(u'xpath'))
    rpn = schema.TextLine(
        title=_t(u'rpn'))


class oVirtDataPointInfo(DataPointInfo):
    implements(IoVirtDataPointInfo)
    adapts(oVirtDataPoint)

    xpath = ProxyProperty('xpath')
    rpn = ProxyProperty('rpn')
