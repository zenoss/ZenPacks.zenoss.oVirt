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
#. Click on the ``Add Device`` menu item and select ``Add a Singe Device...`` option.
#. Add the name or IP address of the oVrit server and set the ``Device Class`` to be ``/oVrit``.
#. Click on the ``Add`` button.
#. Wait for the device to be modeled.
#. Navigate to the new device.
#. Click on the ``Configuration Properties`` item.
#. Update the following zProperties:
    * zOvirtServerName: name of the oVirt server as known by the oVirt server.
    * zOvirtPort: Port number where the oVirt server can be reached.
    * zOvirtUser: User name
    * zOvirtDomain: Domain in which the user credentials are valid.
    * zOvirtPassword: Password for the user
#. Run the ``zengenericmodeler`` daemon by click on the ``Commands`` item and selecting ``Liberator Modeler`` command.


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

