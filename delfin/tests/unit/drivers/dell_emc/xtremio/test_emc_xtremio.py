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
from unittest import TestCase, mock

sys.modules['delfin.cryptor'] = mock.Mock()
from requests import Session

from delfin import context
from delfin.drivers.dell_emc.xtremio import consts
from delfin.drivers.dell_emc.xtremio.rest_handler import RestHandler
from delfin.drivers.dell_emc.xtremio.xtremio import XtremioStorDriver


class Request:
    def __init__(self):
        self.environ = {'delfin.context': context.RequestContext()}
        pass


ACCESS_INFO = {
    "storage_id": "12345",
    "rest": {
        "host": "110.143.132.231",
        "port": "443",
        "username": "username",
        "password": "cGFzc3dvcmQ="
    },
    "vendor": "dell_emc",
    "model": "xtremio"
}
GET_CLUSTER = {
    "clusters": [{
        "href": "https://vxms-xbrickdrm919/api/json/v3/types/clusters/"
                "7e0bbd4b7d69477ab32e2953636a70de",
        "name": "xbrickdrm919"
    }]
}
GET_CLUSTER_DETAIL = {
    "content": {
        "obj-severity": "major",
        "sys-health-state": "healthy",
        "name": "xbrickdrm1652",
        "sys-sw-version": "6.2.0-61_X2",
        "index": 1,
        "ud-ssd-space-in-use": "36317455",
        "ud-ssd-space": "5358306912",
        "size-and-capacity": "1 Bricks & 6TB",
        "compression-mode": "enabled",
        "sys-psnt-serial-number": "XIO00171313881",
        "vol-size": "16052166656"
    }
}
GET_SSD = {
    "ssds": [{
        "href": "https://vxms-xbrickdrm1652/api/json/v3/types/ssds/"
                "ca9e25ad56dd4ee6ac7709ec2646a72b",
        "name": "wwn-0x500003970c89f855",
        "sys-name": "xbrickdrm1652"
    }]
}
GET_SSD_DETAIL = {
    "content": {
        "ssd-size-in-kb": 1875902464
    }
}
GET_VOLUME = {
    "volumes": [{
        "href": "https://vxms-xbrickdrm1652/api/json/v3/types/volumes/"
                "bd5ca31a6af240318e0b6ac5e49b1629",
        "name": "volspider1",
        "sys-name": "xbrick224-rename"
    }]
}
GET_VOLUME_DETAIL = {
    "content": {
        "obj-severity": "information",
        "name": "ReadOnlyPrefillObj_643.1535119200432-1",
        "sys-index": 1,
        "index": 2000729,
        "naa-name": "",
        "vol-size": "10240",
        "logical-space-in-use": "0"
    }
}
GET_ALERT = {
    "alerts": [{
        "href": "https://vxms-xbrickdrm919/api/json/v3/types/alerts/"
                "07ff05ddd3654536a1fc25a0a805918f",
        "name": ""
    }]
}
GET_ALERT_DETAIL = {
    "content": {
        "assoc-obj-name": "20:01:00:0e:1e:c2:c9:3c",
        "description": "Initiator has non-redundant path connectivity",
        "class-name": "Initiator",
        "alert-code": "2400203",
        "guid": "f171f554430746798496eb947da10147",
        "name": "",
        "severity": "major",
        "alert-type": "alert_def_initiator_redundancy_state_non_redundant",
        "raise-time": "1517310529142"
    }
}
TRAP_INFO = {
    '1.3.6.1.4.1.1139.103.1.18.1.1': '123',
    '1.3.6.1.4.1.1139.30.1.1.1.5': 'major',
    '1.3.6.1.4.1.1139.30.1.1.1.8': 'test alert trap',
    '1.3.6.1.4.1.1139.30.1.1.1.11': '500001',
    '1.3.6.1.4.1.1139.30.1.1.1.15': 'acknowledged',
    '1.3.6.1.4.1.1139.30.1.1.1.9': '2020/11/20 14:10:10',
    '1.3.6.1.4.1.1139.30.1.1.1.4': 'ssd:01'
}
GET_CONTROLLER = {
    "storage-controllers": [
        {
            "href": "https://vxms-xbrickdrm1652/api/json/v3/types/"
                    "storage-controllers/a662e77f21854989be01f4d03eb69bf4",
            "name": "X1-SC1",
            "sys-name": "xbrickdrm1652"
        }
    ]
}
GET_CONTROLLER_DETAIL = {
    "content": {
        "node-guid": "001e67f38d5100000000000000000000",
        "obj-severity": "information",
        "node-health-state": "healthy",
        "os-version": "Xtremio OS release 6.1.0-96_X2",
        "name": "X1-SC1",
        "index": 1,
        "node-id": ["953c29f0d39449de8732531e3786b02c", "X1-SC1", 1],
        "brick-index": 1
    }
}
GET_DISK = {
    "ssds": [
        {
            "href": "https://vxms-xbrickdrm1652/api/json/v3/types/"
                    "ssds/ca9e25ad56dd4ee6ac7709ec2646a72b",
            "name": "wwn-0x500003970c89f855",
            "sys-name": "xbrickdrm1652"
        }
    ]
}
GET_DISK_DETAIL = {
    "content": {
        "ssd-size": "1875902464",
        "slot-num": 17,
        "fru-lifecycle-state": "healthy",
        "serial-number": "0x5000cca06c4a2b00",
        "brick-name": "X1",
        "name": "wwn-0x5000cca06c4a2b00",
        "model-name": "HGST HUSMR119CLAR1920",
        "index": 18,
        "fw-version": "C1T6"
    }
}
GET_PORT = {
    "targets": [
        {
            "href": "https://vxms-xbrickdrm1652/api/json/v3/types/"
                    "targets/e374cf48b95b4ddb913dd3527a642a88",
            "name": "X1-SC1-fc1",
            "sys-name": "xbrick224-rename"
        },
        {
            "href": "https://vxms-xbrickdrm1652/api/json/v3/types/"
                    "targets/07e07a2fedf444d7b5c16590be8d4334",
            "name": "X1-SC1-target1-rename",
            "sys-name": "xbrickdrm1652"
        }
    ]
}
GET_PORT_DETAIL = {
    "content": {
        "port-mac-addr": "a4bf010012c7",
        "port-state": "down",
        "port-type": "eth_replication",
        "port-address": "a4:bf:01:00:12:c7",
        "port-health-level": "level_1_clear",
        "port-speed": "10Gb",
        "name": "X1-SC2-target5",
        "index": 10
    }
}

