#!/usr/bin/env python
###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, 2012 Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import os
import sys
import md5
import tempfile
import json
import time
import random
import datetime

import xml.utils.iso8601

from twisted.internet import reactor
from twisted.internet.defer import DeferredList, inlineCallbacks, returnValue

from utils import add_local_lib_path

add_local_lib_path()

import txovirt
from txovirt import CamelCase

# Map of ovirt severities to Zenoss Severity.
SEVERITY_MAP = {
    'warning': 3,
    }

#Map of ErrorCodes response parameter to textual description.
EVENT_TYPE_MAP = {
    0: "UNASSIGNED",
    1: "VDC_START",
    2: "VDC_STOP",
    12: "HOST_FAILURE",
    13: "HOST_DETECTED",
    14: "HOST_RECOVER",
    15: "HOST_MAINTENANCE",
    16: "HOST_ACTIVATE",
    17: "HOST_MAINTENANCE_FAILED",
    18: "HOST_ACTIVATE_FAILED",
    19: "HOST_RECOVER_FAILED",
    20: "USER_HOST_START",
    21: "USER_HOST_STOP",
    22: "IRS_FAILURE",
    26: "IRS_DISK_SPACE_LOW",
    30: "USER_VDC_LOGIN",
    31: "USER_VDC_LOGOUT",
    32: "USER_RUN_VM",
    33: "USER_STOP_VM",
    34: "USER_ADD_VM",
    35: "USER_UPDATE_VM",
    36: "USER_REMOVE_VM",
    37: "USER_ADD_VM_STARTED",
    38: "USER_CHANGE_DISK_VM",
    39: "USER_PAUSE_VM",
    40: "USER_RESUME_VM",
    41: "USER_HOST_RESTART",
    42: "USER_ADD_HOST",
    43: "USER_UPDATE_HOST",
    44: "USER_REMOVE_HOST",
    45: "USER_CREATE_SNAPSHOT",
    46: "USER_TRY_BACK_TO_SNAPSHOT",
    47: "USER_RESTORE_FROM_SNAPSHOT",
    48: "USER_ADD_VM_TEMPLATE",
    49: "USER_UPDATE_VM_TEMPLATE",
    50: "USER_REMOVE_VM_TEMPLATE",
    51: "USER_ADD_VM_TEMPLATE_FINISHED_SUCCESS",
    52: "USER_ADD_VM_TEMPLATE_FINISHED_FAILURE",
    53: "USER_ADD_VM_FINISHED_SUCCESS",
    54: "USER_FAILED_RUN_VM",
    55: "USER_FAILED_PAUSE_VM",
    56: "USER_FAILED_STOP_VM",
    57: "USER_FAILED_ADD_VM",
    58: "USER_FAILED_UPDATE_VM",
    59: "USER_FAILED_REMOVE_VM",
    60: "USER_ADD_VM_FINISHED_FAILURE",
    61: "VM_DOWN",
    62: "VM_MIGRATION_START",
    63: "VM_MIGRATION_DONE",
    64: "VM_MIGRATION_ABORT",
    65: "VM_MIGRATION_FAILED",
    66: "VM_FAILURE",
    68: "USER_CREATE_SNAPSHOT_FINISHED_SUCCESS",
    69: "USER_CREATE_SNAPSHOT_FINISHED_FAILURE",
    70: "USER_RUN_VM_AS_STATELESS_FINISHED_FAILURE",
    71: "USER_TRY_BACK_TO_SNAPSHOT_FINISH_SUCCESS",
    72: "USER_CHANGE_FLOPPY_VM",
    73: "USER_INITIATED_SHUTDOWN_VM",
    74: "USER_FAILED_SHUTDOWN_VM",
    75: "USER_FAILED_CHANGE_FLOPPY_VM",
    76: "USER_STOPPED_VM_INSTEAD_OF_SHUTDOWN",
    77: "USER_FAILED_STOPPING_VM_INSTEAD_OF_SHUTDOWN",
    78: "USER_ADD_DISK_TO_VM",
    79: "USER_FAILED_ADD_DISK_TO_VM",
    80: "USER_REMOVE_DISK_FROM_VM",
    81: "USER_FAILED_REMOVE_DISK_FROM_VM",
    82: "USER_MOVED_VM",
    83: "USER_FAILED_MOVE_VM",
    84: "USER_MOVED_TEMPLATE",
    85: "USER_FAILED_MOVE_TEMPLATE",
    86: "USER_COPIED_TEMPLATE",
    87: "USER_FAILED_COPY_TEMPLATE",
    88: "USER_UPDATE_VM_DISK",
    89: "USER_FAILED_UPDATE_VM_DISK",
    90: "USER_HOST_SHUTDOWN",
    91: "USER_MOVED_VM_FINISHED_SUCCESS",
    92: "USER_MOVED_VM_FINISHED_FAILURE",
    93: "USER_MOVED_TEMPLATE_FINISHED_SUCCESS",
    94: "USER_MOVED_TEMPLATE_FINISHED_FAILURE",
    95: "USER_COPIED_TEMPLATE_FINISHED_SUCCESS",
    96: "USER_COPIED_TEMPLATE_FINISHED_FAILURE",
    97: "USER_ADD_DISK_TO_VM_FINISHED_SUCCESS",
    98: "USER_ADD_DISK_TO_VM_FINISHED_FAILURE",
    99: "USER_TRY_BACK_TO_SNAPSHOT_FINISH_FAILURE",
    100: "USER_RESTORE_FROM_SNAPSHOT_FINISH_SUCCESS",
    101: "USER_RESTORE_FROM_SNAPSHOT_FINISH_FAILURE",
    102: "USER_FAILED_CHANGE_DISK_VM",
    103: "USER_FAILED_RESUME_VM",
    104: "USER_FAILED_ADD_HOST",
    105: "USER_FAILED_UPDATE_HOST",
    106: "USER_FAILED_REMOVE_HOST",
    107: "USER_FAILED_HOST_RESTART",
    108: "USER_FAILED_ADD_VM_TEMPLATE",
    109: "USER_FAILED_UPDATE_VM_TEMPLATE",
    110: "USER_FAILED_REMOVE_VM_TEMPLATE",
    111: "USER_STOP_SUSPENDED_VM",
    112: "USER_STOP_SUSPENDED_VM_FAILED",
    113: "USER_REMOVE_VM_FINISHED",
    114: "USER_VDC_LOGIN_FAILED",
    115: "USER_FAILED_TRY_BACK_TO_SNAPSHOT",
    116: "USER_FAILED_RESTORE_FROM_SNAPSHOT",
    117: "USER_FAILED_CREATE_SNAPSHOT",
    118: "USER_FAILED_HOST_START",
    119: "VM_DOWN_ERROR",
    120: "VM_MIGRATION_FAILED_FROM_TO",
    121: "SYSTEM_HOST_RESTART",
    122: "SYSTEM_FAILED_HOST_RESTART",
    123: "HOST_SLOW_STORAGE_RESPONSE_TIME",
    124: "VM_IMPORT",
    125: "VM_IMPORT_FAILED",
    126: "VM_NOT_RESPONDING",
    127: "HOST_RUN_IN_NO_KVM_MODE",
    128: "VM_MIGRATION_TRYING_RERUN",
    129: "VM_CLEARED",
    130: "USER_FAILED_HOST_SHUTDOWN",
    131: "USER_EXPORT_VM",
    132: "USER_EXPORT_VM_FAILED",
    133: "USER_EXPORT_TEMPLATE",
    134: "USER_EXPORT_TEMPLATE_FAILED",
    135: "TEMPLATE_IMPORT",
    136: "TEMPLATE_IMPORT_FAILED",
    137: "USER_FAILED_HOST_STOP",
    138: "VM_PAUSED_ENOSPC",
    139: "VM_PAUSED_ERROR",
    140: "VM_MIGRATION_FAILED_DURING_MOVE_TO_MAINTANANCE",
    141: "HOST_VERSION_NOT_SUPPORTED_FOR_CLUSTER",
    142: "VM_SET_TO_UNKNOWN_STATUS",
    143: "VM_WAS_SET_DOWN_DUE_TO_HOST_REBOOT_OR_MANUAL_FENCE",
    144: "VM_IMPORT_INFO",
    145: "VM_BLK_VIRTIO_NO_CACHE",
    149: "USER_ADD",
    150: "USER_INITIATED_RUN_VM",
    151: "USER_INITIATED_RUN_VM_FAILED",
    152: "USER_RUN_VM_ON_NON_DEFAULT_HOST",
    153: "USER_STARTED_VM",
    182: "USER_FAILED_ATTACH_USER_TO_VM",
    201: "IRS_DISK_SPACE_LOW_ERROR",
    204: "IRS_HOSTED_ON_HOST",
    250: "USER_UPDATE_VM_CLUSTER_DEFAULT_HOST_CLEARED",
    251: "USER_REMOVE_VM_TEMPLATE_FINISHED",
    300: "USER_ADD_VM_POOL",
    301: "USER_ADD_VM_POOL_FAILED",
    302: "USER_ADD_VM_POOL_WITH_VMS",
    303: "USER_ADD_VM_POOL_WITH_VMS_FAILED",
    304: "USER_REMOVE_VM_POOL",
    305: "USER_REMOVE_VM_POOL_FAILED",
    306: "USER_ADD_VM_TO_POOL",
    307: "USER_ADD_VM_TO_POOL_FAILED",
    308: "USER_REMOVE_VM_FROM_POOL",
    309: "USER_REMOVE_VM_FROM_POOL_FAILED",
    310: "USER_ATTACH_USER_TO_POOL",
    311: "USER_ATTACH_USER_TO_POOL_FAILED",
    312: "USER_DETACH_USER_FROM_POOL",
    313: "USER_DETACH_USER_FROM_POOL_FAILED",
    314: "USER_UPDATE_VM_POOL",
    315: "USER_UPDATE_VM_POOL_FAILED",
    316: "USER_ATTACH_USER_TO_VM_FROM_POOL",
    317: "USER_ATTACH_USER_TO_VM_FROM_POOL_FAILED",
    318: "USER_ATTACH_USER_TO_VM_FROM_POOL_FINISHED_SUCCESS",
    319: "USER_ATTACH_USER_TO_VM_FROM_POOL_FINISHED_FAILURE",
    320: "USER_ADD_VM_POOL_WITH_VMS_ADD_HOST_FAILED",
    325: "USER_REMOVE_ADUSER",
    326: "USER_FAILED_REMOVE_ADUSER",
    327: "USER_FAILED_ADD_ADUSER",
    328: "USER_ATTACH_USER_TO_TIME_LEASED_POOL",
    329: "USER_ATTACH_USER_TO_TIME_LEASED_POOL_FAILED",
    330: "USER_DETACH_USER_FROM_TIME_LEASED_POOL",
    331: "USER_DETACH_USER_FROM_TIME_LEASED_POOL_FAILED",
    332: "USER_ATTACH_AD_GROUP_TO_TIME_LEASED_POOL",
    333: "USER_ATTACH_AD_GROUP_TO_TIME_LEASED_POOL_FAILED",
    334: "USER_DETACH_AD_GROUP_FROM_TIME_LEASED_POOL",
    335: "USER_DETACH_AD_GROUP_FROM_TIME_LEASED_POOL_FAILED",
    336: "USER_UPDATE_USER_TO_TIME_LEASED_POOL",
    337: "USER_UPDATE_USER_TO_TIME_LEASED_POOL_FAILED",
    338: "USER_UPDATE_AD_GROUP_TO_TIME_LEASED_POOL",
    339: "USER_UPDATE_AD_GROUP_TO_TIME_LEASED_POOL_FAILED",
    342: "USER_MERGE_SNAPSHOT",
    343: "USER_FAILED_MERGE_SNAPSHOT",
    344: "USER_UPDATE_VM_POOL_WITH_VMS",
    345: "USER_UPDATE_VM_POOL_WITH_VMS_FAILED",
    346: "USER_PASSWORD_CHANGED",
    347: "USER_PASSWORD_CHANGE_FAILED",
    348: "USER_CLEAR_UNKNOWN_VMS",
    349: "USER_FAILED_CLEAR_UNKNOWN_VMS",
    350: "USER_ADD_BOOKMARK",
    351: "USER_ADD_BOOKMARK_FAILED",
    352: "USER_UPDATE_BOOKMARK",
    353: "USER_UPDATE_BOOKMARK_FAILED",
    354: "USER_REMOVE_BOOKMARK",
    355: "USER_REMOVE_BOOKMARK_FAILED",
    356: "USER_MERGE_SNAPSHOT_FINISHED_SUCCESS",
    357: "USER_MERGE_SNAPSHOT_FINISHED_FAILURE",
    360: "USER_DETACH_USER_FROM_VM",
    361: "USER_FAILED_DETACH_USER_FROM_VM",
    400: "USER_ATTACH_VM_TO_AD_GROUP",
    401: "USER_ATTACH_VM_TO_AD_GROUP_FAILED",
    402: "USER_DETACH_VM_TO_AD_GROUP",
    403: "USER_DETACH_VM_TO_AD_GROUP_FAILED",
    404: "USER_ATTACH_VM_POOL_TO_AD_GROUP",
    405: "USER_ATTACH_VM_POOL_TO_AD_GROUP_FAILED",
    406: "USER_DETACH_VM_POOL_TO_AD_GROUP",
    407: "USER_DETACH_VM_POOL_TO_AD_GROUP_FAILED",
    408: "USER_REMOVE_AD_GROUP",
    409: "USER_REMOVE_AD_GROUP_FAILED",
    430: "USER_UPDATE_TAG",
    431: "USER_UPDATE_TAG_FAILED",
    432: "USER_ADD_TAG",
    433: "USER_ADD_TAG_FAILED",
    434: "USER_REMOVE_TAG",
    435: "USER_REMOVE_TAG_FAILED",
    436: "USER_ATTACH_TAG_TO_USER",
    437: "USER_ATTACH_TAG_TO_USER_FAILED",
    438: "USER_ATTACH_TAG_TO_USER_GROUP",
    439: "USER_ATTACH_TAG_TO_USER_GROUP_FAILED",
    440: "USER_ATTACH_TAG_TO_VM",
    441: "USER_ATTACH_TAG_TO_VM_FAILED",
    442: "USER_ATTACH_TAG_TO_HOST",
    443: "USER_ATTACH_TAG_TO_HOST_FAILED",
    444: "USER_DETACH_HOST_FROM_TAG",
    445: "USER_DETACH_HOST_FROM_TAG_FAILED",
    446: "USER_DETACH_VM_FROM_TAG",
    447: "USER_DETACH_VM_FROM_TAG_FAILED",
    448: "USER_DETACH_USER_FROM_TAG",
    449: "USER_DETACH_USER_FROM_TAG_FAILED",
    450: "USER_DETACH_USER_GROUP_FROM_TAG",
    451: "USER_DETACH_USER_GROUP_FROM_TAG_FAILED",
    452: "USER_ATTACH_TAG_TO_USER_EXISTS",
    453: "USER_ATTACH_TAG_TO_USER_GROUP_EXISTS",
    454: "USER_ATTACH_TAG_TO_VM_EXISTS",
    455: "USER_ATTACH_TAG_TO_HOST_EXISTS",
    456: "USER_LOGGED_IN_VM",
    457: "USER_LOGGED_OUT_VM",
    458: "USER_LOCKED_VM",
    459: "USER_UNLOCKED_VM",
    460: "USER_DETACH_USER_FROM_TIME_LEASED_POOL_INTERNAL",
    461: "USER_DETACH_USER_FROM_TIME_LEASED_POOL_FAILED_INTERNAL",
    462: "USER_DETACH_AD_GROUP_FROM_TIME_LEASED_POOL_INTERNAL",
    463: "USER_DETACH_AD_GROUP_FROM_TIME_LEASED_POOL_FAILED_INTERNAL",
    467: "UPDATE_TAGS_VM_DEFAULT_DISPLAY_TYPE",
    468: "UPDATE_TAGS_VM_DEFAULT_DISPLAY_TYPE_FAILED",
    470: "USER_ATTACH_VM_POOL_TO_AD_GROUP_INTERNAL",
    471: "USER_ATTACH_VM_POOL_TO_AD_GROUP_FAILED_INTERNAL",
    472: "USER_ATTACH_USER_TO_POOL_INTERNAL",
    473: "USER_ATTACH_USER_TO_POOL_FAILED_INTERNAL",
    494: "HOST_MANUAL_FENCE_STATUS",
    495: "HOST_MANUAL_FENCE_STATUS_FAILED",
    496: "HOST_FENCE_STATUS",
    497: "HOST_FENCE_STATUS_FAILED",
    498: "HOST_APPROVE",
    499: "HOST_APPROVE_FAILED",
    500: "HOST_FAILED_TO_RUN_VMS",
    501: "USER_SUSPEND_VM",
    502: "USER_FAILED_SUSPEND_VM",
    503: "USER_SUSPEND_VM_OK",
    504: "HOST_INSTALL",
    505: "HOST_INSTALL_FAILED",
    506: "HOST_INITIATED_RUN_VM",
    507: "HOST_INITIATED_RUN_VM_FAILED",
    509: "HOST_INSTALL_IN_PROGRESS",
    510: "HOST_INSTALL_IN_PROGRESS_WARNING",
    511: "HOST_INSTALL_IN_PROGRESS_ERROR",
    512: "USER_SUSPEND_VM_FINISH_SUCCESS",
    513: "HOST_RECOVER_FAILED_VMS_UNKNOWN",
    514: "HOST_INITIALIZING",
    515: "HOST_CPU_LOWER_THAN_CLUSTER",
    516: "HOST_CPU_RETRIEVE_FAILED",
    517: "HOST_SET_NONOPERATIONAL",
    518: "HOST_SET_NONOPERATIONAL_FAILED",
    519: "HOST_SET_NONOPERATIONAL_NETWORK",
    520: "USER_ATTACH_USER_TO_VM",
    521: "USER_SUSPEND_VM_FINISH_FAILURE",
    522: "HOST_SET_NONOPERATIONAL_DOMAIN",
    523: "HOST_SET_NONOPERATIONAL_DOMAIN_FAILED",
    524: "AUTO_SUSPEND_VM",
    524: "HOST_DOMAIN_DELAY_INTERVAL",
    525: "AUTO_SUSPEND_VM_FINISH_SUCCESS",
    526: "AUTO_SUSPEND_VM_FINISH_FAILURE",
    527: "AUTO_FAILED_SUSPEND_VM",
    528: "USER_EJECT_VM_DISK",
    529: "USER_EJECT_VM_FLOPPY",
    530: "HOST_MANUAL_FENCE_FAILED_CALL_FENCE_SPM",
    531: "HOST_LOW_MEM",
    555: "USER_MOVE_TAG",
    556: "USER_MOVE_TAG_FAILED",
    600: "USER_HOST_MAINTENANCE",
    601: "CPU_FLAGS_NX_IS_MISSING",
    602: "USER_HOST_MAINTENANCE_MIGRATION_FAILED",
    603: "HOST_SET_NONOPERATIONAL_IFACE_DOWN",
    800: "IMAGES_SYNCRONIZER_DESKTOP_NOT_EXIST_IN_VDC",
    801: "IMAGES_SYNCRONIZER_TEMPLATE_NOT_EXIST_IMAGE_EXIST",
    802: "IMAGES_SYNCRONIZER_SNAPSHOT_NOT_EXIST_IN_VDC",
    803: "IMAGES_SYNCRONIZER_SNAPSHOTS_NOT_ATTACHED_TO_VM_IN_VDC",
    804: "IMAGES_SYNCRONIZER_TEMPLATE_NOT_EXIST_IN_VDC",
    805: "IMAGES_SYNCRONIZER_DESKTOP_NOT_EXIST_IN_IRS",
    806: "IMAGES_SYNCRONIZER_SNAPSHOT_NOT_EXIST_IN_IRS",
    807: "IMAGES_SYNCRONIZER_DESKTOP_WITHOUT_TEMPLATE_VDC",
    808: "IMAGES_SYNCRONIZER_IMAGE_TEMPLATE_NOT_EXIST",
    809: "USER_ADD_HOST_GROUP",
    810: "USER_ADD_HOST_GROUP_FAILED",
    811: "USER_UPDATE_HOST_GROUP",
    812: "USER_UPDATE_HOST_GROUP_FAILED",
    813: "USER_REMOVE_HOST_GROUP",
    814: "USER_REMOVE_HOST_GROUP_FAILED",
    815: "USER_VDC_LOGOUT_FAILED",
    816: "MAC_POOL_EMPTY",
    817: "CERTIFICATE_FILE_NOT_FOUND",
    818: "RUN_VM_FAILED",
    819: "HOST_REGISTER_ERROR_UPDATING_HOST",
    820: "HOST_REGISTER_ERROR_UPDATING_HOST_ALL_TAKEN",
    821: "HOST_REGISTER_HOST_IS_ACTIVE",
    822: "HOST_REGISTER_ERROR_UPDATING_NAME",
    823: "HOST_REGISTER_ERROR_UPDATING_NAMES_ALL_TAKEN",
    824: "HOST_REGISTER_NAME_IS_ACTIVE",
    825: "HOST_REGISTER_AUTO_APPROVE_PATTERN",
    826: "HOST_REGISTER_FAILED",
    827: "HOST_REGISTER_EXISTING_HOST_UPDATE_FAILED",
    828: "HOST_REGISTER_SUCCEEDED",
    829: "VM_MIGRATION_ON_CONNECT_CHECK_FAILED",
    830: "VM_MIGRATION_ON_CONNECT_CHECK_SUCCEEDED",
    831: "USER_DEDICATE_VM_TO_POWERCLIENT",
    832: "USER_DEDICATE_VM_TO_POWERCLIENT_FAILED",
    833: "MAC_ADDRESS_IS_IN_USE",
    835: "SYSTEM_UPDATE_HOST_GROUP",
    836: "SYSTEM_UPDATE_HOST_GROUP_FAILED",
    850: "USER_ADD_PERMISSION",
    851: "USER_ADD_PERMISSION_FAILED",
    852: "USER_REMOVE_PERMISSION",
    853: "USER_REMOVE_PERMISSION_FAILED",
    854: "USER_ADD_ROLE",
    855: "USER_ADD_ROLE_FAILED",
    856: "USER_UPDATE_ROLE",
    857: "USER_UPDATE_ROLE_FAILED",
    858: "USER_REMOVE_ROLE",
    859: "USER_REMOVE_ROLE_FAILED",
    860: "USER_ATTACHED_ACTION_GROUP_TO_ROLE",
    861: "USER_ATTACHED_ACTION_GROUP_TO_ROLE_FAILED",
    862: "USER_DETACHED_ACTION_GROUP_FROM_ROLE",
    863: "USER_DETACHED_ACTION_GROUP_FROM_ROLE_FAILED",
    864: "USER_ADD_ROLE_WITH_ACTION_GROUP",
    865: "USER_ADD_ROLE_WITH_ACTION_GROUP_FAILED",
    900: "AD_COMPUTER_ACCOUNT_SUCCEEDED",
    901: "AD_COMPUTER_ACCOUNT_FAILED",
    920: "NETWORK_ATTACH_NETWORK_TO_HOST",
    921: "NETWORK_ATTACH_NETWORK_TO_HOST_FAILED",
    922: "NETWORK_DETACH_NETWORK_FROM_HOST",
    923: "NETWORK_DETACH_NETWORK_FROM_HOST_FAILED",
    924: "NETWORK_ADD_BOND",
    925: "NETWORK_ADD_BOND_FAILED",
    926: "NETWORK_REMOVE_BOND",
    927: "NETWORK_REMOVE_BOND_FAILED",
    928: "NETWORK_HOST_NETWORK_MATCH_CLUSTER",
    929: "NETWORK_HOST_NETWORK_NOT_MATCH_CLUSTER",
    930: "NETWORK_REMOVE_VM_INTERFACE",
    931: "NETWORK_REMOVE_VM_INTERFACE_FAILED",
    932: "NETWORK_ADD_VM_INTERFACE",
    933: "NETWORK_ADD_VM_INTERFACE_FAILED",
    934: "NETWORK_UPDATE_VM_INTERFACE",
    935: "NETWORK_UPDATE_VM_INTERFACE_FAILED",
    936: "NETWORK_ADD_TEMPLATE_INTERFACE",
    937: "NETWORK_ADD_TEMPLATE_INTERFACE_FAILED",
    938: "NETWORK_REMOVE_TEMPLATE_INTERFACE",
    939: "NETWORK_REMOVE_TEMPLATE_INTERFACE_FAILED",
    940: "NETWORK_UPDATE_TEMPLATE_INTERFACE",
    941: "NETWORK_UPDATE_TEMPLATE_INTERFACE_FAILED",
    942: "NETWORK_ADD_NETWORK",
    943: "NETWORK_ADD_NETWORK_FAILED",
    944: "NETWORK_REMOVE_NETWORK",
    945: "NETWORK_REMOVE_NETWORK_FAILED",
    946: "NETWORK_ATTACH_NETWORK_TO_HOST_GROUP",
    947: "NETWORK_ATTACH_NETWORK_TO_HOST_GROUP_FAILED",
    948: "NETWORK_DETACH_NETWORK_TO_HOST_GROUP",
    949: "NETWORK_DETACH_NETWORK_TO_HOST_GROUP_FAILED",
    950: "USER_ADD_STORAGE_POOL",
    951: "USER_ADD_STORAGE_POOL_FAILED",
    952: "USER_UPDATE_STORAGE_POOL",
    953: "USER_UPDATE_STORAGE_POOL_FAILED",
    954: "USER_REMOVE_STORAGE_POOL",
    955: "USER_REMOVE_STORAGE_POOL_FAILED",
    956: "USER_ADD_STORAGE_DOMAIN",
    957: "USER_ADD_STORAGE_DOMAIN_FAILED",
    958: "USER_UPDATE_STORAGE_DOMAIN",
    959: "USER_UPDATE_STORAGE_DOMAIN_FAILED",
    960: "USER_REMOVE_STORAGE_DOMAIN",
    961: "USER_REMOVE_STORAGE_DOMAIN_FAILED",
    962: "USER_ATTACH_STORAGE_DOMAIN_TO_POOL",
    963: "USER_ATTACH_STORAGE_DOMAIN_TO_POOL_FAILED",
    964: "USER_DETACH_STORAGE_DOMAIN_FROM_POOL",
    965: "USER_DETACH_STORAGE_DOMAIN_FROM_POOL_FAILED",
    966: "USER_ACTIVATED_STORAGE_DOMAIN",
    967: "USER_ACTIVATE_STORAGE_DOMAIN_FAILED",
    968: "USER_DEACTIVATED_STORAGE_DOMAIN",
    969: "USER_DEACTIVATE_STORAGE_DOMAIN_FAILED",
    970: "SYSTEM_DEACTIVATED_STORAGE_DOMAIN",
    971: "SYSTEM_DEACTIVATE_STORAGE_DOMAIN_FAILED",
    972: "USER_EXTENDED_STORAGE_DOMAIN",
    973: "USER_EXTENDED_STORAGE_DOMAIN_FAILED",
    974: "USER_REMOVE_VG",
    975: "USER_REMOVE_VG_FAILED",
    976: "USER_ACTIVATE_STORAGE_POOL",
    977: "USER_ACTIVATE_STORAGE_POOL_FAILED",
    978: "SYSTEM_FAILED_CHANGE_STORAGE_POOL_STATUS",
    979: "SYSTEM_CHANGE_STORAGE_POOL_STATUS_NO_HOST_FOR_SPM",
    980: "SYSTEM_CHANGE_STORAGE_POOL_STATUS_PROBLEMATIC",
    981: "USER_FORCE_REMOVE_STORAGE_DOMAIN",
    982: "USER_FORCE_REMOVE_STORAGE_DOMAIN_FAILED",
    983: "RECONSTRUCT_MASTER_FAILED_NO_MASTER",
    984: "RECONSTRUCT_MASTER_DONE",
    985: "RECONSTRUCT_MASTER_FAILED",
    986: "SYSTEM_CHANGE_STORAGE_POOL_STATUS_PROBLEMATIC_SEARCHING_NEW_SPM",
    987: "SYSTEM_CHANGE_STORAGE_POOL_STATUS_PROBLEMATIC_WITH_ERROR",
    988: "USER_CONNECT_HOSTS_TO_LUN_FAILED",
    989: "SYSTEM_CHANGE_STORAGE_POOL_STATUS_PROBLEMATIC_FROM_NON_OPERATIONAL",
    990: "SYSTEM_MASTER_DOMAIN_NOT_IN_SYNC",
    991: "RECOVERY_STORAGE_POOL",
    992: "RECOVERY_STORAGE_POOL_FAILED",
    993: "SYSTEM_CHANGE_STORAGE_POOL_STATUS_RESET_IRS",
    994: "CONNECT_STORAGE_SERVERS_FAILED",
    995: "CONNECT_STORAGE_POOL_FAILED",
    996: "STORAGE_DOMAIN_ERROR",
    1100: "NETWORK_UPDATE_DISPLAY_TO_HOST_GROUP",
    1101: "NETWORK_UPDATE_DISPLAY_TO_HOST_GROUP_FAILED",
    1102: "NETWORK_UPDATE_NETWORK_TO_HOST_INTERFACE",
    1103: "NETWORK_UPDATE_NETWORK_TO_HOST_INTERFACE_FAILED",
    1104: "NETWORK_COMMINT_NETWORK_CHANGES",
    1105: "NETWORK_COMMINT_NETWORK_CHANGES_FAILED",
    1106: "NETWORK_HOST_USING_WRONG_CLUSER_VLAN",
    1107: "NETWORK_HOST_MISSING_CLUSER_VLAN",
    1150: "IMPORTEXPORT_EXPORT_VM",
    1151: "IMPORTEXPORT_EXPORT_VM_FAILED",
    1152: "IMPORTEXPORT_IMPORT_VM",
    1153: "IMPORTEXPORT_IMPORT_VM_FAILED",
    1154: "IMPORTEXPORT_REMOVE_TEMPLATE",
    1155: "IMPORTEXPORT_REMOVE_TEMPLATE_FAILED",
    1156: "IMPORTEXPORT_EXPORT_TEMPLATE",
    1157: "IMPORTEXPORT_EXPORT_TEMPLATE_FAILED",
    1158: "IMPORTEXPORT_IMPORT_TEMPLATE",
    1159: "IMPORTEXPORT_IMPORT_TEMPLATE_FAILED",
    1160: "IMPORTEXPORT_REMOVE_VM",
    1161: "IMPORTEXPORT_REMOVE_VM_FAILED",
    1162: "IMPORTEXPORT_STARTING_EXPORT_VM",
    1163: "IMPORTEXPORT_STARTING_IMPORT_TEMPLATE",
    1164: "IMPORTEXPORT_STARTING_EXPORT_TEMPLATE",
    1165: "IMPORTEXPORT_STARTING_IMPORT_VM",
    1166: "IMPORTEXPORT_STARTING_REMOVE_TEMPLATE",
    1167: "IMPORTEXPORT_STARTING_REMOVE_VM",
    1168: "IMPORTEXPORT_FAILED_TO_IMPORT_VM",
    1169: "IMPORTEXPORT_FAILED_TO_IMPORT_TEMPLATE",
    9000: "HOST_ALERT_FENCING_IS_NOT_CONFIGURED",
    9001: "HOST_ALERT_FENCING_TEST_FAILED",
    9002: "HOST_ALERT_FENCING_OPERATION_FAILED",
    9003: "HOST_ALERT_FENCING_OPERATION_SKIPPED",
    9004: "HOST_ALERT_FENCING_NO_PROXY_HOST",
    9500: "TASK_STOPPING_ASYNC_TASK",
    9501: "TASK_CLEARING_ASYNC_TASK"
}


