# Copyright 2021 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys
import time
from unittest import TestCase, mock

from delfin.common import constants
from delfin.drivers.dell_emc.vnx.vnx_block import consts
from delfin.drivers.dell_emc.vnx.vnx_block.alert_handler import AlertHandler
from delfin.drivers.utils.tools import Tools

sys.modules['delfin.cryptor'] = mock.Mock()
from delfin import context
from delfin.drivers.dell_emc.vnx.vnx_block.navi_handler import NaviHandler
from delfin.drivers.dell_emc.vnx.vnx_block.navicli_client import NaviClient
from delfin.drivers.dell_emc.vnx.vnx_block.vnx_block import VnxBlockStorDriver

ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "dell_emc",
    "model": "vnx_block",
    "cli": {
        "host": "110.143.132.231",
        "port": 22,
        "username": "user",
        "password": "cGFzc3dvcmQ="
    }
}
AGENT_INFOS = """
    Agent Rev:           7.33.1 (0.38)
    Name:                K10
    Desc:
    Revision:            05.33.000.5.038
    Model:               VNX5400
    Serial No:           CETV00000001
"""
DOMAIN_INFOS = """
Node: APM00011111111
IP Address: 111.222.33.55
(Master)
Name: CX300I_33_55
Port: 80
Secure Port: 443
IP Address: 111.222.33.44
Name: CX300I_33_44
Port: 80
Secure Port: 443
"""
DISK_INFOS = """
        Bus 0 Enclosure 0  Disk 0
        State:                   Enabled
        Capacity:                54969
        """
POOL_INFOS = """
        Pool Name:  Pool 1
        Pool ID:  1
        Description:
        State:  Offline
        Status:  Storage Pool requires recovery. service provider(0x712d8518)
        User Capacity (GBs):  8583.732
        Consumed Capacity (GBs):  8479.780
        Available Capacity (GBs):  103.953
        Total Subscribed Capacity (GBs):  8479.780
        """
RAID_INFOS = """
        RaidGroup ID:                              0
        RaidGroup State:                           Valid_luns
        Raw Capacity (Blocks):                     1688426496
        Logical Capacity (Blocks):                 1688420352
        Free Capacity (Blocks,non-contiguous):     522260480
        """
LUN_INFOS = """
        LOGICAL UNIT NUMBER 239
        Name:  sun_data_VNX_2
        User Capacity (GBs):  9.000
        Consumed Capacity (GBs):  1.753
        Pool Name:  Migration_pool
        Current State:  Ready
        Status:  OK(0x0)
        Is Thin LUN:  Yes
        Is Compressed:  No
        """