clusters_list_result = {
    'clusters': [{
        'href': 'https://vxms-xbrickdrm919/api/json/v3/types/clusters/'
                '7e0bbd4b7d69477ab32e2953636a70de',
        'name': 'xbrickdrm919'
    }]
}
storage_result = {
    'name': 'xbrickdrm1652',
    'vendor': 'DELL EMC',
    'model': '1 Bricks & 6TB',
    'status': 'normal',
    'serial_number': 'XIO00171313881',
    'firmware_version': '6.2.0-61_X2',
    'total_capacity': 5486906277888,
    'raw_capacity': 1920924123136,
    'used_capacity': 37189073920,
    'free_capacity': 5449717203968
}
volume_result = [{
    'name': 'ReadOnlyPrefillObj_643.1535119200432-1',
    'storage_id': '12345',
    'status': 'normal',
    'native_volume_id': '2000729',
    'wwn': '',
    'type': 'thin',
    'total_capacity': 10240,
    'used_capacity': 0,
    'free_capacity': 10240
}]
alert_result = [{
    'location': 'Initiator--20:01:00:0e:1e:c2:c9:3c',
    'alert_id': '2400203',
    'sequence_number': 'f171f554430746798496eb947da10147',
    'description': 'Initiator has non-redundant path connectivity',
    'alert_name': 'alert_def_initiator_redundancy_state_non_redundant',
    'resource_type': 'Storage',
    'occur_time': 1517310529142000,
    'category': 'Fault',
    'type': 'EquipmentAlarm',
    'severity': 'Major'
}]
trap_result = {
    'alert_id': '500001',
    'alert_name': 'test alert trap',
    'severity': 'Major',
    'sequence_number': '123',
    'category': 'Fault',
    'type': 'EquipmentAlarm',
    'occur_time': 1614736843000,
    'description': 'test alert trap',
    'resource_type': 'Storage'
}
controller_result = [{
    'name': 'X1-SC1',
    'storage_id': '12345',
    'native_controller_id': 1,
    'status': 'normal',
    'location': None,
    'soft_version': 'Xtremio OS release 6.1.0-96_X2',
    'cpu_info': None,
    'memory_size': None
}]
disk_result = [
    {
        'name': 'wwn-0x5000cca06c4a2b00',
        'storage_id': '12345',
        'native_disk_id': 18,
        'serial_number': '0x5000cca06c4a2b00',
        'manufacturer': None,
        'model': 'HGST HUSMR119CLAR1920',
        'firmware': 'C1T6',
        'speed': None,
        'capacity': 1920924123136,
        'status': 'normal',
        'physical_type': 'flash',
        'logical_type': None,
        'health_score': None,
        'native_disk_group_id': None,
        'location': 'X-Brick:X1 Slot:17'
    }]
