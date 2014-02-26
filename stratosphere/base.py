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

import itertools

import troposphere


class StratosphereObject(object):
    """A mixin for AWS objects to make them DSL-y."""
    def __init__(self, name, **kwargs):
        self.name = name # So it is available for later calls
        self.template = template = kwargs.pop('template', None)
        for prop in itertools.chain(self.__class__.props.iterkeys(), ['Metadata', 'DependsOn']):
            if prop not in kwargs and hasattr(self, prop):
                # Can't use getattr() because AWSObject overrides that and isn't initialized yet
                value = object.__getattribute__(self, prop)
                if callable(value):
                    value = value()
                if value is None:
                    continue
                kwargs[prop] = value
        # Auto-name-ify DependsOn
        if 'DependsOn' in kwargs:
            def _nameify(obj):
                if isinstance(obj, troposphere.AWSObject):
                    return obj.name
                else:
                    return obj
            if isinstance(kwargs['DependsOn'], list):
                kwargs['DependsOn'] = [_nameify(obj) for obj in kwargs['DependsOn']]
            else:
                kwargs['DependsOn'] = _nameify(kwargs['DependsOn'])
        super(StratosphereObject, self).__init__(name, **kwargs)
        # Reset it because Troposphere set it to None again
        self.template = template
