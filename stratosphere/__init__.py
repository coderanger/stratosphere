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
from .base import StratospherePendingObject, StratosphereObject
from .functions import *

class Parameter(StratosphereObject, troposphere.Parameter):
    @classmethod
    def add_to_template(cls, template, name, obj):
        template.add_parameter(obj)


class Output(StratosphereObject, troposphere.Output):
    @classmethod
    def add_to_template(cls, template, name, obj):
        template.add_output(obj)


class Mapping(troposphere.AWSObject):
    props = {}

    def __init__(self, name, template=None, **kwargs):
        self.data = kwargs
        self.template = template
        super(Mapping, self).__init__(name)

    def JSONrepr(self):
        return self.data

    @classmethod
    def add_to_template(cls, template, name, obj):
        template.add_mapping(name, obj.data)


class Condition(troposphere.AWSObject):
    props = {}

    def __init__(self, name, template=None, **kwargs): # FIXMEFIXMEFIXMEFIXME
        self.data = kwargs
        self.template = template
        super(Mapping, self).__init__(name)

    def JSONrepr(self):
        return self.data

    @classmethod
    def add_to_template(cls, template, name, obj):
        template.add_condition(name, obj)


def cfn(name, type):
    def decorator(fn):
        @functools.wraps(fn)
        def inner(self, *args, **kwargs):
            value = fn(self, *args, **kwargs)
            if isinstance(value, dict):
                if fn.__doc__:
                    value.setdefault('Description', fn.__doc__)
                value['template'] = self
                value = StratospherePendingObject(name, type, **value)
            return value
        inner._stratosphere_name = name
        inner._stratosphere_type = type
        return inner
    return decorator


class TemplateMeta(type):
    def __init__(self, name, bases, d):
        types = self.STRATOSPHERE_TYPES()
        for key, value in d.iteritems():
            if key.startswith('_'):
                continue
            parts = key.split('_', 1)
            prefix = parts[0]
            value_type = types.get(prefix)
            if not value_type:
                continue
            if len(parts) == 1:
                name = value_type.__name__ if value_type else key
            else:
                name = parts[1]
            # Apply the @cfn() decorator
            value = cfn(name, value_type)(value)
            setattr(self, key, value)


class Template(troposphere.Template):
    __metaclass__ = TemplateMeta

    @classmethod
    def STRATOSPHERE_TYPES(cls):
        return {
            'cond': Condition,
            'map': Mapping,
            'param': Parameter,
            'out': Output,
            'asg': autoscaling.AutoScalingGroup,
            'dhcp': ec2.DHCPOptions,
            'elb': elasticloadbalancing.LoadBalancer,
            'ig': ec2.InternetGateway,
            'instance': ec2.Instance,
            'insp': iam.InstanceProfile,
            'lc': autoscaling.LaunchConfiguration,
            'role': iam.Role,
            'route': ec2.Route,
            'rtb': ec2.RouteTable,
            'sg': ec2.SecurityGroup,
            'stack': cloudformation.Stack,
            'subnet': ec2.Subnet,
            'srta': ec2.SubnetRouteTableAssociation,
            'vdoa': ec2.VPCDHCPOptionsAssociation,
            'vpc': ec2.VPC,
            'vga': ec2.VPCGatewayAttachment,
        }

    def __init__(self):
        super(Template, self).__init__()
        # Use the docstring of the class as a default
        if self.__class__.__doc__:
            self.add_description(self.__class__.__doc__)
        # Process all magic methods
        for key in dir(self):
            value = getattr(self, key)
            if getattr(value, '_stratosphere_type', False):
                obj = value()
                if not obj:
                    continue # Returning none is a knockout
                if isinstance(obj, StratospherePendingObject):
                    obj = obj.to_object()
                value._stratosphere_type.add_to_template(self, value._stratosphere_name, obj)
                if hasattr(obj, 'post_add'):
                    obj.post_add(self)
