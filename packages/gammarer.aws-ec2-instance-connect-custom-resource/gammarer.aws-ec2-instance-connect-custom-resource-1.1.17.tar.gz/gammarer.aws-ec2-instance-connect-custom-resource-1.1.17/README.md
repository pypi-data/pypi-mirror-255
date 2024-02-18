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
