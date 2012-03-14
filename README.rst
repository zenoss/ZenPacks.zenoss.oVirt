==========================
ZenPacks.zenoss.oVirt
==========================


About
------
This ZenPack models, collects events, and collects performance information from an oVirt server ( http://http://www.ovirt.org/ ) for data centers, clusters, hosts and virtual machines.


Features
--------

The ZenPack adds the following items:

================================== ======================================
Feature                            Description
================================== ======================================
Device Class                       /oVirt
Event Class                        /oVirt
Data Source                        oVirt
Daemons                            zenovirtevents, zenovirtperf
================================== ======================================


Prerequisites
--------------

==================  ==================================================================
Prerequisite        Restriction
==================  ==================================================================
Product             Zenoss 4.0 or higher
Required ZenPacks   ZenPacks.zenoss.Liberator, ZenPacks.zenoss.AdvancedSearch, ZenPacks.zenoss.Impact
Other dependencies  External oVirt server
==================  ==================================================================


Limitations
------------
This version of the ZenPack only supports HTTP access to the oVirt server.


Usage
------

Add an oVirt Server
++++++++++++++++++++++++++++++++

#. Navigate to the ``Infrastructure`` page
#. Click on the ``Add Device`` menu item and select ``Add oVirt Infrastructure...`` option.
#. Fill in the appropriate fields in the dialog box:
    * Name or ID: name by which the oVirt service will be created as a device under
    * Host: name or IP address of the oVirt server as known by the oVirt server.
    * Port #: Port number where the oVirt server can be reached.
    * Authentication Domain: Domain in which the user credentials are valid.
    * Username: User name
    * Password: Password for the user
    * Collector: Name of the remote collector which this should run.
#. Click on the ``Add`` button.
#. Wait for the device to be modeled.
#. Navigate to the new device.

Remodel an oVirt Server
++++++++++++++++++++++++++++++++
#. Navigate to the device.
#. Run the ``zengenericmodeler`` daemon by clicking on the ``Commands`` item and select the  ``Liberator Modeler`` command.


Installing
-----------
Install the ZenPack via the command line and restart Zenoss

``zenpack --install ZenPacks.zenoss.oVirt-1.0.0-py2.7.egg``
``zenoss restart``

Removing
---------
To remove the ZenPack, use the following command:

``zenpack --erase ZenPacks.zenoss.oVirt``
``zenoss restart``


Appendex Related Daemons
------------------------

======================  ==============
Type                    Name
======================  ==============
Event Collector         zenovirtevents
Performance Collection  zenovirtperf
======================  ==============

