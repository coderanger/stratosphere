#
# Author:: Noah Kantrowitz <noah@coderanger.net>
#
# Copyright 2014, Balanced, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import collections
import functools

import troposphere

from . import autoscaling, cloudformation, ec2, elasticloadbalancing, iam
from .base import StratosphereObject

class Parameter(StratosphereObject, troposphere.Parameter):
    pass


class Output(StratosphereObject, troposphere.Output):
    pass


class Mapping(troposphere.AWSObject):
    props = {}

    def __init__(self, name, template=None, **kwargs):
        self.data = kwargs
        self.template = template
        super(Mapping, self).__init__(name)

    def JSONrepr(self):
        return self.data


class TemplateMeta(type):
    def __init__(self, name, bases, d):
        for fn_prefix, collection_name, add_fn, value_type in self.STRATOSPHERE_TYPES():
            collection = collections.OrderedDict()
            # Pull in base class data
            if bases and hasattr(bases[0], collection_name):
                collection.update(getattr(bases[0], collection_name))
            # Process any magic methods
            for key, value in d.iteritems():
                if (key == fn_prefix or key.startswith(fn_prefix+'_')) and callable(value):
                    if key == fn_prefix:
                        param_name = value_type.__name__ if value_type else key
                    else:
                        param_name = key[len(fn_prefix+'_'):]
                    value = self.troposphere_fn(value, param_name, value_type)
                    collection[param_name] = value
                    setattr(self, key, value)
            setattr(self, collection_name, collection)

    @staticmethod
    def troposphere_fn(fn, name, value_type):
        cache = {}
        @functools.wraps(fn)
        def inner(self):
            value = cache.get(name)
            if value is not None:
                return value
            value = fn(self)
            if value is None:
                return value
            def _value(value, suffix=''):
                if isinstance(value, dict):
                    # Cast from dict to troposphere object (or subclass)
                    value = value_type(name+suffix, template=self, **value)
                if fn.__doc__:
                    if 'Description' in value_type.props and not getattr(value, 'Description', None):
                        # Set the description based on the docstring
                        value.Description = fn.__doc__
                    elif 'GroupDescription' in value_type.props and not getattr(value, 'GroupDescription', None):
                        # Security groups use GroupDescription for whatever reason
                        value.GroupDescription = fn.__doc__
                    elif 'Tags' in value_type.props:
                        # Fallback, set a tag named Description
                        value.Tags = getattr(value, 'Tags', [])
                        for tag in value.Tags:
                            if tag['Key'] == 'Description':
                                # If it already has a description, don't change it
                                break
                        else:
                            tag = {'Key': 'Description', 'Value': fn.__doc__}
                            tag.update(getattr(value_type, 'DESCRIPTION_TAG_EXTRA', {}))
                            value.Tags.append(tag)
                return value
            if isinstance(value, list):
                value = [_value(v, str(i)) for i, v in enumerate(value)]
            else:
                value = _value(value)
            cache[name] = value
            return value
        return inner


class Template(troposphere.Template):
    __metaclass__ = TemplateMeta

    AUTO_SCALING_GROUP_TYPE = autoscaling.AutoScalingGroup
    DHCP_OPTIONS_TYPE = ec2.DHCPOptions
    INSTANCE_TYPE = ec2.Instance
    INSTANCE_PROFILE_TYPE = iam.InstanceProfile
    INTERNET_GATEWAY_TYPE = ec2.InternetGateway
    LOAD_BALANCER_TYPE = elasticloadbalancing.LoadBalancer
    LAUNCH_CONFIGURATION_TYPE = autoscaling.LaunchConfiguration
    ROLE_TYPE = iam.Role
    ROUTE_TYPE = ec2.Route
    ROUTE_TABLE_TYPE = ec2.RouteTable
    SUBNET_TYPE = ec2.Subnet
    SUBNET_ROUTE_TABLE_ASSOCIATION = ec2.SubnetRouteTableAssociation
    SECURITY_GROUP_TYPE = ec2.SecurityGroup
    STACK_TYPE = cloudformation.Stack
    VPC_TYPE = ec2.VPC
    VPC_DHCP_OPTIONS_ASSOCIATION_TYPE = ec2.VPCDHCPOptionsAssociation
    VPC_GATEWAY_ATTACHEMENT_TYPE = ec2.VPCGatewayAttachment

    @classmethod
    def STRATOSPHERE_TYPES(cls):
        return [
            # (fn_prefix, collection_name, add_fn, value_type)
            ('cond', 'conditions', 'add_condition', None),
            ('map', 'mappings', 'add_mapping', Mapping),
            ('param', 'parameters', 'add_parameter', Parameter),
            ('out', 'outputs', 'add_output', Output),
            ('asg', 'auto_scaling_groups', 'add_resource', cls.AUTO_SCALING_GROUP_TYPE),
            ('dhcp', 'dhcp_options', 'add_resource', cls.DHCP_OPTIONS_TYPE),
            ('elb', 'load_balancers', 'add_resource', cls.LOAD_BALANCER_TYPE),
            ('ig', 'internet_gateways', 'add_resource', cls.INTERNET_GATEWAY_TYPE),
            ('instance', 'instances', 'add_resource', cls.INSTANCE_TYPE),
            ('insp', 'instance_profiles', 'add_resource', cls.INSTANCE_PROFILE_TYPE),
            ('lc', 'launch_configurations', 'add_resource', cls.LAUNCH_CONFIGURATION_TYPE),
            ('role', 'roles', 'add_resource', cls.ROLE_TYPE),
            ('route', 'routes', 'add_resource', cls.ROUTE_TYPE),
            ('rtb', 'route_tables', 'add_resource', cls.ROUTE_TABLE_TYPE),
            ('sg', 'security_groups', 'add_resource', cls.SECURITY_GROUP_TYPE),
            ('stack', 'stacks', 'add_resource', cls.STACK_TYPE),
            ('subnet', 'subnets', 'add_resource', cls.SUBNET_TYPE),
            ('srta', 'subnet_route_table_associations', 'add_resource', cls.SUBNET_ROUTE_TABLE_ASSOCIATION),
            ('vdoa', 'vpc_dhcp_options_associations', 'add_resource', cls.VPC_DHCP_OPTIONS_ASSOCIATION_TYPE),
            ('vpc', 'vpcs', 'add_resource', cls.VPC_TYPE),
            ('vga', 'vpc_gateway_attachements', 'add_resource', cls.VPC_GATEWAY_ATTACHEMENT_TYPE),
        ]

    def __init__(self):
        super(Template, self).__init__()
        # Use the docstring of the class as a default
        if self.__class__.__doc__:
            self.add_description(self.__class__.__doc__)
        # Process all magic methods
        for fn_prefix, collection_name, add_fn, value_type in self.STRATOSPHERE_TYPES():
            for key, value in getattr(self.__class__, collection_name).iteritems():
                if callable(value):
                    value = value(self)
                if value is None:
                    continue # Knock out via None
                if not value_type or isinstance(value, value_type): # Allow not adding if its a string
                    if value_type:
                        getattr(self, add_fn)(value)
                    else:
                        getattr(self, add_fn)(key, value)
                    if hasattr(value, 'post_add'):
                        getattr(value, 'post_add')(self)

    def add_mapping(self, name_or_data, data=None):
        if not data:
            # Allow passing either one or two arguments
            data = name_or_data
            name_or_data = data.name
        super(Template, self).add_mapping(name_or_data, data)