def elementtree_to_dict(element):
    node = {}

    text = getattr(element, 'text', None)
    if text is not None:
        node['text'] = text

    node.update(element.items())  # element's attributes

    child_nodes = {}
    for child in element:  # element's children
        child_nodes.setdefault(child.tag, []).append(elementtree_to_dict(child))

    # convert all single-element lists into non-lists
    for key, value in child_nodes.items():
        if len(value) == 1:
            if 'text' in value[0].keys():
                child_nodes[key] = value[0]['text']
            else:
                child_nodes[key] = value[0]

    node.update(child_nodes.items())
    return node


class oVirtPoller(object):
    """Caching poller that gathers events and statistics from an ovirt system"""

    def __init__(self, url, username, domain, password, collect_events=False):
        self._url = url
        self._username = username
        self._domain = domain
        self._password = password
        self._collect_events = collect_events
        self._events = []
        self._values = {}
        self.client = txovirt.Client(
            self._url,
            self._username,
            self._domain,
            self._password)

    def _temp_filename(self, key):
        """Create a tempfile for the cache based on a key"""
        target_hash = md5.md5('%s+%s+%s' % (self._url, self._username, self._domain)).hexdigest()

        return os.path.join(
            tempfile.gettempdir(),
            '.zenoss_ovirt_%s_%s' % (key, target_hash))

    def _save(self, data, key):
        tmpfile = self._temp_filename(key=key)
        tmp = open(tmpfile, 'w')
        json.dump(data, tmp)
        tmp.close()

    def _saved(self, key):
        tmpfile = self._temp_filename(key=key)
        if not os.path.isfile(tmpfile):
            return None

        # Make sure temporary data isn't too stale.
        if os.stat(tmpfile).st_mtime < (time.time() - 50):
            os.unlink(tmpfile)
            return None

        try:
            tmp = open(tmpfile, 'r')
            values = json.load(tmp)
            tmp.close()
        except ValueError:
            # Error loading the json out of the cache, lets remove the cache.
            os.unlink(tmpfile)
            return None

        return values

    def _saved_values(self):
        return self._saved(key='values')

    def _print_output(self):
        print json.dumps({'events': self._events, 'values': self._values}, sort_keys=True, indent=4)

    def _process_events(self, response):
        response = response[0]
        events = []

        last_events = self._saved(key='events')
        last_event_ids = set()
        if last_events:
            for event in last_events:
                last_event_ids.add(event['id'])

        new_events = elementtree_to_dict(response)['event']
        new_event_ids = set()

        #Update the saved events cache
        self._save(new_events, key='events')

        for event in new_events:
            # Use for generating clears later.
            new_event_ids.add(event['id'])

            if event['id'] in last_event_ids:
                continue

            rcvtime = xml.utils.iso8601.parse(event['time'])

            # Dont send alerts for logins and logouts
            if 'logged in' in event['description']:
                continue
            if 'logged out' in event['description']:
                continue

            event_type = EVENT_TYPE_MAP.get(int(event['code']), 'Unknown (%s)' % event['code'])
            #Process severity
            if 'severity' in event.keys():
                severity = SEVERITY_MAP.get(event['severity'], 3)
            else:
                severity = 3

            events.append(dict(
                severity=severity,
                summary=event['description'],
                message='%s: %s' % (event_type, event['description']),
                eventKey='event_%s' % event['id'],
                eventClassKey='ovirt_alert',
                rcvtime=rcvtime,
                ovirt_type=event_type
                ))

        # Send clear events for events that no longer exist.
        if last_events:
            for event in last_events:
                # Dont send clears for logins and logouts
                if 'logged in' in event['description']:
                    continue
                if 'logged out' in event['description']:
                    continue
                if event['id'] not in new_event_ids:
                    event_type = EVENT_TYPE_MAP.get(int(event['code']), 'Unknown (%s)' % event['code'])
                    events.append(dict(
                        severity=0,
                        summary=event['description'],
                        message='%s: %s' % (event_type, event['description']),
                        eventKey='event_%s' % event['id'],
                        eventClassKey='ovirt_alert',
                        ovirt_type=event_type,
                        ))

        self._save(new_events, key='events')
        return events

    def _process_statistics(self, responses):

        results = {}
        for (host, response) in responses:
            results.setdefault(host['id'], {})

            for metric in response.getchildren():
                results[host['id']][CamelCase(metric.find('name').text)] = metric.find('values').find('value').find('datum').text

        return results

    def _errback(self, result):
        if reactor.running:
            reactor.stop()
        error = result.getErrorMessage()
        self._events.append(dict(
                  severity=4,
                  summary='oVirt error: %s' % error,
                  eventKey='ovirt_failure',
                  eventClassKey='ovirt_error',
                  ))
        self._print_output()

    @inlineCallbacks
    def _callback(self, results):
        data = {}
        for success, result in results:
            if not success:
                error = result.getErrorMessage()
                self._events.append(dict(
                    severity=4,
                    summary='oVirt error: %s' % error,
                    eventKey='ovirt_failure',
                    eventClassKey='ovirt_error',
                    ))

                self._print_output()
                os._exit(1)
            #result_to_json
            #data.update(result)
            data.setdefault(result.tag, []).append(result)

        if 'events' in data.keys():
            self._events.extend(
                self._process_events(data['events']))

        if 'storage_domain' in data.keys():
            data['storage_domain']

        deferred_statistics = []
        if 'hosts' in data.keys():
            hosts = elementtree_to_dict(data['hosts'][0])['host']
            for host in hosts:
                deferred_statistics.append(self.client.request(host['link'][4]['href'].split('/api/')[1]))

        if 'vms' in data.keys():
            vms = elementtree_to_dict(data['vms'][0])['vm']
            for vm in vms:
                deferred_statistics.append(self.client.request(vm['link'][6]['href'].split('/api/')[1]))
                #Try except here!
                disk = yield self.client.request(vm['link'][0]['href'].split('/api/')[1])
                deferred_statistics.append(self.client.request(elementtree_to_dict(disk.getchildren()[0])['link']['href'].split('/api/')[1]))

        #DeferredLists do NOT need try/except handling when consumeErrors are True
        #We check its results for problems later.
        statistics_results = yield DeferredList(deferred_statistics, consumeErrors=True)

        processed_results = {}
        for success, result in statistics_results:
            if not success:
                error = result.getErrorMessage()
                self._events.append(dict(
                    severity=4,
                    summary='oVirt error: %s' % error,
                    eventKey='ovirt_failure',
                    eventClassKey='ovirt_error',
                    ))

                self._print_output()
                os._exit(1)

            for data in result.getchildren():
                key = None
                for component in ('host', 'vm', 'disk'):
                    try:
                        key = data.find(component).attrib['id']
                    except Exception:
                        pass

                def mName(metric):
                    return CamelCase(metric.find('name').text)

                def mValue(metric):
                        try:
                            return metric.find('values').find('value').find('datum').text
                        except Exception:
                            return None

                if mValue(data) is not None:
                    processed_results.setdefault(key, {})
                    processed_results[key][mName(data)] = mValue(data)

        self._values.update(processed_results)

        if len(self._values.keys()) > 0:
            self._save(self._values, key='values')

        self._events.append(dict(
            severity=0,
            summary='CloudStack polled successfully',
            eventKey='cloudstack_failure',
            eventClassKey='cloudstack_success',
            ))

        self._print_output()
        # We are not needing any more data, stop the reactor.
        if reactor.running:
            reactor.stop()

    def run(self):
        deferreds = []

        if self._collect_events:
            deferreds.extend((
                    self.client.listEvents(),
                    ))
        else:
            saved_values = self._saved_values()
            if saved_values is not None:
                self._values = saved_values
                self._events.append(dict(
                    severity=0,
                    summary='CloudStack polled successfully',
                    eventKey='cloudstack_failure',
                    eventClassKey='cloudstack_success',
                    ))
                self._print_output()
                return
            deferreds.extend((
                self.client.request('hosts'),
                self.client.request('vms'),
                ))
        DeferredList(deferreds, consumeErrors=True).addCallback(self._callback)

        reactor.run()

if __name__ == '__main__':
    usage = "Usage: %s <url> <username> <domain> <password>"
    url = username = domain = password = None

    try:
        url, username, domain, password = sys.argv[1:5]
    except ValueError:
        print >> sys.stderr, usage % sys.argv[0]
        sys.exit(1)

    events = False
    if len(sys.argv) > 5 and sys.argv[5] == 'events':
        events = True

    #time.sleep(random.randint(1, 5))
    poller = oVirtPoller(url, username, domain, password, collect_events=events)
    poller.run()
