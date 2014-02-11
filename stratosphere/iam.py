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

import troposphere.iam

from .base import StratosphereObject

# Some hopefully saner defaults
class InstanceProfile(StratosphereObject, troposphere.iam.InstanceProfile):
    def Path(self):
        return '/' # I have no idea what this means


class Role(StratosphereObject, troposphere.iam.Role):
    def __init__(self, *args, **kwargs):
        self._statements = kwargs.pop('Statements', [])
        super(Role, self).__init__(*args, **kwargs)

    def Path(self):
        return '/' # I have no idea what this means

    def AssumeRolePolicyDocument(self):
         # I also have no idea what this means.
         # Copied from http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html
        return {
           'Version': '2012-10-17',
            'Statement': [ {
                'Effect': 'Allow',
                'Principal': {
                    'Service': [ 'ec2.amazonaws.com' ]
                },
                'Action': [ 'sts:AssumeRole' ]
            } ]
         }

    def Policies(self):
        return [troposphere.iam.Policy(
            PolicyName=self.name,
            PolicyDocument={
                'Version': '2012-10-17',
                'Statement': self._statements
            }
        )]
