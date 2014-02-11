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

from troposphere import Ref, FindInMap

import stratosphere

class TestTemplate(object):
    def d(self, cls):
        return json.loads(cls().to_json())

    def test_empty(self):
        class MyTemplate(stratosphere.Template):
            pass
        assert self.d(MyTemplate) == {'Resources': {}}

    def test_parameter(self):
        class MyTemplate(stratosphere.Template):
            def param_Foo(self):
                return {'Type': 'String'}
        assert self.d(MyTemplate) == {
            'Resources': {},
            'Parameters': {
                'Foo': {'Type': 'String'},
            },
        }

    def test_parameter_description(self):
        class MyTemplate(stratosphere.Template):
            def param_Foo(self):
                """I am a teapot."""
                return {'Type': 'String'}
        assert self.d(MyTemplate) == {
            'Resources': {},
            'Parameters': {
                'Foo': {
                    'Type': 'String',
                    'Description': 'I am a teapot.',
                },
            },
        }

    def test_subnet(self):
        class MyTemplate(stratosphere.Template):
            def subnet(self):
                return {'VpcId': Ref('vpc-teapot'), 'CidrBlock': '10.0.0.0/16'}
        assert self.d(MyTemplate) == {
            'Resources': {
                'Subnet': {
                    'Properties': {
                        'CidrBlock': '10.0.0.0/16',
                        'VpcId': {'Ref': 'vpc-teapot'},
                    },
                    'Type': 'AWS::EC2::Subnet',
                },
            },
        }

    def test_subnet_description(self):
        class MyTemplate(stratosphere.Template):
            def subnet(self):
                """I am a teapot."""
                return {'VpcId': Ref('vpc-teapot'), 'CidrBlock': '10.0.0.0/16'}
        assert self.d(MyTemplate) == {
            'Resources': {
                'Subnet': {
                    'Properties': {
                        'CidrBlock': '10.0.0.0/16',
                        'VpcId': {'Ref': 'vpc-teapot'},
                        'Tags': [{'Key': 'Description', 'Value': 'I am a teapot.'}],
                    },
                    'Type': 'AWS::EC2::Subnet',
                },
            },
        }

    def test_subnet_tags(self):
        class MyTemplate(stratosphere.Template):
            def subnet(self):
                """I am a teapot."""
                return {
                    'VpcId': Ref('vpc-teapot'),
                    'CidrBlock': '10.0.0.0/16',
                    'Tags': [{'Key': 'Foo', 'Value': 'Bar'}],
                }
        assert self.d(MyTemplate) == {
            'Resources': {
                'Subnet': {
                    'Properties': {
                        'CidrBlock': '10.0.0.0/16',
                        'VpcId': {'Ref': 'vpc-teapot'},
                        'Tags': [
                            {'Key': 'Foo', 'Value': 'Bar'},
                            {'Key': 'Description', 'Value': 'I am a teapot.'},
                        ],
                    },
                    'Type': 'AWS::EC2::Subnet',
                },
            },
        }

    def test_subnet_tags_description(self):
        class MyTemplate(stratosphere.Template):
            def subnet(self):
                """I am a teapot."""
                return {
                    'VpcId': Ref('vpc-teapot'),
                    'CidrBlock': '10.0.0.0/16',
                    'Tags': [
                        {'Key': 'Foo', 'Value': 'Bar'},
                        {'Key': 'Description', 'Value': 'Short and stout'},
                    ],
                }
        assert self.d(MyTemplate) == {
            'Resources': {
                'Subnet': {
                    'Properties': {
                        'CidrBlock': '10.0.0.0/16',
                        'VpcId': {'Ref': 'vpc-teapot'},
                        'Tags': [
                            {'Key': 'Foo', 'Value': 'Bar'},
                            {'Key': 'Description', 'Value': 'Short and stout'},
                        ],
                    },
                    'Type': 'AWS::EC2::Subnet',
                },
            },
        }

    def test_subnet_name(self):
        class MyTemplate(stratosphere.Template):
            def subnet_MySubnet(self):
                return {'VpcId': Ref('vpc-teapot'), 'CidrBlock': '10.0.0.0/16'}
        assert self.d(MyTemplate) == {
            'Resources': {
                'MySubnet': {
                    'Properties': {
                        'CidrBlock': '10.0.0.0/16',
                        'VpcId': {'Ref': 'vpc-teapot'},
                    },
                    'Type': 'AWS::EC2::Subnet',
                },
            },
        }

    def test_subnets(self):
        class MyTemplate(stratosphere.Template):
            def subnet(self):
                return [
                    {'VpcId': Ref('vpc-teapot'), 'CidrBlock': '10.0.0.0/16'},
                    {'VpcId': Ref('vpc-teapot'), 'CidrBlock': '10.1.0.0/16'},
                ]
        assert self.d(MyTemplate) == {
            'Resources': {
                'Subnet0': {
                    'Properties': {
                        'CidrBlock': '10.0.0.0/16',
                        'VpcId': {'Ref': 'vpc-teapot'},
                    },
                    'Type': 'AWS::EC2::Subnet',
                },
                'Subnet1': {
                    'Properties': {
                        'CidrBlock': '10.1.0.0/16',
                        'VpcId': {'Ref': 'vpc-teapot'},
                    },
                    'Type': 'AWS::EC2::Subnet',
                },
            },
        }

    def test_subnet_object(self):
        class MyTemplate(stratosphere.Template):
            def subnet(self):
                return {'VpcId': Ref('vpc-teapot'), 'CidrBlock': '10.0.0.0/16'}
        assert type(MyTemplate().subnet()) == stratosphere.ec2.Subnet

    def test_mapping(self):
        class MyTemplate(stratosphere.Template):
            def map_MyMap(self):
                return {
                    'Region': {'Cidr': '10.0.0.0/16'}
                }
            def subnet(self):
                return {
                    'VpcId': Ref('vpc-teapot'),
                    'CidrBlock': FindInMap(self.map_MyMap(), 'Region', 'Cidr')}
        assert self.d(MyTemplate) == {
            'Mappings': {
                'MyMap': {
                    'Region': {
                        'Cidr': '10.0.0.0/16',
                    },
                },
            },
            'Resources': {
                'Subnet': {
                    'Properties': {
                        'CidrBlock': {'Fn::FindInMap': ['MyMap', 'Region', 'Cidr']},
                        'VpcId': {'Ref': 'vpc-teapot'},
                    },
                    'Type': 'AWS::EC2::Subnet',
                },
            },
        }

    def test_depends_on(self):
        class MyTemplate(stratosphere.Template):
            def subnet_One(self):
                return {'VpcId': Ref('vpc-teapot'), 'CidrBlock': '10.0.0.0/16'}
            def subnet_Two(self):
                return {'VpcId': Ref('vpc-teapot'), 'CidrBlock': '10.0.0.0/16', 'DependsOn': self.subnet_One()}
        assert self.d(MyTemplate)['Resources']['Two']['DependsOn'] == 'One'