GET_ALL_LUN_INFOS = """
        LOGICAL UNIT NUMBER 186
        Name                        LN_10G_01
        RAIDGroup ID:               1
        State:                      Bound
        LUN Capacity(Megabytes):    10240
        Is Thin LUN:                YES
        LOGICAL UNIT NUMBER 84
Name                        esx_208_raid_1
Read Requests:              81835
Write Requests:             41190
Blocks read:                4811166
Blocks written:             41230
Read cache hits:            77420
Read cache misses:          4415
Prefetched blocks:          0
Unused prefetched blocks:   0
Write cache hits:           41190
Forced flushes:             0
Read Hit Ratio:             94
Write Hit Ratio:            84
RAID Type:                  RAID5
RAIDGroup ID:               1
State:                      Bound
Stripe Crossing:            1277
Element Size:               128
Current owner:              SP A
Offset:                     N/A
Auto-trespass:              DISABLED
Auto-assign:                DISABLED
Write cache:                ENABLED
Read cache:                 ENABLED
Idle Threshold:             N/A
Idle Delay Time:            N/A
Write Aside Size:           0
Default Owner:              SP A
Rebuild Priority:           N/A
Verify Priority:            N/A
Prct Reads Forced Flushed:  N/A
Prct Writes Forced Flushed: N/A
Prct Rebuilt:               100
Prct Bound:                 N/A
LUN Capacity(Megabytes):    30720
LUN Capacity(Blocks):       62914560
UID:                        60:06:01:60:28:F0:36:00:11:EA:95:A0:B9:9F:EA:11
LUN Capacity(Stripes):      122880
Blocks Read SPA:            2378775  (optimal)
Blocks Read SPB:            2432391
Blocks Written SPA:         20714  (optimal)
Blocks Written SPB:         20516
Read Requests SPA:          40777  (optimal)
Read Requests SPB:          41058
Write Requests SPA:         20698  (optimal)
Write Requests SPB:         20492
LUN Busy Ticks SPA:         2511531  (optimal)
LUN Busy Ticks SPB:         2668802
LUN Idle Ticks SPA:         3302295952  (optimal)
LUN Idle Ticks SPB:         3317505096
Number of arrivals with non-zero queue:          16451
Sum queue lengths by arrivals:                   139481
Statistics logging start time:                   10/26/20 09:18:04
Statistics logging current time:                 10/26/20 15:43:36
Explicit Trespasses SPA:                 0
Explicit Trespasses SPB:                 0
Explicit Trespasses:                     0
Implicit Trespasses SPA:                 2
Implicit Trespasses SPB:                 0
Implicit Trespasses:                     2
Non-zero Request Count Arrivals SPA:           8135  (optimal)
Non-zero Request Count Arrivals SPB:           8316
Non-zero Request Count Arrivals:              16451
Sum of Oustanding Requests SPA:    69613  (optimal)
Sum of Oustanding Requests SPB:    69868
Sum of Oustanding Requests:      139481
Shrink State:                    N/A
Write cache Re-hits:        34645
Fast Write Count:           41190
Is Private:                 NO
Snapshots List:             Not Available
MirrorView Name if any:     Not Available
Address Offset:             813924352
Is Meta LUN:                NO
Is Thin LUN:                NO
Is Pool LUN:                NO
Is Snapshot Mount Point:    NO
LUN Idle Ticks:             2324833752
LUN Busy Ticks:             5180333
LUN Offline (Cache Dirty Condition):  NO
LU Storage Groups:          "Storage_esx_208"
Device Map:                 Valid
Average Read Time:            2862
Average Write Time:            29972
FAST Cache :             N/A
FAST Cache Read Hits:    N/A
FAST Cache Read Misses:  N/A
FAST Cache Write Hits:   N/A
FAST Cache Write Misses: N/A

LOGICAL UNIT NUMBER 220
Name                        LUN 220
Minimum latency reads N/A

RAID Type:                  N/A
RAIDGroup ID:               N/A
State:                      Bound
Stripe Crossing:            0
Element Size:               0
Current owner:              SP B
Offset:                     N/A
Auto-trespass:              DISABLED
Auto-assign:                DISABLED
Write cache:                ENABLED
Read cache:                 ENABLED
Idle Threshold:             N/A
Idle Delay Time:            N/A
Write Aside Size:           0
Default Owner:              SP B
Rebuild Priority:           N/A
Verify Priority:            N/A
Prct Reads Forced Flushed:  N/A
Prct Writes Forced Flushed: N/A
Prct Rebuilt:               100
Prct Bound:                 N/A
LUN Capacity(Megabytes):    16384
LUN Capacity(Blocks):       33554432
UID:                        60:06:01:60:28:F0:36:00:53:1A:3A:E7:33:89:EA:11
LUN Capacity(Stripes):      N/A
Shrink State:                    N/A
Is Private:                 NO
Snapshots List:             Not Available
MirrorView Name if any:     Not Available
Address Offset:             N/A
Is Meta LUN:                NO
Is Thin LUN:                YES
Is Pool LUN:                YES
Is Snapshot Mount Point:    NO
LUN Idle Ticks:             N/A
LUN Busy Ticks:             N/A
LUN Offline (Cache Dirty Condition):  N/A
LU Storage Groups:
Device Map:                 Valid
Average Read Time:            0
Average Write Time:            0
FAST Cache :             N/A
FAST Cache Read Hits:    N/A
FAST Cache Read Misses:  N/A
FAST Cache Write Hits:   N/A
FAST Cache Write Misses: N/A

        """
CER_INFOS = """
-----------------------------
Subject:CN=TrustedRoot,C=US,ST=MA,L=Hopkinton,EMAIL=rsa@emc.com,OU=CSP,O=RSA
Issuer:1.1.1.1
Serial#: 00d8280b0c863f6d4e
Valid From: 20090407135111Z
Valid To: 20190405135111Z
-----------------------------
Subject:CN=TrustedRoot,C=US,ST=MA,L=Hopkinton,EMAIL=rsa@emc.com,OU=CSP,O=RSA
Issuer:110.143.132.231
Serial#: 00d8280b0c863f6d4e
Valid From: 20090407135111Z
Valid To: 20190405135111Z
        """

