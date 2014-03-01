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

import json

import stratosphere
from stratosphere import Ref

class TestObjects(object):
    def d(self, cls):
        return json.loads(cls().to_json())

    def test_post_add(self):
        class MySubnet(stratosphere.ec2.Subnet):
            def post_add(self, template):
                template.add_resource(stratosphere.ec2.Subnet(
                    '{}Two'.format(self.name),
                    VpcId=self.VpcId,
                    CidrBlock=self.CidrBlock,
                ))
        class MyTemplate(stratosphere.Template):
            def subnet(self):
                return MySubnet('Subnet', VpcId=Ref('vpc-teapot'), CidrBlock='10.0.0.0/16')
        assert self.d(MyTemplate) == {
            'Resources': {
                'Subnet': {
                    'Properties': {
                        'CidrBlock': '10.0.0.0/16',
                        'VpcId': {'Ref': 'vpc-teapot'},
                    },
                    'Type': 'AWS::EC2::Subnet',
                },
                'SubnetTwo': {
                    'Properties': {
                        'CidrBlock': '10.0.0.0/16',
                        'VpcId': {'Ref': 'vpc-teapot'},
                    },
                    'Type': 'AWS::EC2::Subnet',
                },
            },
        }
