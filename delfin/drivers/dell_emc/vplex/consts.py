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
from delfin.common import constants

SOCKET_TIMEOUT = 10
BASE_CONTEXT = '/vplex'
REST_AUTH_URL = '/vplex/clusters'

PORT_TYPE_MAP = {
    'fc': constants.PortType.FC,
    'iscsi': constants.PortType.ISCSI,
    'ficon': constants.PortType.FICON,
    'fcoe': constants.PortType.FCOE,
    'eth': constants.PortType.ETH,
    'sas': constants.PortType.SAS,
    'ib': constants.PortType.IB,
    'other': constants.PortType.OTHER,
}
PORT_LOGICAL_TYPE_MAP = {
    'front-end': constants.PortLogicalType.FRONTEND,
    'back-end': constants.PortLogicalType.BACKEND,
    'service': constants.PortLogicalType.SERVICE,
    'management': constants.PortLogicalType.MANAGEMENT,
    'internal': constants.PortLogicalType.INTERNAL,
    'maintenance': constants.PortLogicalType.MAINTENANCE,
    'inter-director-communication': constants.PortLogicalType.INTERCONNECT,
    'other': constants.PortLogicalType.OTHER,
    'local-com': constants.PortLogicalType.INTERCLUSTER,
    'wan-com': constants.PortLogicalType.CLUSTER_MGMT
}
PORT_CONNECT_STATUS_MAP = {
    'up': constants.PortConnectionStatus.CONNECTED,
    'down': constants.PortConnectionStatus.DISCONNECTED,
    'no-link': constants.PortConnectionStatus.UNKNOWN,
    'ok': constants.PortConnectionStatus.CONNECTED,
    'pending': constants.PortConnectionStatus.CONNECTED,
    'suspended': constants.PortConnectionStatus.DISCONNECTED,
    'hardware error': constants.PortConnectionStatus.UNKNOWN
}
PORT_HEALTH_STATUS_MAP = {
    'ok': constants.PortHealthStatus.NORMAL,
    'error': constants.PortHealthStatus.ABNORMAL,
    'stopped': constants.PortHealthStatus.UNKNOWN
}
CONTROLLER_STATUS_MAP = {
    "ok": constants.ControllerStatus.NORMAL,
    "busy": constants.ControllerStatus.NORMAL,
    "no contact": constants.ControllerStatus.OFFLINE,
    "lost communication": constants.ControllerStatus.OFFLINE,
    "unknown": constants.ControllerStatus.UNKNOWN
}

IOPS_DESCRIPTION = {
    "name": "iops",
    "unit": "IOPS",
    "description": "Input/output operations per second"
}
READ_IOPS_DESCRIPTION = {
    "name": "readIops",
    "unit": "IOPS",
    "description": "Read input/output operations per second"
}
WRITE_IOPS_DESCRIPTION = {
    "name": "writeIops",
    "unit": "IOPS",
    "description": "Write input/output operations per second"
}
THROUGHPUT_DESCRIPTION = {
    "name": "throughput",
    "unit": "MB/s",
    "description": "Represents how much data is "
                   "successfully transferred in MB/s"
}
READ_THROUGHPUT_DESCRIPTION = {
    "name": "readThroughput",
    "unit": "MB/s",
    "description": "Represents how much data read is "
                   "successfully transferred in MB/s"
}
WRITE_THROUGHPUT_DESCRIPTION = {
    "name": "writeThroughput",
    "unit": "MB/s",
    "description": "Represents how much data write is "
                   "successfully transferred in MB/s"
}
RESPONSE_TIME_DESCRIPTION = {
    "name": "responseTime",
    "unit": "ms",
    "description": "Average time taken for an IO "
                   "operation in ms"
}
CACHE_HIT_RATIO_DESCRIPTION = {
    "name": "cacheHitRatio",
    "unit": "%",
    "description": "Percentage of io that are cache hits"
}
READ_CACHE_HIT_RATIO_DESCRIPTION = {
    "name": "readCacheHitRatio",
    "unit": "%",
    "description": "Percentage of read ops that are cache hits"
}
WRITE_CACHE_HIT_RATIO_DESCRIPTION = {
    "name": "writeCacheHitRatio",
    "unit": "%",
    "description": "Percentage of write ops that are cache hits"
}
IO_SIZE_DESCRIPTION = {
    "name": "ioSize",
    "unit": "KB",
    "description": "The average size of IO requests in KB"
}
READ_IO_SIZE_DESCRIPTION = {
    "name": "ioSizeRead",
    "unit": "KB",
    "description": "The average size of read IO requests in KB"
}
WRITE_IO_SIZE_DESCRIPTION = {
    "name": "ioSizeWrite",
    "unit": "KB",
    "description": "The average size of write IO requests in KB"
}

VOLUME_CAP = {
    "iops": IOPS_DESCRIPTION,
    "readIops": READ_IOPS_DESCRIPTION,
    "writeIops": WRITE_IOPS_DESCRIPTION,
    "throughput": THROUGHPUT_DESCRIPTION,
    "readThroughput": READ_THROUGHPUT_DESCRIPTION,
    "writeThroughput": WRITE_THROUGHPUT_DESCRIPTION,
    "responseTime": RESPONSE_TIME_DESCRIPTION,
    "cacheHitRatio": CACHE_HIT_RATIO_DESCRIPTION,
    "readCacheHitRatio": READ_CACHE_HIT_RATIO_DESCRIPTION,
    "writeCacheHitRatio": WRITE_CACHE_HIT_RATIO_DESCRIPTION,
    "ioSize": IO_SIZE_DESCRIPTION,
    "readIoSize": READ_IO_SIZE_DESCRIPTION,
    "writeIoSize": WRITE_IO_SIZE_DESCRIPTION,
}

