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
import copy
import re

import six
from oslo_log import log
from oslo_utils import units

from delfin import exception
from delfin.common import constants
from delfin.drivers.dell_emc.vnx.vnx_block import consts
from delfin.drivers.utils.tools import Tools

LOG = log.getLogger(__name__)


class ComponentHandler(object):

    def __init__(self, navi_handler):
        self.navi_handler = navi_handler

    def get_storage(self):
        domain = self.navi_handler.get_domain()
        agent = self.navi_handler.get_agent()
        status = constants.StorageStatus.NORMAL
        raw_cap = self.handle_disk_capacity()
        pool_capacity = self.handle_pool_capacity()
        if domain and agent:
            result = {
                'name': domain[0].get('node'),
                'vendor': consts.EMCVNX_VENDOR,
                'model': agent.get('model'),
                'status': status,
                'serial_number': agent.get('serial_no'),
                'firmware_version': agent.get('revision'),
                'total_capacity': pool_capacity.get('total_capacity'),
                'raw_capacity': int(raw_cap),
                'used_capacity': pool_capacity.get('used_capacity'),
                'free_capacity': pool_capacity.get('free_capacity')
            }
        else:
            err_msg = "domain or agent error: %s, %s" % \
                      (six.text_type(domain), six.text_type(agent))
            LOG.error(err_msg)
            raise exception.StorageBackendException(err_msg)
        return result

    def list_storage_pools(self, storage_id):
        pools = self.navi_handler.get_pools()
        pool_list = []
        if pools:
            for pool in pools:
                if pool.get('pool_name') is not None:
                    status = consts.STATUS_MAP.get(
                        pool.get('state'),
                        constants.StoragePoolStatus.OFFLINE)
                    used_cap = float(
                        pool.get("consumed_capacity_gbs")) * units.Gi
                    free_cap = float(
                        pool.get("available_capacity_gbs")) * units.Gi
                    total_cap = float(
                        pool.get("user_capacity_gbs")) * units.Gi
                    subscribed_cap = float(pool.get(
                        "total_subscribed_capacity_gbs")) * units.Gi
                    p = {
                        'name': pool.get('pool_name'),
                        'storage_id': storage_id,
                        'native_storage_pool_id': str(pool.get('pool_id')),
                        'description': pool.get('description'),
                        'status': status,
                        'storage_type': constants.StorageType.BLOCK,
                        'total_capacity': int(total_cap),
                        'subscribed_capacity': int(subscribed_cap),
                        'used_capacity': int(used_cap),
                        'free_capacity': int(free_cap)
                    }
                    pool_list.append(p)
        raid_groups = self.handle_raid_groups(storage_id)
        if raid_groups:
            pool_list.extend(raid_groups)
        return pool_list

    def handle_raid_groups(self, storage_id):
        raid_groups = self.navi_handler.get_raid_group()
        raid_list = []
        if raid_groups:
            for raid in raid_groups:
                if raid.get('raidgroup_id') is not None:
                    status = consts.STATUS_MAP.get(
                        raid.get('raidgroup_state'),
                        constants.StoragePoolStatus.OFFLINE)
                    free_cap = float(raid.get(
                        "free_capacity_blocks,non-contiguous"))
                    total_cap = float(
                        raid.get("logical_capacity_blocks"))
                    used_cap = total_cap - free_cap
                    p = {
                        'name': 'RAID Group %s' % raid.get('raidgroup_id'),
                        'storage_id': storage_id,
                        'native_storage_pool_id': '%s%s' % (
                            consts.RAID_GROUP_ID_PREFIX,
                            raid.get('raidgroup_id')),
                        'status': status,
                        'storage_type': constants.StorageType.BLOCK,
                        'total_capacity': int(total_cap * (units.Ki / 2)),
                        'used_capacity': int(used_cap * (units.Ki / 2)),
                        'free_capacity': int(free_cap * (units.Ki / 2))
                    }
                    raid_list.append(p)
        return raid_list

    def handle_volume_from_pool(self, volumes, pool_ids, storage_id):
        volume_list = []
        if volumes:
            for volume in volumes:
                if volume.get('name') is not None:
                    status = consts.STATUS_MAP.get(
                        volume.get('current_state'),
                        constants.StoragePoolStatus.OFFLINE)
                    orig_pool_name = volume.get('pool_name')
                    vol_type = consts.VOL_TYPE_MAP.get(
                        volume.get('is_thin_lun').lower())
                    volume_used_cap_str = volume.get('consumed_capacity_gbs')
                    used_cap = 0
                    if volume_used_cap_str and volume_used_cap_str != 'N/A':
                        used_cap = float(volume_used_cap_str) * units.Gi
                    total_cap = float(
                        volume.get('user_capacity_gbs')) * units.Gi
                    free_cap = total_cap - used_cap
                    if free_cap < 0:
                        free_cap = 0
                    v = {
                        'name': volume.get('name'),
                        'storage_id': storage_id,
                        'status': status,
                        'native_volume_id': str(volume.get('lun_id')),
                        'native_storage_pool_id': pool_ids.get(orig_pool_name,
                                                               ''),
                        'type': vol_type,
                        'total_capacity': int(total_cap),
                        'used_capacity': int(used_cap),
                        'free_capacity': int(free_cap),
                        'compressed': consts.VOL_COMPRESSED_MAP.get(
                            volume.get('is_compressed').lower()),
                        'wwn': volume.get('uid')
                    }
                    volume_list.append(v)
        return volume_list

    def handle_volume_from_raid_group(self, storage_id):
        volume_list = []
        volumes = self.navi_handler.get_all_lun()
        if volumes:
            for volume in volumes:
                if volume.get('raidgroup_id') and (
                        volume.get('raidgroup_id') != 'N/A' or volume.get(
                        'is_meta_lun') == 'YES'):
                    pool_id = None
                    if volume.get('raidgroup_id') != 'N/A':
                        pool_id = '%s%s' % (consts.RAID_GROUP_ID_PREFIX,
                                            volume.get('raidgroup_id'))
                    status = consts.STATUS_MAP.get(
                        volume.get('state'),
                        constants.StoragePoolStatus.OFFLINE)
                    vol_type = consts.VOL_TYPE_MAP.get(
                        volume.get('is_thin_lun').lower())
                    total_cap = float(
                        volume.get('lun_capacitymegabytes')) * units.Mi
                    used_cap = total_cap
                    free_cap = 0
                    v = {
                        'name': volume.get('name'),
                        'storage_id': storage_id,
                        'status': status,
                        'native_volume_id': str(
                            volume.get('logical_unit_number')),
                        'native_storage_pool_id': pool_id,
                        'type': vol_type,
                        'total_capacity': int(total_cap),
                        'used_capacity': int(used_cap),
                        'free_capacity': int(free_cap),
                        'wwn': volume.get('uid')
                    }
                    volume_list.append(v)
        return volume_list

    def list_volumes(self, storage_id):
        volumes = self.navi_handler.get_pool_lun()
        pools = self.navi_handler.get_pools()
        pool_ids = {}
        if pools:
            for pool in pools:
                if pool.get('pool_name') is not None:
                    pool_ids[pool.get('pool_name')] = pool.get('pool_id')
        volume_list = self.handle_volume_from_pool(volumes, pool_ids,
                                                   storage_id)
        raid_volumes = self.handle_volume_from_raid_group(storage_id)
        if raid_volumes:
            volume_list.extend(raid_volumes)
        return volume_list

    def handle_disk_capacity(self):
        disks = self.navi_handler.get_disks()
        raw_capacity = 0
        if disks:
            for disk in disks:
                if disk.get('disk_id') is not None:
                    capacity = float(disk.get("capacity", 0))
                    raw_capacity += capacity
        return raw_capacity * units.Mi

    def handle_pool_capacity(self):
        pools = self.list_storage_pools(None)
        total_capacity = 0
        free_capacity = 0
        used_capacity = 0
        obj_model = None
        if pools:
            for pool in pools:
                total_capacity += pool.get("total_capacity")
                free_capacity += pool.get("free_capacity")
                used_capacity += pool.get("used_capacity")
            obj_model = {
                'total_capacity': total_capacity,
                'free_capacity': free_capacity,
                'used_capacity': used_capacity
            }
        return obj_model

    def list_disks(self, storage_id):
        disks = self.navi_handler.get_disks()
        disk_list = []
        for disk in (disks or []):
            if disk.get('disk_id'):
                status = consts.DISK_STATUS_MAP.get(
                    disk.get('state', '').upper(),
                    constants.DiskStatus.ABNORMAL)
                capacity = int(float(disk.get("capacity", 0)) * units.Mi)
                logical_type = constants.DiskLogicalType.UNKNOWN
                hot_spare = disk.get('hot_spare', '')
                if hot_spare and hot_spare != 'N/A':
                    logical_type = constants.DiskLogicalType.HOTSPARE
                disk_model = {
                    'name': disk.get('disk_name'),
                    'storage_id': storage_id,
                    'native_disk_id': disk.get('disk_id'),
                    'serial_number': disk.get('serial_number'),
                    'manufacturer': disk.get('vendor_id'),
                    'model': disk.get('product_id'),
                    'firmware': disk.get('product_revision'),
                    'speed': None,
                    'capacity': capacity,
                    'status': status,
                    'physical_type': consts.DISK_PHYSICAL_TYPE_MAP.get(
                        disk.get('drive_type', '').upper(),
                        constants.DiskPhysicalType.UNKNOWN),
                    'logical_type': logical_type,
                    'health_score': None,
                    'native_disk_group_id': None,
                    'location': disk.get('disk_name')
                }
                disk_list.append(disk_model)
        return disk_list

    def analyse_speed(self, speed_value):
        speed = 0
        try:
            speeds = re.findall("\\d+", speed_value)
            if speeds:
                speed = int(speeds[0])
            if 'Gbps' in speed_value:
                speed = speed * units.G
            elif 'Mbps' in speed_value:
                speed = speed * units.M
            elif 'Kbps' in speed_value:
                speed = speed * units.k
        except Exception as err:
            err_msg = "analyse speed error: %s" % (six.text_type(err))
            LOG.error(err_msg)
        return speed

    def list_controllers(self, storage_id):
        controllers = self.navi_handler.get_controllers()
        cpus = self.navi_handler.get_cpus()
        controller_list = []
        for controller in (controllers or []):
            memory_size = int(controller.get('memory_size_for_the_sp',
                                             '0')) * units.Mi
            cpu_info = ''
            if cpus:
                cpu_info = cpus.get(
                    controller.get('serial_number_for_the_sp', ''), '')
            controller_model = {
                'name': controller.get('sp_name'),
                'storage_id': storage_id,
                'native_controller_id': controller.get('signature_for_the_sp'),
                'status': constants.ControllerStatus.NORMAL,
                'location': None,
                'soft_version': controller.get(
                    'revision_number_for_the_sp'),
                'cpu_info': cpu_info,
                'memory_size': str(memory_size)
            }
            controller_list.append(controller_model)
        return controller_list

    def list_ports(self, storage_id):
        port_list = []
        io_configs = self.navi_handler.get_io_configs()
        iscsi_port_map = self.get_iscsi_ports()
        ports = self.get_ports(storage_id, io_configs, iscsi_port_map)
        port_list.extend(ports)
        bus_ports = self.get_bus_ports(storage_id, io_configs)
        port_list.extend(bus_ports)
        return port_list

    def get_ports(self, storage_id, io_configs, iscsi_port_map):
        ports = self.navi_handler.get_ports()
        port_list = []
        for port in (ports or []):
            port_id = port.get('sp_port_id')
            sp_name = port.get('sp_name').replace('SP ', '')
            name = '%s-%s' % (sp_name, port_id)
            location = 'Slot %s%s,Port %s' % (
                sp_name, port.get('i/o_module_slot'),
                port.get('physical_port_id'))
            mac_address = port.get('mac_address')
            if mac_address == 'Not Applicable':
                mac_address = None
            module_key = '%s_%s' % (
                sp_name, port.get('i/o_module_slot'))
            type = ''
            if io_configs:
                type = io_configs.get(module_key, '')

            ipv4 = None
            ipv4_mask = None
            if iscsi_port_map:
                iscsi_port = iscsi_port_map.get(name)
                if iscsi_port:
                    ipv4 = iscsi_port.get('ip_address')
                    ipv4_mask = iscsi_port.get('subnet_mask')
            port_model = {
                'name': name,
                'storage_id': storage_id,
                'native_port_id': name,
                'location': location,
                'connection_status':
                    consts.PORT_CONNECTION_STATUS_MAP.get(
                        port.get('link_status', '').upper(),
                        constants.PortConnectionStatus.UNKNOWN),
                'health_status': consts.PORT_HEALTH_STATUS_MAP.get(
                    port.get('port_status', '').upper(),
                    constants.PortHealthStatus.UNKNOWN),
                'type': consts.PORT_TYPE_MAP.get(
                    type.upper(), constants.PortType.OTHER),
                'logical_type': None,
                'speed': self.analyse_speed(
                    port.get('speed_value', '')),
                'max_speed': self.analyse_speed(
                    port.get('max_speed', '')),
                'native_parent_id': None,
                'wwn': port.get('sp_uid'),
                'mac_address': mac_address,
                'ipv4': ipv4,
                'ipv4_mask': ipv4_mask,
                'ipv6': None,
                'ipv6_mask': None,
            }
            port_list.append(port_model)
        return port_list

    def get_bus_ports(self, storage_id, io_configs):
        bus_ports = self.navi_handler.get_bus_ports()
        port_list = []
        if bus_ports:
            bus_port_state_map = self.navi_handler.get_bus_port_state()
            for bus_port in bus_ports:
                sps = bus_port.get('sps')
                for sp in (sps or []):
                    sp_name = sp.replace('sp', '').upper()
                    name = '%s-%s' % (sp_name,
                                      bus_port.get('bus_name'))
                    location = '%s %s,Port %s' % (
                        bus_port.get('i/o_module_slot'), sp_name,
                        bus_port.get('physical_port_id'))
                    native_port_id = location.replace(' ', '')
                    native_port_id = native_port_id.replace(',', '')
                    module_key = '%s_%s' % (
                        sp_name, bus_port.get('i/o_module_slot'))
                    type = ''
                    if io_configs:
                        type = io_configs.get(module_key, '')
                    state = ''
                    if bus_port_state_map:
                        port_state_key = '%s_%s' % (
                            sp_name, bus_port.get('physical_port_id'))
                        state = bus_port_state_map.get(port_state_key,
                                                       '')
                    port_model = {
                        'name': name,
                        'storage_id': storage_id,
                        'native_port_id': native_port_id,
                        'location': location,
                        'connection_status':
                            constants.PortConnectionStatus.UNKNOWN,
                        'health_status':
                            consts.PORT_HEALTH_STATUS_MAP.get(
                                state.upper(),
                                constants.PortHealthStatus.UNKNOWN),
                        'type': consts.PORT_TYPE_MAP.get(
                            type.upper(), constants.PortType.OTHER),
                        'logical_type': None,
                        'speed': self.analyse_speed(
                            bus_port.get('current_speed', '')),
                        'max_speed': self.analyse_speed(
                            bus_port.get('max_speed', '')),
                        'native_parent_id': None,
                        'wwn': None,
                        'mac_address': None,
                        'ipv4': None,
                        'ipv4_mask': None,
                        'ipv6': None,
                        'ipv6_mask': None,
                    }
                    port_list.append(port_model)
        return port_list

    def get_iscsi_ports(self):
        iscsi_port_map = {}
        iscsi_ports = self.navi_handler.get_iscsi_ports()
        for iscsi_port in (iscsi_ports or []):
            name = '%s-%s' % (iscsi_port.get('sp'), iscsi_port.get('port_id'))
            iscsi_port_map[name] = iscsi_port
        return iscsi_port_map

    def collect_perf_metrics(self, storage_id, resource_metrics,
                             start_time, end_time):
        metrics = []
        try:
            # controller metrics
            if resource_metrics.get(constants.ResourceType.CONTROLLER):
                controller_metrics = self.get_controller_metrics(
                    storage_id,
                    resource_metrics.get(constants.ResourceType.CONTROLLER),
                    start_time, end_time)
                metrics.extend(controller_metrics)

            # volume metrics
            if resource_metrics.get(constants.ResourceType.VOLUME):
                volume_metrics = self.get_volume_metrics(
                    storage_id,
                    resource_metrics.get(constants.ResourceType.VOLUME),
                    start_time, end_time)
                metrics.extend(volume_metrics)

            # port metrics
            if resource_metrics.get(constants.ResourceType.PORT):
                port_metrics = self.get_port_metrics(
                    storage_id,
                    resource_metrics.get(constants.ResourceType.PORT),
                    start_time, end_time)
                metrics.extend(port_metrics)

            # disk metrics
            if resource_metrics.get(constants.ResourceType.DISK):
                disk_metrics = self.get_disk_metrics(
                    storage_id,
                    resource_metrics.get(constants.ResourceType.DISK),
                    start_time, end_time)
                metrics.extend(disk_metrics)
        except exception.DelfinException as err:
            err_msg = "Failed to collect metrics from VnxBlockStor: %s" % \
                      (six.text_type(err))
            LOG.error(err_msg)
            raise err
        except Exception as err:
            err_msg = "Failed to collect metrics from VnxBlockStor: %s" % \
                      (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return metrics

    def get_controller_metrics(self, storage_id, metric_list,
                               start_time, end_time):
        metrics = []
        sp_map = {}

        domains = self.navi_handler.get_domain()
        if domains:
            sps = self.navi_handler.get_controllers()
            for sp in (sps or []):
                sp_map[sp.get('sp_name')] = sp.get('signature_for_the_sp')
            for domain in domains:
                if domain and domain.get('ip_address'):
                    sp_ip = domain.get('ip_address')
                    sp_info = self.navi_handler.get_sp_detail(sp_ip)
                    if sp_info:
                        sp_info['readIops'] = int(sp_info.get('read_requests'))
                        sp_info['writeIops'] = int(
                            sp_info.get('write_requests'))
                        sp_info['iops'] = sp_info.get(
                            'readIops') + sp_info.get('writeIops')

                        sp_info['readThroughput'] = int(
                            sp_info.get('blocks_read', 0)) / consts.BLOCK_SIZE
                        sp_info['writeThroughput'] = int(
                            sp_info.get('blocks_written',
                                        0)) / consts.BLOCK_SIZE
                        sp_info['throughput'] = sp_info.get(
                            'readThroughput') + sp_info.get('writeThroughput')

                        sp_id = sp_map.get(sp_info.get('storage_processor'))
                        if sp_id:
                            labels = {
                                'storage_id': storage_id,
                                'resource_type':
                                    constants.ResourceType.CONTROLLER,
                                'resource_id': sp_id,
                                'type': 'RAW',
                                'unit': ''
                            }
                            metric_model_list = self._get_metric_model(
                                metric_list,
                                labels,
                                sp_info,
                                consts.CONTROLLER_CAP, end_time)
                            if metric_model_list:
                                metrics.extend(metric_model_list)
        return metrics

    def _get_metric_model(self, metric_list, labels, metric_value, obj_cap,
                          end_time):
        metric_model_list = []
        for metric_name in (metric_list or []):
            values = {}
            obj_labels = copy.deepcopy(labels)
            obj_labels['unit'] = obj_cap.get(metric_name).get('unit')
            if metric_value and metric_value.get(metric_name) is not None:
                values[end_time] = metric_value.get(metric_name)
            if values:
                metric_model = constants.metric_struct(name=metric_name,
                                                       labels=obj_labels,
                                                       values=values)
                metric_model_list.append(metric_model)
        return metric_model_list

    def get_volume_metrics(self, storage_id, metric_list,
                           start_time, end_time):
        metrics = []
        volumes = self.navi_handler.get_all_lun()
        for volume in (volumes or []):
            if volume:
                if volume.get('read_requests'):
                    volume['readIops'] = int(volume.get('read_requests'))
                    volume['writeIops'] = int(volume.get('write_requests'))
                    volume['iops'] = volume.get('readIops') + \
                        volume.get('writeIops')
                if volume.get('blocks_read'):
                    volume['readThroughput'] = int(
                        volume.get('blocks_read')) / consts.BLOCK_SIZE
                    volume['writeThroughput'] = int(
                        volume.get('blocks_written')) / consts.BLOCK_SIZE
                    volume['throughput'] = volume.get(
                        'readThroughput') + volume.get('writeThroughput')
                if volume.get('read_hit_ratio'):
                    volume['readCacheHitRatio'] = float(
                        volume.get('read_hit_ratio'))
                    volume['writeCacheHitRatio'] = float(
                        volume.get('write_hit_ratio'))

                responseTime = float(volume.get('average_read_time', 0))
                if volume.get('average_write_time', 0) > volume.get(
                        'average_read_time', 0):
                    responseTime = float(volume.get('average_write_time', 0))
                volume['responseTime'] = responseTime

                labels = {
                    'storage_id': storage_id,
                    'resource_type':
                        constants.ResourceType.VOLUME,
                    'resource_id': str(volume.get('logical_unit_number')),
                    'type': 'RAW',
                    'unit': ''
                }
                metric_model_list = self._get_metric_model(
                    metric_list,
                    labels,
                    volume,
                    consts.VOLUME_CAP, end_time)
                if metric_model_list:
                    metrics.extend(metric_model_list)

        return metrics

    def get_port_metrics(self, storage_id, metric_list, start_time, end_time):
        metrics = []
        ports = self.navi_handler.get_ports()
        for port in (ports or []):
            if port:
                port_id = port.get('sp_port_id')
                sp_name = port.get('sp_name').replace('SP ', '')
                name = '%s-%s' % (sp_name, port_id)
                if port.get('reads'):
                    port['readIops'] = int(port.get('reads'))
                    port['writeIops'] = int(port.get('writes'))
                    port['iops'] = port.get('readIops') + \
                        port.get('writeIops')
                if port.get('blocks_read'):
                    port['readThroughput'] = int(
                        port.get('blocks_read')) / consts.BLOCK_SIZE
                    port['writeThroughput'] = int(
                        port.get('blocks_written')) / consts.BLOCK_SIZE
                    port['throughput'] = port.get(
                        'readThroughput') + port.get('writeThroughput')

                labels = {
                    'storage_id': storage_id,
                    'resource_type':
                        constants.ResourceType.PORT,
                    'resource_id': name,
                    'type': 'RAW',
                    'unit': ''
                }
                metric_model_list = self._get_metric_model(
                    metric_list,
                    labels,
                    port,
                    consts.PORT_CAP, end_time)
                if metric_model_list:
                    metrics.extend(metric_model_list)

        return metrics

    def get_disk_metrics(self, storage_id, metric_list, start_time, end_time):
        metrics = []
        disks = self.navi_handler.get_disks()
        for disk in (disks or []):
            if disk:
                if disk.get('read_requests'):
                    disk['readIops'] = int(disk.get('read_requests'))
                    disk['writeIops'] = int(disk.get('write_requests'))
                    disk['iops'] = disk.get('readIops') + \
                        disk.get('writeIops')
                if disk.get('kbytes_read'):
                    disk['readThroughput'] = int(
                        disk.get('kbytes_read')) / units.Ki
                    disk['writeThroughput'] = int(
                        disk.get('kbytes_written')) / units.Ki
                    disk['throughput'] = disk.get(
                        'readThroughput') + disk.get('writeThroughput')

                labels = {
                    'storage_id': storage_id,
                    'resource_type':
                        constants.ResourceType.DISK,
                    'resource_id': disk.get('disk_id'),
                    'type': 'RAW',
                    'unit': ''
                }
                metric_model_list = self._get_metric_model(
                    metric_list,
                    labels,
                    disk,
                    consts.DISK_CAP, end_time)
                if metric_model_list:
                    metrics.extend(metric_model_list)

        return metrics

    def get_latest_perf_timestamp(self):
        latest_time = 0
        sp_info = self.navi_handler.get_sp_detail(None)
        if sp_info and sp_info.get('system_date') \
                and sp_info.get('system_time'):
            latest_time_str = '%s %s' % (sp_info.get('system_date'),
                                         sp_info.get('system_time'))
            tools = Tools()
            latest_time = tools.time_str_to_timestamp(latest_time_str,
                                                      consts.TIME_PATTERN)

        return latest_time