DISK_DATAS = """
        Bus 0 Enclosure 0  Disk 0
        Vendor Id:               HITACHI
        Product Id:              HUC10906 CLAR600
        Product Revision:        C430
        Type:                    193: RAID5 129: RAID5 146: RAID5 151: RAID5
        State:                   Enabled
        Hot Spare:               N/A
        Serial Number:           KSJEX35J
        Capacity:                549691
        Number of Reads:         14684285
        Number of Writes:        10844109
        Number of Luns:          10
        Raid Group ID:           0
        Clariion Part Number:    DG118032933
        Request Service Time:    N/A
        Read Requests:           14684285
        Write Requests:          10844109
        Kbytes Read:             550362331
        Kbytes Written:          481080832
        Stripe Boundary Crossing: 145505
        Drive Type:              SAS
        Current Speed: 6Gbps
        """
SP_DATAS = """

SP A

Cabinet:             DPE9
Signature For The SP:          3600485
Signature For The Peer SP:     3600424
Revision Number For The SP:    05.33.000.5.038
Serial Number For The SP:      CF2Z7134700101
Memory Size For The SP:        16384
SP SCSI ID if Available:       0

SP B

Cabinet:             DPE9
Signature For The SP:          3600424
Signature For The Peer SP:     3600485
Revision Number For The SP:    05.33.000.5.038
Serial Number For The SP:      CF2Z7134700040
Memory Size For The SP:        16384
SP SCSI ID if Available:       0


"""
RESUME_DATAS = """
Storage Processor A
  CPU Module
    EMC Serial Number:               CF2Z7134700101
    Assembly Name:                   JFSP 1.8GHZ 4C CPU GEN3

Storage Processor B
  CPU Module
    EMC Serial Number:               CF2Z7134700040
    Assembly Name:                   JFSP 1.8GHZ 4C CPU GEN3
"""
PORT_DATAS = """
Information about each SPPORT:

SP Name:             SP A
SP Port ID:          6
SP UID:              50:06:01:60:88:60:24:1E:50:06:01:66:08:60:24:1E
Link Status:         Up
Port Status:         Online
Switch Present:      YES
Switch UID:          10:00:C4:F5:7C:20:05:80:20:0E:C4:F5:7C:20:05:80
SP Source ID:        1773056
ALPA Value:         0
Speed Value :         8Gbps
Auto Negotiable :     YES
Available Speeds:
2Gbps
4Gbps
8Gbps
Auto
Requested Value:      Auto
MAC Address:         Not Applicable
SFP State:           Online
Reads:               510068560
Writes:              331050079
Blocks Read:         1504646456
Blocks Written:      236376118
Queue Full/Busy:     12246
I/O Module Slot:     3
Physical Port ID:    0
"""
BUS_PORT_DATAS = """

Bus 0

Current Speed: 6Gbps.
Available Speeds:
              3Gbps.
              6Gbps.

SPA SFP State: N/A
SPB SFP State: N/A

I/O Module Slot: Base Module
Physical Port ID: 0
Port Combination In Use: No



SPA Connector State: None
SPB Connector State: None

"""
BUS_PORT_STATE_DATAS = """
Information about each I/O module(s) on SPA:

SP ID: A
I/O Module Slot: Base Module
I/O Module Type: SAS
I/O Module State: Present
I/O Module Substate: Good
I/O Module Power state: On
I/O Carrier: No

Information about each port on this I/O module:
Physical Port ID: 0
Port State: Enabled
Physical Port ID: 1
Port State: Missing
Information about each I/O module(s) on SPB:

SP ID: B
I/O Module Slot: Base Module
I/O Module Type: SAS
I/O Module State: Present
I/O Module Substate: Good
I/O Module Power state: On
I/O Carrier: No

Information about each port on this I/O module:
Physical Port ID: 0
Port State: Enabled
Physical Port ID: 1
Port State: Missing
"""
ISCSI_PORT_DATAS = """
SP: A
Port ID: 4
Port WWN: iqn.1992-04.com.emc:cx.apm00093300877.a4
iSCSI Alias: 0877.a4
IP Address: 172.20.1.140
Subnet Mask: 255.255.255.0
Gateway Address: 172.20.1.1
Initiator Authentication: Not Available

SP: A
Port ID: 5
Port WWN: iqn.1992-04.com.emc:cx.apm00093300877.a5
iSCSI Alias: 0877.a5

SP: A
Port ID: 6
Port WWN: iqn.1992-04.com.emc:cx.apm00093300877.a6
iSCSI Alias: 0877.a6
IP Address: 172.20.2.140
Subnet Mask: 255.255.255.0
Gateway Address: 172.20.2.1
Initiator Authentication: Not Available

SP: A
Port ID: 7
Port WWN: iqn.1992-04.com.emc:cx.apm00093300877.a7
iSCSI Alias: 0877.a7

SP: B
Port ID: 4
Port WWN: iqn.1992-04.com.emc:cx.apm00093300877.b4
iSCSI Alias: 0877.b4
IP Address: 172.20.1.141
Subnet Mask: 255.255.255.0
Gateway Address: 172.20.1.1
Initiator Authentication: Not Available

SP: B
Port ID: 5
Port WWN: iqn.1992-04.com.emc:cx.apm00093300877.b5
iSCSI Alias: 0877.b5

SP: B
Port ID: 6
Port WWN: iqn.1992-04.com.emc:cx.apm00093300877.b6
iSCSI Alias: 0877.b6
IP Address: 172.20.2.141
Subnet Mask: 255.255.255.0
Gateway Address: 172.20.2.1
Initiator Authentication: Not Available

SP: B
Port ID: 7
Port WWN: iqn.1992-04.com.emc:cx.apm00093300877.b7
iSCSI Alias: 0877.b7

SP: B
Port ID: 9
Port WWN: 50:06:01:60:BB:20:13:0D:50:06:01:69:3B:24:13:0D
iSCSI Alias: N/A
IP Address: N/A
Subnet Mask: N/A
Gateway Address: N/A
Initiator Authentication: N/A

SP: A
Port ID: 8
Port WWN: 50:06:01:60:BB:20:13:0D:50:06:01:60:3B:24:13:0D
iSCSI Alias: N/A
IP Address: N/A
Subnet Mask: N/A
Gateway Address: N/A
Initiator Authentication: N/A

SP: A
Port ID: 9
Port WWN: 50:06:01:60:BB:20:13:0D:50:06:01:61:3B:24:13:0D
iSCSI Alias: N/A
IP Address: N/A
Subnet Mask: N/A
Gateway Address: N/A
Initiator Authentication: N/A

SP: B
Port ID: 8
Port WWN: 50:06:01:60:BB:20:13:0D:50:06:01:68:3B:24:13:0D
iSCSI Alias: N/A
IP Address: N/A
Subnet Mask: N/A
Gateway Address: N/A
Initiator Authentication: N/A
"""
IO_PORT_CONFIG_DATAS = """
SP ID :  A
I/O Module Slot :  3
I/O Module Type :  Fibre Channel
I/O Module State :  Present

SP ID :  A
I/O Module Slot :  Base Module
I/O Module Type :  SAS

SP ID :  B
I/O Module Slot :  Base Module
I/O Module Type :  SAS
"""

