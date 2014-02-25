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

import troposphere.ec2

from .base import StratosphereObject


class DHCPOptions(StratosphereObject, troposphere.ec2.DHCPOptions):
    pass


class Instance(StratosphereObject, troposphere.ec2.Instance):
    pass


class InternetGateway(StratosphereObject, troposphere.ec2.InternetGateway):
    pass


class Route(StratosphereObject, troposphere.ec2.Route):
    pass


class RouteTable(StratosphereObject, troposphere.ec2.RouteTable):
    pass


class SecurityGroup(StratosphereObject, troposphere.ec2.SecurityGroup):
    pass


class SecurityGroupIngress(StratosphereObject, troposphere.ec2.SecurityGroupIngress):
    pass


class SecurityGroupRule(StratosphereObject, troposphere.ec2.SecurityGroupRule):
    pass


class Subnet(StratosphereObject, troposphere.ec2.Subnet):
    pass


class SubnetRouteTableAssociation(StratosphereObject, troposphere.ec2.SubnetRouteTableAssociation):
    pass


class VPC(StratosphereObject, troposphere.ec2.VPC):
    pass


class VPCDHCPOptionsAssociation(StratosphereObject, troposphere.ec2.VPCDHCPOptionsAssociation):
    pass


class VPCGatewayAttachment(StratosphereObject, troposphere.ec2.VPCGatewayAttachment):
    pass
