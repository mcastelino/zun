# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_log import log as logging

from zun.common import exception
from zun import objects

LOG = logging.getLogger(__name__)


class ComputeNodeTracker(object):
    def __init__(self, host, container_driver):
        self.host = host
        self.container_driver = container_driver

    def update_available_resources(self, context):
        # Check if the compute_node is already registered
        node = self._get_compute_node(context)
        if not node:
            # If not, register it and pass the object to the driver
            numa_obj = self.container_driver.get_host_numa_topology()
            node = objects.ComputeNode(context)
            node.hostname = self.host
            node.numa_topology = numa_obj
            node.create(context)
            LOG.info('Node created for :%(host)s', {'host': self.host})
        self.container_driver.get_available_resources(node)
        node.save()
        # NOTE(sbiswas7): Consider removing the return statement if not needed
        return node

    def _get_compute_node(self, context):
        """Returns compute node for the host"""
        try:
            return objects.ComputeNode.get_by_hostname(context, self.host)
        except exception.ComputeNodeNotFound:
            LOG.warning("No compute node record for: %(host)s",
                        {'host': self.host})