SP_DATAS_DETAILL = """


Server IP Address:       8.44.162.249
Agent Rev:           7.33.1 (0.38)


SP Information
--------------


Storage Processor:                  SP B
Storage Processor Network Name:     B-IMAGE
Storage Processor IP Address:       8.44.162.249
Storage Processor Subnet Mask:      255.255.192.0
Storage Processor Gateway Address:  8.44.128.1
Storage Processor IPv6 Mode:               Not Supported
Management Port Settings:
Link Status:                        Link-Up
Current Speed:                      1000Mbps/full duplex
Requested Speed:                    Auto
Auto-Negotiate:                     YES
Capable Speeds:                     1000Mbps half/full duplex
                                    10Mbps half/full duplex
                                    100Mbps half/full duplex
System Fault LED:              ON
Statistics Logging:            ON
SP Read Cache State            Enabled
SP Write Cache State           Enabled
Max Requests:                  N/A
Average Requests:              N/A
Hard errors:                   N/A
Total Reads:                   950598365
Total Writes:                  492822033
Prct Busy:                     15.1
Prct Idle:                     84.8
System Date:                   03/30/2021
Day of the week:               Tuesday
System Time:                   11:40:23
Read_requests:                 950598365
Write_requests:                492822033
Blocks_read:                   310450016065
Blocks_written:                108176671659
Sum_queue_lengths_by_arrivals: 0
Arrivals_to_non_zero_queue:    0
Hw_flush_on:                   N/A
Idle_flush_on:                 N/A
Lw_flush_off:                  N/A
Write_cache_flushes:           594830819
Write_cache_blocks_flushed:    3284869527
Internal bus 1 busy ticks:     N/A
Internal bus 1 idle ticks:     N/A
Internal bus 2 busy ticks:     N/A
Internal bus 2 idle ticks:     N/A
Internal bus 3 busy ticks:     N/A
Internal bus 3 idle ticks:     N/A
Internal bus 4 busy ticks:     N/A
Internal bus 4 idle ticks:     N/A
Internal bus 5 busy ticks:     N/A
Internal bus 5 idle ticks:     N/A
Controller busy ticks:         2199758
Controller idle ticks:         12361970
Serial Number For The SP:      CF2Z7134700040


"""

