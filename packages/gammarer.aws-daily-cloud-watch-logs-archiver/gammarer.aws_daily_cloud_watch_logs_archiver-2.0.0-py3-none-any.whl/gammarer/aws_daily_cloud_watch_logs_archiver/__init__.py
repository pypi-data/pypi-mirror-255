'''
[![GitHub](https://img.shields.io/github/license/yicr/aws-daily-cloud-watch-logs-archiver?style=flat-square)](https://github.com/yicr/aws-daily-cloud-watch-logs-archiver/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@gammarer/aws-daily-cloud-watch-logs-archiver?style=flat-square)](https://www.npmjs.com/package/@gammarer/aws-daily-cloud-watch-logs-archiver)
[![PyPI](https://img.shields.io/pypi/v/gammarer.aws-daily-cloud-watch-logs-archiver?style=flat-square)](https://pypi.org/project/gammarer.aws-daily-cloud-watch-logs-archiver/)

<!-- [![Nuget](https://img.shields.io/nuget/v/Gammarer.CDK.AWS.DailyCloudWatchLogsArchiver?style=flat-square)](https://www.nuget.org/packages/Gammarer.CDK.AWS.DailyCloudWatchLogsArchiver/)  --><!-- [![Sonatype Nexus (Releases)](https://img.shields.io/nexus/r/com.gammarer/aws-daily-cloud-watch-logs-archiver?server=https%3A%2F%2Fs01.oss.sonatype.org%2F&style=flat-square)](https://s01.oss.sonatype.org/content/repositories/releases/com/gammarer/aws-daily-cloud-watch-logs-archiver/) -->

[![GitHub Workflow Status (branch)](https://img.shields.io/github/actions/workflow/status/yicr/aws-daily-cloud-watch-logs-archiver/release.yml?branch=main&label=release&style=flat-square)](https://github.com/yicr/aws-daily-cloud-watch-logs-archiver/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/yicr/aws-daily-cloud-watch-logs-archiver?sort=semver&style=flat-square)](https://github.com/yicr/aws-daily-cloud-watch-logs-archiver/releases)

# AWS Daily CloudWatch Logs Archiver

AWS CloudWatch Logs daily(13:00Z) archive to s3 bucket.

## Resources

This construct creating resource list.

* S3 Bucket (log-archive-xxxxxxxx from @yicr/aws-secure-log-bucket)
* Lambda function execution role
* Lambda function
* Lambda function log group
* StepFunctions state machine execution role
* StepFunctions state machine
* EventBridge Scheduler execution role
* EventBridge Scheduler

## Install

### TypeScript

```shell
npm install @gammarer/aws-daily-cloud-watch-logs-archiver
# or
yarn add @gammarer/aws-daily-cloud-watch-logs-archiver
```

### Python

```shell
pip install gammarer.aws-daily-cloud-watch-logs-archiver
```

## Example

```shell
npm install @gammarer/aws-daily-cloud-watch-logs-archiver
```

```python
import { DailyCloudWatchLogsArchiver } from '@gammarer/aws-daily-cloud-watch-logs-archiver';

new DailyCloudWatchLogsArchiver(stack, 'DailyCloudWatchLogsArchiver', {
    resource: {
      key: 'DailyLogExport',
      values: ['Yes'],
    },
});
```

## License

This project is licensed under the Apache-2.0 License.
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import constructs as _constructs_77d1e7e8


class DailyCloudWatchLogsArchiver(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@gammarer/aws-daily-cloud-watch-logs-archiver.DailyCloudWatchLogsArchiver",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        resource: typing.Union["ResourceTagProperty", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param resource: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e72c2c7b24eae3cd643e26390a7256d4cd092a754c618a1f7640c2fb0e27b3b1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DailyCloudWatchLogsArchiverProps(resource=resource)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@gammarer/aws-daily-cloud-watch-logs-archiver.DailyCloudWatchLogsArchiverProps",
    jsii_struct_bases=[],
    name_mapping={"resource": "resource"},
)
class DailyCloudWatchLogsArchiverProps:
    def __init__(
        self,
        *,
        resource: typing.Union["ResourceTagProperty", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param resource: 
        '''
        if isinstance(resource, dict):
            resource = ResourceTagProperty(**resource)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f57aec0f3186cca3b12d63a473fd51ab3ed39b18d5a0bd495a8899be9278bbc5)
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "resource": resource,
        }

    @builtins.property
    def resource(self) -> "ResourceTagProperty":
        result = self._values.get("resource")
        assert result is not None, "Required property 'resource' is missing"
        return typing.cast("ResourceTagProperty", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DailyCloudWatchLogsArchiverProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@gammarer/aws-daily-cloud-watch-logs-archiver.ResourceTagProperty",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "values": "values"},
)
class ResourceTagProperty:
    def __init__(
        self,
        *,
        key: builtins.str,
        values: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param key: 
        :param values: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d545dab64143138cf4ef3d2cca5896f735b29e934ff30e6bef6e1891253960d)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument values", value=values, expected_type=type_hints["values"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "values": values,
        }

    @builtins.property
    def key(self) -> builtins.str:
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def values(self) -> typing.List[builtins.str]:
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResourceTagProperty(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DailyCloudWatchLogsArchiver",
    "DailyCloudWatchLogsArchiverProps",
    "ResourceTagProperty",
]

publication.publish()

def _typecheckingstub__e72c2c7b24eae3cd643e26390a7256d4cd092a754c618a1f7640c2fb0e27b3b1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    resource: typing.Union[ResourceTagProperty, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f57aec0f3186cca3b12d63a473fd51ab3ed39b18d5a0bd495a8899be9278bbc5(
    *,
    resource: typing.Union[ResourceTagProperty, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d545dab64143138cf4ef3d2cca5896f735b29e934ff30e6bef6e1891253960d(
    *,
    key: builtins.str,
    values: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass
