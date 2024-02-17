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