AGENT_RESULT = {
    'agent_rev': '7.33.1 (0.38)',
    'name': 'K10',
    'desc': '',
    'revision': '05.33.000.5.038',
    'model': 'VNX5400',
    'serial_no': 'CETV00000001'
}
STORAGE_RESULT = {
    'name': 'APM00011111111',
    'vendor': 'DELL EMC',
    'model': 'VNX5400',
    'status': 'normal',
    'serial_number': 'CETV00000001',
    'firmware_version': '05.33.000.5.038',
    'total_capacity': 10081183274631,
    'raw_capacity': 57639174144,
    'used_capacity': 9702168298782,
    'free_capacity': 379016049590
}
DOMAIN_RESULT = [
    {
        'node': 'APM00011111111',
        'ip_address': '111.222.33.55',
        'master': 'True',
        'name': 'CX300I_33_55',
        'port': '80',
        'secure_port': '443'
    }]
POOLS_RESULT = [
    {
        'name': 'Pool 1',
        'storage_id': '12345',
        'native_storage_pool_id': '1',
        'description': '',
        'status': 'offline',
        'storage_type': 'block',
        'total_capacity': 9216712054407,
        'subscribed_capacity': 9105094444318,
        'used_capacity': 9105094444318,
        'free_capacity': 111618683830
    }]
RAID_RESULT = [
    {
        'raidgroup_id': '0',
        'raidgroup_state': 'Valid_luns',
        'raw_capacity_blocks': '1688426496',
        'logical_capacity_blocks': '1688420352',
        'free_capacity_blocks,non-contiguous': '522260480'
    }]
ALL_LUN_RESULT = [
    {
        'logical_unit_number': '186',
        'name': 'LN_10G_01',
        'raidgroup_id': '1',
        'state': 'Bound',
        'lun_capacitymegabytes': '10240',
        'is_thin_lun': 'YES'
    }]
POOLS_ANALYSE_RESULT = [{
    'pool_name': 'Pool 1',
    'pool_id': '1',
    'description': '',
    'state': 'Offline',
    'status': 'Storage Pool requires recovery. service provider(0x712d8518)',
    'user_capacity_gbs': '8583.732',
    'consumed_capacity_gbs': '8479.780',
    'available_capacity_gbs': '103.953',
    'total_subscribed_capacity_gbs': '8479.780'
}]
VOLUMES_RESULT = [
    {
        'name': 'sun_data_VNX_2',
        'storage_id': '12345',
        'status': 'normal',
        'native_volume_id': '239',
        'native_storage_pool_id': '',
        'type': 'thin',
        'total_capacity': 9663676416,
        'used_capacity': 1882269417,
        'free_capacity': 7781406998,
        'compressed': False,
        'wwn': None
    }]
ALERTS_RESULT = [
    {
        'alert_id': '0x76cc',
        'alert_name': 'Navisphere Agent, version 7.33',
        'severity': 'Critical',
        'category': 'Fault',
        'type': 'EquipmentAlarm',
        'occur_time': 1585114217000,
        'description': 'Navisphere Agent, version 7.33',
        'resource_type': 'Storage',
        'match_key': 'b969bbaa22b62ebcad4074618cc29b94'
    }]
ALERT_RESULT = {
    'alert_id': '0x761f',
    'alert_name': 'Unisphere can no longer manage',
    'severity': 'Critical',
    'category': 'Fault',
    'type': 'EquipmentAlarm',
    'occur_time': 1614310456716,
    'description': 'Unisphere can no longer manage',
    'resource_type': 'Storage',
    'match_key': '8e97fe0af779d78bad8f2de52e15c65c'
}
DISK_RESULT = [
    {
        'name': 'Bus 0 Enclosure 0  Disk 0',
        'storage_id': '12345',
        'native_disk_id': 'Bus0Enclosure0Disk0',
        'serial_number': 'KSJEX35J',
        'manufacturer': 'HITACHI',
        'model': 'HUC10906 CLAR600',
        'firmware': 'C430',
        'speed': None,
        'capacity': 576392790016,
        'status': 'normal',
        'physical_type': 'sas',
        'logical_type': 'unknown',
        'health_score': None,
        'native_disk_group_id': None,
        'location': 'Bus 0 Enclosure 0  Disk 0'
    }]