port_result = [
    {
        'name': 'X1-SC2-target5',
        'storage_id': '12345',
        'native_port_id': 10,
        'location': None,
        'connection_status': 'disconnected',
        'health_status': 'normal',
        'type': 'eth',
        'logical_type': None,
        'speed': 10000000000,
        'max_speed': None,
        'native_parent_id': None,
        'wwn': 'a4:bf:01:00:12:c7',
        'mac_address': 'a4bf010012c7',
        'ipv4': None,
        'ipv4_mask': None,
        'ipv6': None,
        'ipv6_mask': None
    }]


def create_driver():
    m = mock.MagicMock(status_code=200)
    with mock.patch.object(Session, 'request', return_value=m):
        m.raise_for_status.return_value = 200
        m.json.return_value = GET_CLUSTER
        return XtremioStorDriver(**ACCESS_INFO)


class TestXtremIOStorDriver(TestCase):
    driver = create_driver()

    @mock.patch.object(RestHandler, 'call')
    def test_login(self, mock_call):
        rest_handler = RestHandler(**ACCESS_INFO)
        rest_handler.login()
        self.assertEqual(mock_call.call_count, 1)

    def test_call_rest(self):
        m = mock.MagicMock(status_code=200)
        with mock.patch.object(Session, 'request', return_value=m):
            m.raise_for_status.return_value = 200
            m.json.return_value = GET_CLUSTER
            rest_handler = RestHandler(**ACCESS_INFO)
            cluster_list = rest_handler.call(consts.REST_CLUSTER_LIST_URL,
                                             method='GET')
            self.assertDictEqual(cluster_list, clusters_list_result)

    def test_get_storage(self):
        RestHandler.call = mock.Mock(side_effect=[
            GET_CLUSTER, GET_CLUSTER_DETAIL, GET_SSD, GET_SSD_DETAIL])
        storage = self.driver.get_storage(context)
        self.assertDictEqual(storage, storage_result)

    def test_list_volumes(self):
        RestHandler.call = mock.Mock(
            side_effect=[GET_CLUSTER, GET_CLUSTER_DETAIL, GET_VOLUME,
                         GET_VOLUME_DETAIL])
        volumes = self.driver.list_volumes(context)
        self.assertDictEqual(volumes[0], volume_result[0])

    def test_list_alerts(self):
        RestHandler.call = mock.Mock(
            side_effect=[GET_CLUSTER, GET_CLUSTER_DETAIL, GET_ALERT,
                         GET_ALERT_DETAIL])
        alerts = self.driver.list_alerts(context)
        self.assertDictEqual(alerts[0], alert_result[0])

    @mock.patch.object(RestHandler, 'remove_alert')
    def test_clear_alert(self, mock_remove_alert):
        RestHandler.call = mock.Mock(
            side_effect=[GET_CLUSTER, GET_CLUSTER_DETAIL, {}])
        self.driver.clear_alert(context, '1')
        self.assertEqual(mock_remove_alert.call_count, 1)

    def test_parse_alert(self):
        trap = self.driver.parse_alert(context, TRAP_INFO)
        trap_result['occur_time'] = trap['occur_time']
        self.assertDictEqual(trap, trap_result)

    @mock.patch.object(RestHandler, 'login')
    def test_reset_connection(self, mock_login):
        self.driver.reset_connection(context, **ACCESS_INFO)
        self.assertEqual(mock_login.call_count, 1)

    def test_list_controllers(self):
        RestHandler.call = mock.Mock(
            side_effect=[GET_CLUSTER, GET_CLUSTER_DETAIL, GET_CONTROLLER,
                         GET_CONTROLLER_DETAIL])
        controllers = self.driver.list_controllers(context)
        self.assertDictEqual(controllers[0], controller_result[0])

    def test_list_disks(self):
        RestHandler.call = mock.Mock(
            side_effect=[GET_CLUSTER, GET_CLUSTER_DETAIL, GET_DISK,
                         GET_DISK_DETAIL])
        disks = self.driver.list_disks(context)
        self.assertDictEqual(disks[0], disk_result[0])

    def test_list_ports(self):
        RestHandler.call = mock.Mock(
            side_effect=[GET_CLUSTER, GET_CLUSTER_DETAIL, GET_PORT,
                         GET_PORT_DETAIL, GET_PORT_DETAIL])
        ports = self.driver.list_ports(context)
        self.assertDictEqual(ports[0], port_result[0])
