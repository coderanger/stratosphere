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


class And(troposphere.AWSHelperFn):
    def __init__(self, *terms):
        self.data = {'Fn::And': terms}

    def JSONrepr(self):
        return self.data


class Equals(troposphere.AWSHelperFn):
    def __init__(self, value_1, value_2):
        self.data = {'Fn::Equals': [value_1, value_2]}

    def JSONrepr(self):
        return self.data


class Not(troposphere.AWSHelperFn):
    def __init__(self, value):
        self.data = {'Fn::Not': [value]}

    def JSONrepr(self):
        return self.data