SP_RESULT = [
    {
        'name': 'SP A',
        'storage_id': '12345',
        'native_controller_id': '3600485',
        'status': 'normal',
        'location': None,
        'soft_version': '05.33.000.5.038',
        'cpu_info': 'JFSP 1.8GHZ 4C CPU GEN3',
        'memory_size': '17179869184'
    },
    {
        'name': 'SP B',
        'storage_id': '12345',
        'native_controller_id': '3600424',
        'status': None,
        'location': None,
        'soft_version': '05.33.000.5.038',
        'cpu_info': 'JFSP 1.8GHZ 4C CPU GEN3',
        'memory_size': '16777216'
    }]
PORT_RESULT = [
    {
        'name': 'A-6',
        'storage_id': '12345',
        'native_port_id': 'A-6',
        'location': 'Slot A3,Port 0',
        'connection_status': 'connected',
        'health_status': 'normal',
        'type': 'fc',
        'logical_type': None,
        'speed': 8000000000,
        'max_speed': 8000000000,
        'native_parent_id': None,
        'wwn': '50:06:01:60:88:60:24:1E:50:06:01:66:08:60:24:1E',
        'mac_address': None,
        'ipv4': '172.20.2.140',
        'ipv4_mask': '255.255.255.0',
        'ipv6': None,
        'ipv6_mask': None
    }]

METRICS_RESULT = [
    constants.metric_struct(name='iops', labels={
        'storage_id': '12345',
        'resource_type': 'controller',
        'resource_id': '3600424',
        'type': 'RAW',
        'unit': 'IOPS'
    }, values={1628472900000: 1443420398}),
    constants.metric_struct(name='readIops', labels={
        'storage_id': '12345',
        'resource_type': 'controller',
        'resource_id': '3600424',
        'type': 'RAW',
        'unit': 'IOPS'
    }, values={1628472900000: 950598365}),
    constants.metric_struct(name='iops', labels={
        'storage_id': '12345',
        'resource_type': 'volume',
        'resource_id': '84',
        'type': 'RAW',
        'unit': 'IOPS'
    }, values={1628472900000: 123025}),
    constants.metric_struct(name='iops', labels={
        'storage_id': '12345',
        'resource_type': 'port',
        'resource_id': 'A-6',
        'type': 'RAW',
        'unit': 'IOPS'
    }, values={1628472900000: 841118639}),
    constants.metric_struct(name='iops', labels={
        'storage_id': '12345',
        'resource_type': 'disk',
        'resource_id': 'Bus0Enclosure0Disk0',
        'type': 'RAW',
        'unit': 'IOPS'
    }, values={1628472900000: 25528394})
]


def create_driver():
    NaviHandler.login = mock.Mock(return_value={"05.33.000.5.038_test"})
    return VnxBlockStorDriver(**ACCESS_INFO)


