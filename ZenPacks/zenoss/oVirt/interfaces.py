##########################################################################
#
#   Copyright 2012 Zenoss, Inc. All Rights Reserved.
#
##########################################################################

from Products.Zuul.form import schema
from Products.Zuul.interfaces.template import IRRDDataSourceInfo
from Products.Zuul.interfaces import IFacade
from Products.Zuul.utils import ZuulMessageFactory as _t


class IOVirtDataSourceInfo(IRRDDataSourceInfo):
    pass


class IOVirtFacade(IFacade):

    def addOVirtInfrastructure(id, host, port, username, domain, password, collector):
        """
        @param id: desired id of new oVirt endpoint
        @param host: hostname of oVirt endpoint to add
        @param port: port of oVirt endpoint to add
        @param username: valid admin username
        @param domain: domain where the username is valid
        @param password: password
        @param collector: the collector to use
        @returns JobId of oVirt modeling job or None if failed
        """

