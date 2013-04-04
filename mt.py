#!/usr/bin/env zendmd
"""
Build monitoring templates based on a YAML input file.

Look at monitoring_templates.yml in the same directory for an example of what
the YAML schema should be.

WARNING: This will delete and recreated the named monitoring templates. So it
         can potentially be very destructive.
"""

try:
    from yaml import dump
except:
    print "Yaml not found, try running easy_install PyYaml"
    sys.exit(1)

import re
import sys
import types

import yaml
import yaml.constructor

# http://jira.zenoss.com/jira/browse/ZEN-5017
from Products.Zuul import info as ZuulInfo

from Products.Zuul.facades import ObjectNotFoundException

tf=getFacade('template')
prefix='/zport/dmd/Devices'
try:
    # included in standard lib from Python 2.7
    from collections import OrderedDict
except ImportError:
    # try importing the backported drop-in replacement
    # it's available on PyPI
    from ordereddict import OrderedDict

#### TODO: Support other types of graph points.
#from Products.ZenModel.GraphPoint import GraphPoint
#from Products.ZenModel.DataPointGraphPoint import DataPointGraphPoint


class OrderedDictYAMLLoader(yaml.Loader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

        self.add_constructor(u'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                'expected a mapping node, but found %s' % node.id, node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError, exc:
                raise yaml.constructor.ConstructorError('while constructing a mapping',
                    node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


def main():
    # sys.argv[0] is zendmd. Pop it so the script can use normal conventions.
    sys.argv.pop(0)
    if len(sys.argv) < 2:
        data = yaml.load(sys.stdin.read(), OrderedDictYAMLLoader)
    else:
        with open(sys.argv[1], 'r') as yaml_file:
            data = yaml.load(yaml_file, OrderedDictYAMLLoader)
    if data:
        for template_path, template_cfg in data.items():
            add_template(template_path, template_cfg)

        # commit comes from the zendmd interpreter.
        print "Templates loaded successfully."
        commit()
    else:
        print "No template found... exiting..."
        sys.exit(0)


def die(msg, *args):
    print >> sys.stderr, msg % args
    sys.exit(1)


def add_template(path, cfg):
    if '/' not in path:
        die("%s is not a path. Include device class and template name", path)

    path_parts = path.split('|')
    id_ = path_parts[1]
    cfg['deviceClass'] = path_parts[0]
    try:
        # dmd comes from the zendmd interpreter.
        device_class = tf.getTree(cfg['deviceClass'])
    except ObjectNotFoundException:
        die("%s is not a valid deviceClass.", cfg['deviceClass'])


    #existing_template = device_class.rrdTemplates._getOb(id_, None)
    existing_template = [t for t in tf.getObjTemplates(device_class.uid) if device_class.uid+'/rrdTemplates/'+id_ == t.uid]
    
    if existing_template:
        tf.deleteTemplate(existing_template[0].uid)

    template = tf.addTemplate(id_,device_class.uid)
    print "Loading template %s in %s" % (id_, device_class.uid) 
    if 'targetPythonClass' in cfg:
        template.targetPythonClass = cfg['targetPythonClass']

    if 'description' in cfg:
        template.description = cfg['description']

    if 'datasources' in cfg:
        for datasource_id, datasource_cfg in cfg['datasources'].items():
            add_datasource(template, datasource_id, datasource_cfg)
    
    # Define the thresholds first to be available for the graphs
    if 'thresholds' in cfg:
        for threshold_id, threshold_cfg in cfg['thresholds'].items():
            add_threshold(device_class,template, threshold_id, threshold_cfg)

    if 'graphs' in cfg:
        for graph_id, graph_cfg in cfg['graphs'].items():
            add_graph(device_class,template, graph_id, graph_cfg)



def add_datasource(template, id_, cfg):
    if 'type' not in cfg:
        die('No type for %s/%s.', template.id, id_)

    datasource_types = [ds_type['type'] for ds_type in tf.getDataSourceTypes()]
    if cfg['type'] not in datasource_types:
        die('%s datasource type is not one of %s.',
            cfg['type'], ', '.join(datasource_types))

    datasource = tf.addDataSource(template.uid,id_,cfg['type'])
    
    # http://jira.zenoss.com/jira/browse/ZEN-5017
    datasource = ZuulInfo(datasource)

    try:
        cfg['severity'] = cfg['severity'].lower()
    except:
        pass

    # Map severity names to values.
    if 'severity' in cfg:
        cfg['severity'] = {
            'critical': 5,
            'error': 4,
            'warning': 3,
            'unknown': 3,
            'info': 2,
            'debug': 1,
            'clear': 0,
        }.get(cfg['severity'], cfg['severity'])
   
    # Apply cfg items directly to datasource attributes.
    for k, v in cfg.items():
        if k not in ('type', 'datapoints'):
            #need to reference the object because 4.2.3
            #didnt register the commanddatasource properly.
            #http://jira.zenoss.com/jira/browse/ZEN-5303 
            setattr(datasource._object, k, v)

    if 'datapoints' in cfg:
        for datapoint_id, datapoint_cfg in cfg['datapoints'].items():
            add_datapoint(datasource, datapoint_id, datapoint_cfg)


def add_datapoint(datasource, id_, cfg):
    datapoint = tf.addDataPoint(datasource.uid,id_)
    
    # http://jira.zenoss.com/jira/browse/ZEN-5017
    datapoint = ZuulInfo(datapoint)


    # Handle cfg shortcuts like DERIVE_MIN_0 and GAUGE_MIN_0_MAX_100.
    if isinstance(cfg, types.StringTypes):
        if 'DERIVE' in cfg.upper():
            datapoint.rrdtype = 'DERIVE'

        min_match = re.search(r'MIN_(\d+)', cfg, re.IGNORECASE)
        if min_match:
            datapoint.rrdmin = min_match.group(1)

        max_match = re.search(r'MAX_(\d+)', cfg, re.IGNORECASE)
        if max_match:
            datapoint.rrdmax = max_match.group(1)

    else:
        # Apply cfg items directly to datasource attributes.
        for k, v in cfg.items():
            if k not in ('aliases'):
                setattr(datapoint, k, v)

        if 'aliases' in cfg:
            add_aliases(datapoint, cfg['aliases'])

def add_aliases(datapoint, aliases):
    data = []
    for id_ in aliases.keys():
        if aliases[id_]['formula'] == None:
            aliases[id_]['formula'] = ""
        data.append({'id':id_,'formula':aliases[id_]['formula']})
    
    tf.setInfo(datapoint.uid, {'aliases':data})
    
def add_graph(device_class,template, id_, cfg):
    tf.addGraphDefinition(template.uid,id_)
    
    # http://jira.zenoss.com/jira/browse/ZEN-5019
    graph = tf.getGraphDefinition(template.uid+'/graphDefs/'+id_)

    # Apply cfg items directly to graph attributes.
    for k, v in cfg.items():
        if k not in ('graphpoints'):
            setattr(graph, k, v)

    if 'graphpoints' in cfg:
        for graphpoint_id, graphpoint_cfg in cfg['graphpoints'].items():
            add_graphpoint(device_class,template,graph, graphpoint_id, graphpoint_cfg)

def add_graphpoint(device_class,template, graph, id_, cfg):
    if cfg['type'] == 'Threshold':
        threshold = [t for t in tf.getThresholds(template.uid) if t.name == id_][0]
        tf.addThresholdToGraph(graph.uid,threshold.uid)
    elif cfg['type'] == 'DataPoint':
        # this is all sorts of messed up getDataSources returns datapoints if the context is a device class
        # there isnt a getDataPoints call
        # the name of a datapoint appears to be a datasource.datapoint but the id path appears better
        # We are just splitting that and probably making some sort of bad assumption here.
        datapoints = [dp for dp in tf.getDataSources(device_class.uid) 
                                             if dp._object.name() == cfg['dpName'] and 
                                                template.uid in dp.uid]
        for datapoint in datapoints:
            tf.addDataPointToGraph(datapoint.uid,graph.uid)
    else:
        print "GraphPoint of %s is not supported yet." % cfg['type']
        return
    
    try:
        graphpoint = [gp for gp in tf.getGraphPoints(graph.uid) if gp.dpName == cfg['dpName']][0]
    except Exception:
        graphpoint = [gp for gp in tf.getGraphPoints(graph.uid) if gp.id == id_][0]
   
        
    
    # Apply cfg items directly to graph attributes.
    for k, v in cfg.items():
        if k not in ('type'):
            setattr(graph, k, v)



"""


    # Validate lineType.
    if 'lineType' in cfg:
        VALID_LINETYPES = ('DONTDRAW', 'LINE', 'AREA')

        if cfg['lineType'].upper() in VALID_LINETYPES:
            cfg['lineType'] = cfg['lineType'].upper()
        else:
            die('%s graphpoint lineType is not one of %s.',
                cfg['lineType'], ', '.join(VALID_LINETYPES))

    # Allow color to be specified by color_index instead of directly. This is
    # useful when you want to keep the normal progression of colors, but need
    # to add some DONTDRAW graphpoints for calculations.
    if 'colorindex' in cfg:
        try:
            colorindex = int(cfg['colorindex']) % len(GraphPoint.colors)
        except (TypeError, ValueError):
            die("graphpoint colorindex must be numeric.")

        cfg['color'] = GraphPoint.colors[colorindex].lstrip('#')

    # Apply cfg items directly to graphpoint attributes.
    for k, v in cfg.items():
        if k not in ('colorindex', 'graphpoints'):
            setattr(graphpoint, k, v)
"""
def add_threshold(device_class,template, id_, cfg):
    # This is weird, the catalog is making us look up the datapoints at the deviceclass level
    points = []
    allpoints = [(ds._object.name(),ds) for ds in tf.getDataSources(device_class.uid)]

    # Handle a single datapoint
    if isinstance(cfg['dataPoints'], str):
        cfg['dataPoints'] = [cfg['dataPoints']]
    
    for dp in cfg['dataPoints']:
        for item in allpoints:
            if item[0] == dp:
                points.append(item[1].uid)
    tf.addThreshold(template.uid,cfg['type'],id_,points)
    threshold = [t for t in tf.getThresholds(template.uid+'/thresholds/'+id_)][0]

    # Apply cfg items directly to threshold attributes.
    for k, v in cfg.items():
        if k not in ('dataPoints','type'):
            setattr(threshold, k, v)

if __name__ == '__main__':
    main()
