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

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSourcePlugin

from ZenPacks.zenoss.oVirtMonitor.utils import (
    createClient,
    result_errmsg,
    eventKey
)

from Products.ZenUtils.ZenTales import talesEvalStr
from Products.ZenModel.MinMaxThreshold import rpneval
from Products.ZenUtils.Utils import prepId
from cStringIO import StringIO
from lxml import etree


def string_to_lines(string):
    if isinstance(string, (list, tuple)):
        return string
    elif hasattr(string, 'splitlines'):
        return string.splitlines()

    return None


class oVirtDataSourcePlugin(PythonDataSourcePlugin):
    proxy_attributes = ('zCommandUsername', 'zCommandPassword', 'zoVirtSSL')

    @classmethod
    def config_key(cls, datasource, context):
            return (
                context.device().id,
                datasource.getCycleTime(context),
                datasource.rrdTemplate().id,
                datasource.id,
                datasource.plugin_classname)

    @classmethod
    def params(cls, datasource, context):
        params = {}

        device = context.device()
        d = {}
        c = {}
        for prop in device.propertyIds():
            try:
                d[prop] = float(device.getProperty(prop))

            except Exception:
                pass

        for prop in context.propertyIds():
            try:
                c[prop] = float(context.getProperty(prop))
            except Exception:
                pass

        environ = {'dev': d,
                   'device': d,
                   'devname': device.id,
                   'here': c,
                   'nothing': None,
                   }
        params['context'] = environ

        if hasattr(context, 'zapi_xpath'):
            params['zapi_xpath'] = context.zapi_xpath

        params['zapicall'] = datasource.talesEval(
            ' '.join(string_to_lines(datasource.zapicall)), context)
        params['delay'] = datasource.delay
        return params

    def collect(self, config):
        client = createClient(config)
        ds0 = config.datasources[0]
        return client.request(ds0.params['zapicall'])

    def onSuccess(self, results, config):
        data = self.new_data()
        tree = etree.parse(StringIO(results))
        for ds in config.datasources:
            for point in ds.points:
                if 'zapi_xpath' in ds.params:
                    try:
                        # Some points may not exist in the xml, skip those...
                        results = tree.xpath(ds.params['zapi_xpath']+point.xpath)[0]
                        # If rpn is defined, lets calculate the new results.
                        if point.rpn:
                            results = rpneval(
                                results, talesEvalStr(point.rpn, context=None, extra=ds.params['context']))
                        component_id = prepId(ds.component)
                        data['values'][component_id][point.id] = (results, 'N')
                    except Exception:
                        pass

        data['events'].append({
            'eventClassKey': 'oVirtCollectionSuccess',
            'eventKey': eventKey(config),
            'summary': 'ONTAP: successful collection',
            'eventClass': '/Status/Perf/',
            'device': config.id,
            'severity': 0,
        })
        return data

    def onError(self, results, config):
        errmsg = "ONTAP: %s" % result_errmsg(results)
        log.error('%s %s', config.id, errmsg)
        data = self.new_data()
        data['events'].append({
            'eventClassKey': 'oVirtCollectionError',
            'eventKey': eventKey(config),
            'eventClass': '/Status/Perf/',
            'summary': errmsg,
            'device': config.id,
            'severity': 4,
        })
        return data
