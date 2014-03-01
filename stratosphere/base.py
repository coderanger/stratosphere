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


class StratospherePendingObject(dict):
    """A dict that will later on be converted to a Stratosphere/Troposphere object."""
    def __init__(self, stratosphere_name, stratosphere_type, *args, **kwargs):
        self._stratosphere_name = stratosphere_name
        self._stratosphere_type = stratosphere_type
        super(StratospherePendingObject, self).__init__(*args, **kwargs)

    def to_object(self):
        type = self._stratosphere_type
        # Try to unify setting a description
        if 'Description' in self:
            description = self.pop('Description')
            if 'Description' in self._stratosphere_type.props:
                # Well, that was fun, wasn't it?
                self['Description'] = description
            elif 'GroupDescription' in self._stratosphere_type.props:
                # Security groups use GroupDescription for whatever reason
                self['GroupDescription'] = description
            elif 'Tags' in type.props:
                # Fallback, set a tag named Description
                self.setdefault('Tags', [])
                for tag in self['Tags']:
                    if tag['Key'] == 'Description':
                        # If it already has a description, don't change it
                        break
                else:
                    tag = {'Key': 'Description', 'Value': description}
                    tag.update(getattr(self._stratosphere_type, 'DESCRIPTION_TAG_EXTRA', {}))
                    self['Tags'].append(tag)
        return self._stratosphere_type(self._stratosphere_name, **self)


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
                if isinstance(obj, StratospherePendingObject):
                    return obj._stratosphere_name
                elif isinstance(obj, troposphere.AWSObject):
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

    @classmethod
    def add_to_template(cls, template, name, obj):
        """Add an object to a given template."""
        if isinstance(obj, troposphere.AWSObject):
            template.add_resource(obj)
