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

import troposphere

from .base import StratospherePendingObject


__all__ = ['And', 'Base64', 'Equals', 'FindInMap', 'GetAtt', 'GetAZs', 'If',
           'Join', 'Name', 'Not', 'NoValue', 'Select', 'Ref']


class AWSHelperFn(troposphere.AWSHelperFn):
    def getdata(self, obj):
        if isinstance(obj, StratospherePendingObject):
            return obj._stratosphere_name
        return super(AWSHelperFn, self).getdata(obj)


# Not really a function, but close enough
NoValue = troposphere.Ref('AWS::NoValue')


# Functions not implemented in troposphere
class And(AWSHelperFn):
    def __init__(self, *terms):
        self.data = {'Fn::And': terms}

    def JSONrepr(self):
        return self.data


class Equals(AWSHelperFn):
    def __init__(self, value_1, value_2):
        self.data = {'Fn::Equals': [value_1, value_2]}

    def JSONrepr(self):
        return self.data


class Not(AWSHelperFn):
    def __init__(self, value):
        self.data = {'Fn::Not': [value]}

    def JSONrepr(self):
        return self.data


# Wrappers to use my mixin
class Base64(AWSHelperFn, troposphere.Base64):
    pass


class FindInMap(AWSHelperFn, troposphere.FindInMap):
    pass


class GetAtt(AWSHelperFn, troposphere.GetAtt):
    pass


class GetAZs(AWSHelperFn, troposphere.GetAZs):
    pass


class If(AWSHelperFn, troposphere.If):
    pass


class Join(AWSHelperFn, troposphere.Join):
    pass


class Name(AWSHelperFn, troposphere.Name):
    pass


class Ref(AWSHelperFn, troposphere.Ref):
    pass


class Select(AWSHelperFn, troposphere.Select):
    pass