class TestVnxBlocktorageDriver(TestCase):
    driver = create_driver()

    def test_init(self):
        NaviHandler.login = mock.Mock(return_value="05.33.000.5.038_test")
        vnx = VnxBlockStorDriver(**ACCESS_INFO)
        self.assertEqual(vnx.version, "05.33.000.5.038_test")

    def test_get_storage(self):
        NaviClient.exec = mock.Mock(
            side_effect=[DOMAIN_INFOS, AGENT_INFOS, DISK_INFOS, POOL_INFOS,
                         RAID_INFOS])
        storage = self.driver.get_storage(context)
        self.assertDictEqual(storage, STORAGE_RESULT)

    def test_get_pools(self):
        NaviClient.exec = mock.Mock(side_effect=[POOL_INFOS, RAID_INFOS])
        pools = self.driver.list_storage_pools(context)
        self.assertDictEqual(pools[0], POOLS_RESULT[0])

    def test_get_volumes(self):
        NaviClient.exec = mock.Mock(
            side_effect=[LUN_INFOS, POOL_INFOS, GET_ALL_LUN_INFOS])
        volumes = self.driver.list_volumes(context)
        self.assertDictEqual(volumes[0], VOLUMES_RESULT[0])

    def test_get_alerts(self):
        with self.assertRaises(Exception) as exc:
            self.driver.list_alerts(context, None)
        self.assertIn('Driver API list_alerts() is not Implemented',
                      str(exc.exception))

    def test_parse_alert(self):
        alert = {
            '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.1981.0.6',
            '1.3.6.1.4.1.1981.1.4.3': 'A-CETV00000001',
            '1.3.6.1.4.1.1981.1.4.4': 'K10',
            '1.3.6.1.4.1.1981.1.4.5': '761f',
            '1.3.6.1.4.1.1981.1.4.6': 'Unisphere can no longer manage',
            '1.3.6.1.4.1.1981.1.4.7': 'VNX5400'
        }
        alert = self.driver.parse_alert(context, alert)
        ALERT_RESULT['occur_time'] = alert['occur_time']
        self.assertDictEqual(alert, ALERT_RESULT)

    def test_cli_res_to_dict(self):
        navi_handler = NaviHandler(**ACCESS_INFO)
        agent_re = navi_handler.cli_res_to_dict(AGENT_INFOS)
        self.assertDictEqual(agent_re, AGENT_RESULT)

    def test_cli_res_to_list(self):
        navi_handler = NaviHandler(**ACCESS_INFO)
        re_list = navi_handler.cli_res_to_list(POOL_INFOS)
        self.assertDictEqual(re_list[0], POOLS_ANALYSE_RESULT[0])

    def test_cli_domain_to_dict(self):
        navi_handler = NaviHandler(**ACCESS_INFO)
        re_list = navi_handler.cli_domain_to_dict(DOMAIN_INFOS)
        self.assertDictEqual(re_list[0], DOMAIN_RESULT[0])

    def test_cli_lun_to_list(self):
        navi_handler = NaviHandler(**ACCESS_INFO)
        re_list = navi_handler.cli_lun_to_list(GET_ALL_LUN_INFOS)
        self.assertDictEqual(re_list[0], ALL_LUN_RESULT[0])

    @mock.patch.object(NaviClient, 'exec')
    def test_init_cli(self, mock_exec):
        mock_exec.return_value = 'test'
        navi_handler = NaviHandler(**ACCESS_INFO)
        re = navi_handler.navi_exe('abc')
        self.assertEqual(re, 'test')
        self.assertEqual(mock_exec.call_count, 1)

    @mock.patch.object(NaviClient, 'exec')
    def test_remove_cer(self, mock_exec):
        navi_handler = NaviHandler(**ACCESS_INFO)
        navi_handler.remove_cer()
        self.assertEqual(mock_exec.call_count, 1)

    def test_err_cli_res_to_dict(self):
        with self.assertRaises(Exception) as exc:
            navi_handler = NaviHandler(**ACCESS_INFO)
            navi_handler.cli_res_to_dict({})
        self.assertIn('arrange resource info error', str(exc.exception))

    def test_err_cli_res_to_list(self):
        with self.assertRaises(Exception) as exc:
            navi_handler = NaviHandler(**ACCESS_INFO)
            navi_handler.cli_res_to_list({})
        self.assertIn('cli resource to list error', str(exc.exception))

    @mock.patch.object(time, 'mktime')
    def test_time_str_to_timestamp(self, mock_mktime):
        tools = Tools()
        time_str = '03/26/2021 14:25:36'
        mock_mktime.return_value = 1616739936
        re = tools.time_str_to_timestamp(time_str, consts.TIME_PATTERN)
        self.assertEqual(1616739936000, re)

    @mock.patch.object(time, 'strftime')
    def test_timestamp_to_time_str(self, mock_strftime):
        tools = Tools()
        mock_strftime.return_value = '03/26/2021 14:25:36'
        timestamp = 1616739936000
        re = tools.timestamp_to_time_str(timestamp, consts.TIME_PATTERN)
        self.assertEqual('03/26/2021 14:25:36', re)

    def test_cli_exec(self):
        with self.assertRaises(Exception) as exc:
            command_str = 'abc'
            NaviClient.exec(command_str)
        self.assertIn('Component naviseccli could not be found',
                      str(exc.exception))

    def test_analyse_cer(self):
        re_map = {
            '1.1.1.1': {
                'subject': 'CN=TrustedRoot,C=US,ST=MA,L=Hopkinton,'
                           'EMAIL=rsa@emc.com,OU=CSP,O=RSA',
                'issuer': '1.1.1.1',
                'serial#': '00d8280b0c863f6d4e',
                'valid_from': '20090407135111Z',
                'valid_to': '20190405135111Z'
            }
        }
        navi_handler = NaviHandler(**ACCESS_INFO)
        cer_map = navi_handler.analyse_cer(CER_INFOS, host_ip='1.1.1.1')
        self.assertDictEqual(cer_map, re_map)

    def test_analyse_cer_exception(self):
        with self.assertRaises(Exception) as exc:
            navi_handler = NaviHandler(**ACCESS_INFO)
            navi_handler.analyse_cer(CER_INFOS)
        self.assertIn('arrange cer info error', str(exc.exception))

    def test_get_resources_info_exception(self):
        with self.assertRaises(Exception) as exc:
            NaviClient.exec = mock.Mock(side_effect=[LUN_INFOS])
            navi_handler = NaviHandler(**ACCESS_INFO)
            navi_handler.get_resources_info('abc', None)
        self.assertIn('object is not callable', str(exc.exception))

    def test_parse_alert_exception(self):
        with self.assertRaises(Exception) as exc:
            AlertHandler.parse_alert(None)
        self.assertIn('The results are invalid', str(exc.exception))

    def test_clear_alert(self):
        self.driver.clear_alert(None, None)

    def test_remove_trap_config(self):
        self.driver.remove_trap_config(None, None)

    def test_get_disks(self):
        NaviClient.exec = mock.Mock(return_value=DISK_DATAS)
        disks = self.driver.list_disks(context)
        self.assertDictEqual(disks[0], DISK_RESULT[0])

    def test_get_controllers(self):
        NaviClient.exec = mock.Mock(side_effect=[SP_DATAS, RESUME_DATAS])
        controllers = self.driver.list_controllers(context)
        self.assertDictEqual(controllers[0], SP_RESULT[0])

    def test_get_ports(self):
        NaviClient.exec = mock.Mock(
            side_effect=[IO_PORT_CONFIG_DATAS, ISCSI_PORT_DATAS, PORT_DATAS,
                         BUS_PORT_DATAS, BUS_PORT_STATE_DATAS])
        ports = self.driver.list_ports(context)
        self.assertDictEqual(ports[0], PORT_RESULT[0])

    def test_get_perf_metrics(self):
        driver = create_driver()
        resource_metrics = {
            'controller': [
                'iops', 'readIops', 'writeIops',
                'throughput', 'readThroughput', 'writeThroughput',
                'responseTime'
            ],
            'volume': [
                'iops', 'readIops', 'writeIops',
                'throughput', 'readThroughput', 'writeThroughput',
                'responseTime',
                'cacheHitRatio', 'readCacheHitRatio', 'writeCacheHitRatio',
                'ioSize', 'readIoSize', 'writeIoSize',
            ],
            'port': [
                'iops', 'readIops', 'writeIops',
                'throughput', 'readThroughput', 'writeThroughput',
                'responseTime'
            ],
            'disk': [
                'iops', 'readIops', 'writeIops',
                'throughput', 'readThroughput', 'writeThroughput',
                'responseTime'
            ]
        }
        start_time = 1628472280000
        end_time = 1628472900000
        NaviClient.exec = mock.Mock(
            side_effect=[DOMAIN_INFOS, SP_DATAS, SP_DATAS_DETAILL,
                         SP_DATAS_DETAILL, GET_ALL_LUN_INFOS, PORT_DATAS,
                         DISK_DATAS])
        metrics = driver.collect_perf_metrics(context, '12345',
                                              resource_metrics, start_time,
                                              end_time)
        self.assertEqual(metrics[0], METRICS_RESULT[0])
        self.assertEqual(metrics[13], METRICS_RESULT[2])
        self.assertEqual(metrics[23], METRICS_RESULT[3])
        self.assertEqual(metrics[29], METRICS_RESULT[4])

    def test_get_capabilities(self):
        cap = VnxBlockStorDriver.get_capabilities(context)
        self.assertIsNotNone(cap.get('resource_metrics'))
        self.assertIsNotNone(cap.get('resource_metrics').get('controller'))
        self.assertIsNotNone(cap.get('resource_metrics').get('volume'))
        self.assertIsNotNone(cap.get('resource_metrics').get('port'))
        self.assertIsNotNone(cap.get('resource_metrics').get('disk'))
