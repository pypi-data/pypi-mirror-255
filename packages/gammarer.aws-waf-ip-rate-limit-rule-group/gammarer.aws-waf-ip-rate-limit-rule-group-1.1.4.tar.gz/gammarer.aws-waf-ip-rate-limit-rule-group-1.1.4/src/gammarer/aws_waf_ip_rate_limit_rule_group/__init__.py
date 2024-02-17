'''
[![GitHub](https://img.shields.io/github/license/gammarer/aws-waf-ip-rate-limit-rule-group?style=flat-square)](https://github.com/gammarer/aws-waf-ip-rate-limit-rule-group/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@gammarer/aws-waf-ip-rate-limit-rule-group?style=flat-square)](https://www.npmjs.com/package/@gammarer/aws-waf-ip-rate-limit-rule-group)
[![PyPI](https://img.shields.io/pypi/v/gammarer.aws-waf-ip-rate-limit-rule-group?style=flat-square)](https://pypi.org/project/gammarer.aws-waf-ip-rate-limit-rule-group/)
[![Nuget](https://img.shields.io/nuget/v/Gammarer.CDK.AWS.WafIpRateLimitRuleGroup?style=flat-square)](https://www.nuget.org/packages/Gammarer.CDK.AWS.WafIpRateLimitRuleGroup/)
[![Sonatype Nexus (Releases)](https://img.shields.io/nexus/r/com.gammarer/aws-waf-ip-rate-limit-rule-group?server=https%3A%2F%2Fs01.oss.sonatype.org%2F&style=flat-square)](https://s01.oss.sonatype.org/content/repositories/releases/com/gammarer/aws-waf-ip-rate-limit-rule-group/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/actions/workflow/status/gammarer/aws-waf-ip-rate-limit-rule-group/release.yml?branch=main&label=release&style=flat-square)](https://github.com/gammarer/aws-waf-ip-rate-limit-rule-group/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/gammarer/aws-waf-ip-rate-limit-rule-group?sort=semver&style=flat-square)](https://github.com/gammarer/aws-waf-ip-rate-limit-rule-group/releases)

# AWS WAF(V2) IP Rete Limit Rule Group

This is an AWS CDK Construct for IP Rate Limit Rule on WAF V2

## Resources

This construct creating resource list.

* WAF V2 RuleGroup

## Install

### TypeScript

```shell
npm install @gammarer/aws-waf-ip-rate-limit-rule-group
# or
yarn add @gammarer/aws-waf-ip-rate-limit-rule-group
```

### Python

```shell
pip install gammarer.aws-waf-ip-rate-limit-rule-group
```

### C# / .Net

```shell
dotnet add package Gammarer.CDK.AWS.WafIpRateLimitRuleGroup
```

### Java

Add the following to pom.xml:

```xml
<dependency>
  <groupId>com.gammarer</groupId>
  <artifactId>aws-waf-ip-rate-limit-rule-group</artifactId>
</dependency>
```

## Example

```python
import { Scope, WafRateLimitRuleGroup } from '@gammarer/aws-waf-ip-rate-limit-rule-group';

new WafIpRateLimitRuleGroup(stack, 'WafIpRateLimitRuleGroup', {
  name: 'rate-limit-rule-group',
  scope: Scope.REGIONAL,
  rateLimitCount: 3000, // default 1000
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

import aws_cdk.aws_wafv2 as _aws_cdk_aws_wafv2_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.enum(jsii_type="@gammarer/aws-waf-ip-rate-limit-rule-group.Scope")
class Scope(enum.Enum):
    GLOBAL = "GLOBAL"
    REGIONAL = "REGIONAL"


class WafIpRateLimitRuleGroup(
    _aws_cdk_aws_wafv2_ceddda9d.CfnRuleGroup,
    metaclass=jsii.JSIIMeta,
    jsii_type="@gammarer/aws-waf-ip-rate-limit-rule-group.WafIpRateLimitRuleGroup",
):
    def __init__(
        self,
        scope_: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        scope: Scope,
        name: typing.Optional[builtins.str] = None,
        rate_limit_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope_: Specifies whether this is for an Amazon CloudFront distribution or for a regional application. A regional application can be an Application Load Balancer (ALB), an Amazon API Gateway REST API, an AWS AppSync GraphQL API, an Amazon Cognito user pool, or an AWS App Runner service. Valid Values are ``CLOUDFRONT`` and ``REGIONAL`` . .. epigraph:: For ``CLOUDFRONT`` , you must create your WAFv2 resources in the US East (N. Virginia) Region, ``us-east-1`` .
        :param id: -
        :param scope: 
        :param name: 
        :param rate_limit_count: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f417af6ffc1be50fef7e14c7b0892dcc48ee68cea3ba9115886196eea172eb5)
            check_type(argname="argument scope_", value=scope_, expected_type=type_hints["scope_"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WafIpRateLimitRuleGroupProps(
            scope=scope, name=name, rate_limit_count=rate_limit_count
        )

        jsii.create(self.__class__, self, [scope_, id, props])


@jsii.data_type(
    jsii_type="@gammarer/aws-waf-ip-rate-limit-rule-group.WafIpRateLimitRuleGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "scope": "scope",
        "name": "name",
        "rate_limit_count": "rateLimitCount",
    },
)
class WafIpRateLimitRuleGroupProps:
    def __init__(
        self,
        *,
        scope: Scope,
        name: typing.Optional[builtins.str] = None,
        rate_limit_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: 
        :param name: 
        :param rate_limit_count: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c677d2470cd21b929c436f05ad4ed58fbe7063d5159b356fc4b3dfe1cb45c8f2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument rate_limit_count", value=rate_limit_count, expected_type=type_hints["rate_limit_count"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "scope": scope,
        }
        if name is not None:
            self._values["name"] = name
        if rate_limit_count is not None:
            self._values["rate_limit_count"] = rate_limit_count

    @builtins.property
    def scope(self) -> Scope:
        result = self._values.get("scope")
        assert result is not None, "Required property 'scope' is missing"
        return typing.cast(Scope, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rate_limit_count(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("rate_limit_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WafIpRateLimitRuleGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Scope",
    "WafIpRateLimitRuleGroup",
    "WafIpRateLimitRuleGroupProps",
]

publication.publish()

def _typecheckingstub__9f417af6ffc1be50fef7e14c7b0892dcc48ee68cea3ba9115886196eea172eb5(
    scope_: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    scope: Scope,
    name: typing.Optional[builtins.str] = None,
    rate_limit_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c677d2470cd21b929c436f05ad4ed58fbe7063d5159b356fc4b3dfe1cb45c8f2(
    *,
    scope: Scope,
    name: typing.Optional[builtins.str] = None,
    rate_limit_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
