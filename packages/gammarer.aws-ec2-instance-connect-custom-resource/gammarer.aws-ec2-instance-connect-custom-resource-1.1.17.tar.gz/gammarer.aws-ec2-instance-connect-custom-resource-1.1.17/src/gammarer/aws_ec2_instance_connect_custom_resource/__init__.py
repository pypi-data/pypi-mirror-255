'''
[![GitHub](https://img.shields.io/github/license/yicr/aws-ec2-instance-connect-custom-resource?style=flat-square)](https://github.com/yicr/aws-ec2-instance-connect-custom-resource/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@gammarer/aws-ec2-instance-connect-custom-resource?style=flat-square)](https://www.npmjs.com/package/@gammarer/aws-ec2-instance-connect-custom-resource)
[![PyPI](https://img.shields.io/pypi/v/gammarer.aws-ec2-instance-connect-custom-resource?style=flat-square)](https://pypi.org/project/gammarer.aws-ec2-instance-connect-custom-resource/)
[![Nuget](https://img.shields.io/nuget/v/Gammarer.CDK.AWS.Ec2InstanceConnectCustomResource?style=flat-square)](https://www.nuget.org/packages/Gammarer.CDK.AWS.Ec2InstanceConnectCustomResource/)
[![Sonatype Nexus (Releases)](https://img.shields.io/nexus/r/com.gammarer/aws-ec2-instance-connect-custom-resource?server=https%3A%2F%2Fs01.oss.sonatype.org%2F&style=flat-square)](https://s01.oss.sonatype.org/content/repositories/releases/com/gammarer/aws-ec2-instance-connect-custom-resource/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/actions/workflow/status/yicr/aws-ec2-instance-connect-custom-resource/release.yml?branch=main&label=release&style=flat-square)](https://github.com/yicr/aws-ec2-instance-connect-custom-resource/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/yicr/aws-ec2-instance-connect-custom-resource?sort=semver&style=flat-square)](https://github.com/yicr/aws-ec2-instance-connect-custom-resource/releases)

# AWS EC2 Instance Connect Custom Resource

AWS EC2 instance connect custom resource

## Resources

This construct creating resource list.

* AWS Custom Resource

  * Lambda Function Iam Role
  * Lambda Function
  * Custom Resource Iam Role
  * Custom Policy

## Install

### TypeScript

```shell
npm install @gammarer/aws-ec2-instance-connect-custom-resource
# or
yarn add @gammarer/aws-ec2-instance-connect-custom-resource
```

### Python

```shell
pip install gammarer.aws-ec2-instance-connect-custom-resource
```

### C# / .NET

```shell
dotnet add package Gammarer.CDK.AWS.Ec2InstanceConnectCustomResource
```

### Java

Add the following to pom.xml:

```xml
<dependency>
  <groupId>com.gammarer</groupId>
  <artifactId>aws-ec2-instance-connect-custom-resource</artifactId>
</dependency>
```

## Example

```python
import { EC2InstanceConnectCustomResource } from '@gammarer/aws-ec2-instance-connect-custom-resource';

new EC2InstanceConnectCustomResource(stack, 'EC2InstanceConnectCustomResource', {
  subnetId: 'example-subnet-id',
  securityGroupIds: [
    'example-security-group-id',
  ],
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

import aws_cdk.custom_resources as _aws_cdk_custom_resources_ceddda9d
import constructs as _constructs_77d1e7e8


class EC2InstanceConnectCustomResource(
    _aws_cdk_custom_resources_ceddda9d.AwsCustomResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@gammarer/aws-ec2-instance-connect-custom-resource.EC2InstanceConnectCustomResource",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        security_group_ids: typing.Sequence[builtins.str],
        subnet_id: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param security_group_ids: 
        :param subnet_id: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f475e5d806199c83bc7094448bc88b57f44e82fb8fab5232cb55c402e072c3e2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EC2InstanceConnectCustomResourceProps(
            security_group_ids=security_group_ids, subnet_id=subnet_id
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@gammarer/aws-ec2-instance-connect-custom-resource.EC2InstanceConnectCustomResourceProps",
    jsii_struct_bases=[],
    name_mapping={"security_group_ids": "securityGroupIds", "subnet_id": "subnetId"},
)
class EC2InstanceConnectCustomResourceProps:
    def __init__(
        self,
        *,
        security_group_ids: typing.Sequence[builtins.str],
        subnet_id: builtins.str,
    ) -> None:
        '''
        :param security_group_ids: 
        :param subnet_id: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__554a8ee9735d8ebe27b681c3d54942ffd87256408e39099f8d73e21cdf04b5b3)
            check_type(argname="argument security_group_ids", value=security_group_ids, expected_type=type_hints["security_group_ids"])
            check_type(argname="argument subnet_id", value=subnet_id, expected_type=type_hints["subnet_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "security_group_ids": security_group_ids,
            "subnet_id": subnet_id,
        }

    @builtins.property
    def security_group_ids(self) -> typing.List[builtins.str]:
        result = self._values.get("security_group_ids")
        assert result is not None, "Required property 'security_group_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def subnet_id(self) -> builtins.str:
        result = self._values.get("subnet_id")
        assert result is not None, "Required property 'subnet_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EC2InstanceConnectCustomResourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "EC2InstanceConnectCustomResource",
    "EC2InstanceConnectCustomResourceProps",
]

publication.publish()

def _typecheckingstub__f475e5d806199c83bc7094448bc88b57f44e82fb8fab5232cb55c402e072c3e2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    security_group_ids: typing.Sequence[builtins.str],
    subnet_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__554a8ee9735d8ebe27b681c3d54942ffd87256408e39099f8d73e21cdf04b5b3(
    *,
    security_group_ids: typing.Sequence[builtins.str],
    subnet_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
