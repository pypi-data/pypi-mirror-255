'''
[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fmoia-oss%2Fbastion-host-forward%2Fbadge&style=flat)](https://actions-badge.atrox.dev/moia-oss/bastion-host-forward/goto)
[![npm version](https://badge.fury.io/js/%40moia-oss%2Fbastion-host-forward.svg)](https://badge.fury.io/js/%40moia-oss%2Fbastion-host-forward)
[![PyPI version](https://badge.fury.io/py/moia-dev.bastion-host-forward.svg)](https://badge.fury.io/py/moia-dev.bastion-host-forward)

# Bastion Host Forward

This is a CDK Library providing custom bastion host constructs for connecting to
several AWS data services. When building secure infrastructure, we face the
problem that the data layer is only accessible from inside the VPC. These
Bastion Hosts close the gap and let you interact with the data layer as they
would be hosted on your machine.

Currently the following AWS Services are supported:

| AWS Service       | CDK Construct                        |
| ----------------- | ------------------------------------ |
| Aurora Serverless | `BastionHostAuroraServerlessForward` |
| Redis             | `BastionHostRedisForward`            |
| Redshift          | `BastionHostRedshiftForward`         |
| RDS               | `BastionHostRDSForward`              |

# V3 DISCLAIMER

With version 3 a patch manager component is included so that the bastion host instance is provided with security updates on a regular basis. These happen in a maintenance window every sunday at 3am (timezone where it's deployed). To disable the patching, you need to provide the attribute `shouldPatch: false`.

Example:

```python
new GenericBastionHostForward(this, 'BastionHostRedshiftForward', {
  vpc,
  securityGroup,
  address,
  port,
  shouldPatch: false,
});
```

# V1 DISCLAIMER

We introduced v1.0.0 recently, which now relies on v2 of CDK. This introced an
incompability, because they don't offer a L2 Construct for
[Redshift](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_redshift-readme.html)
anymore. This is why we cant offer the `BastionHostRedshiftForward` Construct
anymore. We would need to accept a CFN L1 Construct instead, but we didn't allow
this for the `BastionHostRedisForward` as well. Instead we decided to rename the
`BastionHostRedisForward` to `GenericBastionHostForward`, which needs only the
endpoint address and the port of the data store to be able to forward connections.

With the new `GenericBastionHostForward` you are still able to forward
connections to Redis and Redshift and also every other data store in AWS, which
we don't support specifically so far.

# Technical details

The bastion hosts are extensions of the official `BastionHostLinux` CDK
construct, which allows connecting to the bastion host and from there connect to
the data layer.

These constructs additionally install and configure
[HAProxy](https://www.haproxy.org/) to forward the endpoint of the chosen data
store. They also have the SSM Agent to the bastion host, so you can connect via
the AWS Session Manager. Connecting to a bastion host via the AWS Session
Manager brings a couple of benefits:

* No management of SSH Keys anymore
* AWS IAM defines who is able to connect to the bastion host
* Bastion Hosts don't need to be hosted in public subnets anymore
* Easy port forwarding with a single command

The combination of having a local port forward via SSM Session Manager and the
HAProxy on the bastion host itself let you interact with the data layer as they
would be on your machine. This means you can connect to them via localhost:<port
of the data service> and also use visual tools like DataGrip or MySQL Workbench
to interact with the data store in AWS. The following graphic illustrates the
described procedure on the example of RDS:

![bastion-host-forward](doc/bastion-host-forward.png)

# Setup

First of all you need to include this library into your project for the language
you want to deploy the bastion host with

## Javascript/Typescript

For Javascript/Typescript the library can be installed via npm:

```
npm install @moia-oss/bastion-host-forward
```

## Python

For python the library can be installed via pip:

```
pip install moia-dev.bastion-host-forward
```

# Examples

The following section includes some examples in supported languages how the
Bastion Host can be created for different databases.

## Bastion Host for RDS in Typescript

A minimal example for creating the RDS Forward Construct, which will be used via
username/password could look like this snippet:

```python
import * as cdk from '@aws-cdk/core';
import { SecurityGroup, Vpc } from '@aws-cdk/aws-ec2';
import { DatabaseInstance } from '@aws-cdk/aws-rds';
import { BastionHostRDSForward } from '@moia-oss/bastion-host-forward';

export class BastionHostPocStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = Vpc.fromLookup(this, 'MyVpc', {
      vpcId: 'vpc-0123456789abcd'
    });

    const securityGroup = SecurityGroup.fromSecurityGroupId(
      this,
      'RDSSecurityGroup',
      'odsufa5addasdj',
      { mutable: false }
    );

    const rdsInstance = DatabaseInstance.fromDatabaseInstanceAttributes(
      this,
      'MyDb',
      {
        instanceIdentifier: 'abcd1234geh',
        instanceEndpointAddress: 'abcd1234geh.ughia8asd.eu-central-1.rds.amazonaws.com',
        port: 5432,
        securityGroups: [securityGroup]
      }
    );

    new BastionHostRDSForward(this, 'BastionHost', {
      vpc: vpc,
      rdsInstance: rdsInstance,
      name: 'MyBastionHost',
    });
```

If the RDS is IAM Authenticated you also need to add an `iam_user` and
`rdsResourceIdentifier` to the BastionHostRDSForward:

```python
...
new BastionHostRDSForward(this, 'BastionHost', {
  vpc: vpc,
  rdsInstance: rdsInstance,
  name: 'MyBastionHost',
  iamUser: 'iamusername',
  rdsResourceIdentifier: 'db-ABCDEFGHIJKL123'
});
```

This will spawn a Bastion Host in the defined VPC. You also need to make sure
that IPs from within the VPC are able to connect to the RDS Database. This
needs to be set in the RDS's Security Group. Otherwise the Bastion Host can't
connect to the RDS.

## Bastion Host for a generic data store on AWS (Redis, Redshift etc.)

### Typescript

A minimal example for creating the Generic Forward Construct, which will be used
via username/password could look like this snippet. In this case we forward a
connection to a RedShift instance, but this can also be a Redis Node or any
other data store on AWS. Instead of passing the complete L2 construct and
letting the library extract the necessary properties, the client is passing them
directly to the construct:

```python
import * as cdk from '@aws-cdk/core';
import { GenericBastionHostForward } from '@moia-oss/bastion-host-forward';
import { SecurityGroup, Vpc } from '@aws-cdk/aws-ec2';
import { Cluster } from '@aws-cdk/aws-redshift';

export class PocRedshiftStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = Vpc.fromLookup(this, 'MyVpc', {
      vpcId: 'vpc-12345678',
    });

    const securityGroup = SecurityGroup.fromSecurityGroupId(this, 'BastionHostSecurityGroup', 'sg-1245678', {
      mutable: false,
    });

    const redshiftCluster = Cluster.fromClusterAttributes(this, 'RedshiftCluster', {
      clusterName: 'myRedshiftClusterName',
      clusterEndpointAddress: 'myRedshiftClusterName.abcdefg.eu-central-1.redshift.amazonaws.com',
      clusterEndpointPort: 5439,
    });

    new GenericBastionHostForward(this, 'BastionHostRedshiftForward', {
      vpc,
      securityGroup,
      name: 'MyRedshiftBastionHost',
      address: redshiftCluster.clusterEndpointAddress,
      port: redshiftCluster.clusterEndpointPort,
    });
  }
}
```

### Python

```python
from aws_cdk import core as cdk
from aws_cdk import aws_redshift
from aws_cdk import aws_ec2
from moia_dev import bastion_host_forward


class PocRedshiftStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        vpc = aws_ec2.Vpc.from_lookup(
            self,
            "vpc",
            vpc_id="vpc-12345678"
        )
        security_group = aws_ec2.SecurityGroup.from_security_group_id(
            self,
            "sec_group", "sg-12345678"
        )
        redshift_cluster = aws_redshift.Cluster.from_cluster_attributes(
            self,
            "cluster",
            cluster_name="myRedshiftClusterName",
            cluster_endpoint_address="myRedshiftClusterName.abcdefg.eu-central-1.redshift.amazonaws.com",
            cluster_endpoint_port=5439
        )

        bastion_host_forward.GenericBastionHostForward(
            self,
            "bastion-host",
            name="my-bastion-host",
            security_group=security_group,
            address: redshift_cluster.cluster_endpoint_address,
            port: redshift_cluster.cluster_endpoint_port,
            vpc=vpc
        )
```

## Bastion Host for Aurora Serverless

```python
import * as cdk from '@aws-cdk/core';
import { SecurityGroup, Vpc } from '@aws-cdk/aws-ec2';
import { ServerlessCluster } from '@aws-cdk/aws-rds';
import { BastionHostAuroraServerlessForward } from '@moia-oss/bastion-host-rds-forward';

export class BastionHostPocStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = Vpc.fromLookup(this, 'MyVpc', {
      vpcId: 'vpc-0123456789abcd'
    });

    const securityGroup = SecurityGroup.fromSecurityGroupId(
      this,
      'AuroraSecurityGroup',
      'odsufa5addasdj',
      { mutable: false }
    );

    const serverlessCluster = ServerlessCluster.fromServerlessClusterAttributes(
      this,
      'Aurora',
      {
        clusterIdentifier: 'my-cluster',
        port: 3306,
        clusterEndpointAddress: 'my-aurora.cluster-abcdef.eu-central-1.rds.amazonaws.com',
        securityGroups: [securityGroup]
      }
    );

    new BastionHostAuroraServerlessForward(this, 'BastionHost', {
      vpc,
      serverlessCluster,
    });
```

## Deploying the Bastion Host

When you setup the Bastion Host for the Database you want to connect to, you can
now go forward to actually deploy the Bastion Host:

```
cdk deploy
```

When the EC2 Instance for you Bastion Host is visible you can continue with the
setup of the Session-Manager Plugin on your Machine

# Install the Session-Manager Plugin for AWS-CLI

You are also able to connect to the Bastion Host via the AWS Web
Console. For this go to `AWS Systems Manager` -> `Session Manager` -> choose
the newly created instance -> click on start session.

But overall it's a much more comfortable experience to connect to the Bastion
Session Manager Plugin. On Mac OSX you can get it via homebrew for example:

```
brew install --cask session-manager-plugin
```

For Linux it should also be available in the respective package manager. Also
have a look at [the official installation instructions from
AWS](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html)

## Forward the connection to your machine

The Session Manager offers a command to forward a specific port. On the Bastion
Host a HAProxy was installed which forwards the connection on the same
port as the specified service. Those are by default:

* RDS MySQL: 3306
* RDS PostgreSQL: 5432
* Redis: 6739
* Redshift: 5439

In the following example, we show how to forward the connection of a PostgreSQL
database. To forward the connection to our machine we execute the following
command in the shell:

```
aws ssm start-session \
    --target <bastion-host-id> \
    --document-name AWS-StartPortForwardingSession \
    --parameters '{"portNumber": ["5432"], "localPortNumber":["5432"]}'
```

This creates a port forward session on the defined `localPortNumber`. The
target is the id of the bastion host instance. This will be output
automatically after deploying the bastion host. The `portNumber` must be the
same as the RDS Port.

Now you would be able to connect to the RDS as it would run on localhost:5432.

*Note*

In the example of a MySQL running in Serverless Aurora, we couldn't connect to
the database using localhost. If you face the same issue, make sure to also try to connect via
the local IP 127.0.0.1.

Example with the MySQL CLI:

```sh
mysql -u <username> -h 127.0.0.1 -p
```

## Additional step if you are using IAM Authentication on RDS

If you have an IAM authenticated RDS, the inline policy of the bastion
host will be equipped with access rights accordingly. Namely it will get `rds:*`
permissions on the RDS you provided and it also allows `rds-db:connect` with
the provided `iamUser`.

Most of the steps you would perform to connect to the RDS are the same, since it wouldn't
be in a VPC.

First you generate the PGPASSWORD on your local machine:

```
export
PGPASSWORD="$(aws rds generate-db-auth-token
--hostname=<rds endpoint> --port=5432
--username=<iam user> --region <the region of the rds>)"
```

You also need to have the RDS certificate from AWS, which you can download:

```
wget https://s3.amazonaws.com/rds-downloads/rds-ca-2019-root.pem
```

There is now an additional step needed, because the certificate checks against
the real endpoint name during the connect procedure. Therefore we need to add
an entry to the `/etc/hosts` file on our machine:

```
echo "127.0.0.1  <rds endpoint>" >> /etc/hosts
```

Now you can connect to the IAM authenticated RDS like this:

```
psql "host=<rds endpoint> port=5432 dbname=<database name> user=<iamUser> sslrootcert=<full path to downloaded cert> sslmode=verify-ca"
```

For a full guide on how to connect to an IAM authenticated RDS check out [this
guide by AWS](https://aws.amazon.com/premiumsupport/knowledge-center/users-connect-rds-iam/)
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

import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_rds as _aws_cdk_aws_rds_ceddda9d
import constructs as _constructs_77d1e7e8


class BastionHostForward(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@moia-oss/bastion-host-forward.BastionHostForward",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        address: builtins.str,
        port: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        cached_in_context: typing.Optional[builtins.bool] = None,
        client_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        server_timeout: typing.Optional[jsii.Number] = None,
        should_patch: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param address: The address of the service to forward to.
        :param port: The port of the service to forward to.
        :param vpc: The Vpc in which to instantiate the Bastion Host.
        :param cached_in_context: Whether the AMI ID is cached to be stable between deployments. By default, the newest image is used on each deployment. This will cause instances to be replaced whenever a new version is released, and may cause downtime if there aren't enough running instances in the AutoScalingGroup to reschedule the tasks on. If set to true, the AMI ID will be cached in ``cdk.context.json`` and the same value will be used on future runs. Your instances will not be replaced but your AMI version will grow old over time. To refresh the AMI lookup, you will have to evict the value from the cache using the ``cdk context`` command. See https://docs.aws.amazon.com/cdk/latest/guide/context.html for more information. Can not be set to ``true`` in environment-agnostic stacks. Default: false
        :param client_timeout: The HAProxy client timeout in minutes. Default: 1
        :param name: The name of the bastionHost instance. Default: "BastionHost"
        :param security_group: The security group, which is attached to the bastion host. Default: If none is provided a default security group is attached, which doesn't allow incoming traffic and allows outbound traffic to everywhere
        :param server_timeout: The HAProxy server timeout in minutes. Default: 1
        :param should_patch: Whether patching should be enabled for the bastion-host-forward instance. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11d2abdf217ee36451e346fc935fa9cf68c35b672a0da8fe74b9f254090f5ebc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BastionHostForwardProps(
            address=address,
            port=port,
            vpc=vpc,
            cached_in_context=cached_in_context,
            client_timeout=client_timeout,
            name=name,
            security_group=security_group,
            server_timeout=server_timeout,
            should_patch=should_patch,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="bastionHost")
    def _bastion_host(self) -> _aws_cdk_aws_ec2_ceddda9d.BastionHostLinux:
        '''
        :return: The BastionHost Instance
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.BastionHostLinux, jsii.get(self, "bastionHost"))

    @builtins.property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> typing.Optional[builtins.str]:
        '''
        :return:

        the id of the bastion host, which can be used by the session
        manager connect command afterwards
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceId"))

    @instance_id.setter
    def instance_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0aa8ec88289bd4e63d045aa01c31796f7d8df6f7e8c61e5a1635d7c38d19657b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceId", value)

    @builtins.property
    @jsii.member(jsii_name="instancePrivateIp")
    def instance_private_ip(self) -> typing.Optional[builtins.str]:
        '''
        :return: the private ip address of the bastion host
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instancePrivateIp"))

    @instance_private_ip.setter
    def instance_private_ip(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f1513e49883dc7160b0953eba3100220e268a94d25b73bb69473c19b8a60f14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instancePrivateIp", value)

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''
        :return: the security group attached to the bastion host
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], jsii.get(self, "securityGroup"))

    @security_group.setter
    def security_group(
        self,
        value: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbe10306f21028866820c653f2ff1bf09db7797c5923ab094d25cb3942a322c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securityGroup", value)


@jsii.data_type(
    jsii_type="@moia-oss/bastion-host-forward.BastionHostForwardBaseProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "cached_in_context": "cachedInContext",
        "client_timeout": "clientTimeout",
        "name": "name",
        "security_group": "securityGroup",
        "server_timeout": "serverTimeout",
        "should_patch": "shouldPatch",
    },
)
class BastionHostForwardBaseProps:
    def __init__(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        cached_in_context: typing.Optional[builtins.bool] = None,
        client_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        server_timeout: typing.Optional[jsii.Number] = None,
        should_patch: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param vpc: The Vpc in which to instantiate the Bastion Host.
        :param cached_in_context: Whether the AMI ID is cached to be stable between deployments. By default, the newest image is used on each deployment. This will cause instances to be replaced whenever a new version is released, and may cause downtime if there aren't enough running instances in the AutoScalingGroup to reschedule the tasks on. If set to true, the AMI ID will be cached in ``cdk.context.json`` and the same value will be used on future runs. Your instances will not be replaced but your AMI version will grow old over time. To refresh the AMI lookup, you will have to evict the value from the cache using the ``cdk context`` command. See https://docs.aws.amazon.com/cdk/latest/guide/context.html for more information. Can not be set to ``true`` in environment-agnostic stacks. Default: false
        :param client_timeout: The HAProxy client timeout in minutes. Default: 1
        :param name: The name of the bastionHost instance. Default: "BastionHost"
        :param security_group: The security group, which is attached to the bastion host. Default: If none is provided a default security group is attached, which doesn't allow incoming traffic and allows outbound traffic to everywhere
        :param server_timeout: The HAProxy server timeout in minutes. Default: 1
        :param should_patch: Whether patching should be enabled for the bastion-host-forward instance. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f293a86cd803ccc93821f68fa9a4ce7a663457599c3ff2d33b88bafb430fae0)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument cached_in_context", value=cached_in_context, expected_type=type_hints["cached_in_context"])
            check_type(argname="argument client_timeout", value=client_timeout, expected_type=type_hints["client_timeout"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument server_timeout", value=server_timeout, expected_type=type_hints["server_timeout"])
            check_type(argname="argument should_patch", value=should_patch, expected_type=type_hints["should_patch"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
        }
        if cached_in_context is not None:
            self._values["cached_in_context"] = cached_in_context
        if client_timeout is not None:
            self._values["client_timeout"] = client_timeout
        if name is not None:
            self._values["name"] = name
        if security_group is not None:
            self._values["security_group"] = security_group
        if server_timeout is not None:
            self._values["server_timeout"] = server_timeout
        if should_patch is not None:
            self._values["should_patch"] = should_patch

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The Vpc in which to instantiate the Bastion Host.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def cached_in_context(self) -> typing.Optional[builtins.bool]:
        '''Whether the AMI ID is cached to be stable between deployments.

        By default, the newest image is used on each deployment. This will cause
        instances to be replaced whenever a new version is released, and may cause
        downtime if there aren't enough running instances in the AutoScalingGroup
        to reschedule the tasks on.

        If set to true, the AMI ID will be cached in ``cdk.context.json`` and the
        same value will be used on future runs. Your instances will not be replaced
        but your AMI version will grow old over time. To refresh the AMI lookup,
        you will have to evict the value from the cache using the ``cdk context``
        command. See https://docs.aws.amazon.com/cdk/latest/guide/context.html for
        more information.

        Can not be set to ``true`` in environment-agnostic stacks.

        :default: false
        '''
        result = self._values.get("cached_in_context")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def client_timeout(self) -> typing.Optional[jsii.Number]:
        '''The HAProxy client timeout in minutes.

        :default: 1
        '''
        result = self._values.get("client_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the bastionHost instance.

        :default: "BastionHost"
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group, which is attached to the bastion host.

        :default:

        If none is provided a default security group is attached, which
        doesn't allow incoming traffic and allows outbound traffic to everywhere
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def server_timeout(self) -> typing.Optional[jsii.Number]:
        '''The HAProxy server timeout in minutes.

        :default: 1
        '''
        result = self._values.get("server_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def should_patch(self) -> typing.Optional[builtins.bool]:
        '''Whether patching should be enabled for the bastion-host-forward instance.

        :default: true
        '''
        result = self._values.get("should_patch")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BastionHostForwardBaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@moia-oss/bastion-host-forward.BastionHostForwardProps",
    jsii_struct_bases=[BastionHostForwardBaseProps],
    name_mapping={
        "vpc": "vpc",
        "cached_in_context": "cachedInContext",
        "client_timeout": "clientTimeout",
        "name": "name",
        "security_group": "securityGroup",
        "server_timeout": "serverTimeout",
        "should_patch": "shouldPatch",
        "address": "address",
        "port": "port",
    },
)
class BastionHostForwardProps(BastionHostForwardBaseProps):
    def __init__(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        cached_in_context: typing.Optional[builtins.bool] = None,
        client_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        server_timeout: typing.Optional[jsii.Number] = None,
        should_patch: typing.Optional[builtins.bool] = None,
        address: builtins.str,
        port: builtins.str,
    ) -> None:
        '''
        :param vpc: The Vpc in which to instantiate the Bastion Host.
        :param cached_in_context: Whether the AMI ID is cached to be stable between deployments. By default, the newest image is used on each deployment. This will cause instances to be replaced whenever a new version is released, and may cause downtime if there aren't enough running instances in the AutoScalingGroup to reschedule the tasks on. If set to true, the AMI ID will be cached in ``cdk.context.json`` and the same value will be used on future runs. Your instances will not be replaced but your AMI version will grow old over time. To refresh the AMI lookup, you will have to evict the value from the cache using the ``cdk context`` command. See https://docs.aws.amazon.com/cdk/latest/guide/context.html for more information. Can not be set to ``true`` in environment-agnostic stacks. Default: false
        :param client_timeout: The HAProxy client timeout in minutes. Default: 1
        :param name: The name of the bastionHost instance. Default: "BastionHost"
        :param security_group: The security group, which is attached to the bastion host. Default: If none is provided a default security group is attached, which doesn't allow incoming traffic and allows outbound traffic to everywhere
        :param server_timeout: The HAProxy server timeout in minutes. Default: 1
        :param should_patch: Whether patching should be enabled for the bastion-host-forward instance. Default: true
        :param address: The address of the service to forward to.
        :param port: The port of the service to forward to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30164d00a0cf052f5697cd80ac0ac4dee62a4b9c8d27d3e52b1a4b532cfc02ed)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument cached_in_context", value=cached_in_context, expected_type=type_hints["cached_in_context"])
            check_type(argname="argument client_timeout", value=client_timeout, expected_type=type_hints["client_timeout"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument server_timeout", value=server_timeout, expected_type=type_hints["server_timeout"])
            check_type(argname="argument should_patch", value=should_patch, expected_type=type_hints["should_patch"])
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
            "address": address,
            "port": port,
        }
        if cached_in_context is not None:
            self._values["cached_in_context"] = cached_in_context
        if client_timeout is not None:
            self._values["client_timeout"] = client_timeout
        if name is not None:
            self._values["name"] = name
        if security_group is not None:
            self._values["security_group"] = security_group
        if server_timeout is not None:
            self._values["server_timeout"] = server_timeout
        if should_patch is not None:
            self._values["should_patch"] = should_patch

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The Vpc in which to instantiate the Bastion Host.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def cached_in_context(self) -> typing.Optional[builtins.bool]:
        '''Whether the AMI ID is cached to be stable between deployments.

        By default, the newest image is used on each deployment. This will cause
        instances to be replaced whenever a new version is released, and may cause
        downtime if there aren't enough running instances in the AutoScalingGroup
        to reschedule the tasks on.

        If set to true, the AMI ID will be cached in ``cdk.context.json`` and the
        same value will be used on future runs. Your instances will not be replaced
        but your AMI version will grow old over time. To refresh the AMI lookup,
        you will have to evict the value from the cache using the ``cdk context``
        command. See https://docs.aws.amazon.com/cdk/latest/guide/context.html for
        more information.

        Can not be set to ``true`` in environment-agnostic stacks.

        :default: false
        '''
        result = self._values.get("cached_in_context")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def client_timeout(self) -> typing.Optional[jsii.Number]:
        '''The HAProxy client timeout in minutes.

        :default: 1
        '''
        result = self._values.get("client_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the bastionHost instance.

        :default: "BastionHost"
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group, which is attached to the bastion host.

        :default:

        If none is provided a default security group is attached, which
        doesn't allow incoming traffic and allows outbound traffic to everywhere
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def server_timeout(self) -> typing.Optional[jsii.Number]:
        '''The HAProxy server timeout in minutes.

        :default: 1
        '''
        result = self._values.get("server_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def should_patch(self) -> typing.Optional[builtins.bool]:
        '''Whether patching should be enabled for the bastion-host-forward instance.

        :default: true
        '''
        result = self._values.get("should_patch")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def address(self) -> builtins.str:
        '''The address of the service to forward to.'''
        result = self._values.get("address")
        assert result is not None, "Required property 'address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> builtins.str:
        '''The port of the service to forward to.'''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BastionHostForwardProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BastionHostRDSForward(
    BastionHostForward,
    metaclass=jsii.JSIIMeta,
    jsii_type="@moia-oss/bastion-host-forward.BastionHostRDSForward",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        rds_instance: _aws_cdk_aws_rds_ceddda9d.IDatabaseInstance,
        iam_user: typing.Optional[builtins.str] = None,
        rds_resource_identifier: typing.Optional[builtins.str] = None,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        cached_in_context: typing.Optional[builtins.bool] = None,
        client_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        server_timeout: typing.Optional[jsii.Number] = None,
        should_patch: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param rds_instance: -
        :param iam_user: -
        :param rds_resource_identifier: -
        :param vpc: The Vpc in which to instantiate the Bastion Host.
        :param cached_in_context: Whether the AMI ID is cached to be stable between deployments. By default, the newest image is used on each deployment. This will cause instances to be replaced whenever a new version is released, and may cause downtime if there aren't enough running instances in the AutoScalingGroup to reschedule the tasks on. If set to true, the AMI ID will be cached in ``cdk.context.json`` and the same value will be used on future runs. Your instances will not be replaced but your AMI version will grow old over time. To refresh the AMI lookup, you will have to evict the value from the cache using the ``cdk context`` command. See https://docs.aws.amazon.com/cdk/latest/guide/context.html for more information. Can not be set to ``true`` in environment-agnostic stacks. Default: false
        :param client_timeout: The HAProxy client timeout in minutes. Default: 1
        :param name: The name of the bastionHost instance. Default: "BastionHost"
        :param security_group: The security group, which is attached to the bastion host. Default: If none is provided a default security group is attached, which doesn't allow incoming traffic and allows outbound traffic to everywhere
        :param server_timeout: The HAProxy server timeout in minutes. Default: 1
        :param should_patch: Whether patching should be enabled for the bastion-host-forward instance. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3847327fb9da43b4cf37d6406f666160f9f51907472bd90dff13e9b9de1d6d90)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BastionHostRDSForwardProps(
            rds_instance=rds_instance,
            iam_user=iam_user,
            rds_resource_identifier=rds_resource_identifier,
            vpc=vpc,
            cached_in_context=cached_in_context,
            client_timeout=client_timeout,
            name=name,
            security_group=security_group,
            server_timeout=server_timeout,
            should_patch=should_patch,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@moia-oss/bastion-host-forward.BastionHostRDSForwardProps",
    jsii_struct_bases=[BastionHostForwardBaseProps],
    name_mapping={
        "vpc": "vpc",
        "cached_in_context": "cachedInContext",
        "client_timeout": "clientTimeout",
        "name": "name",
        "security_group": "securityGroup",
        "server_timeout": "serverTimeout",
        "should_patch": "shouldPatch",
        "rds_instance": "rdsInstance",
        "iam_user": "iamUser",
        "rds_resource_identifier": "rdsResourceIdentifier",
    },
)
class BastionHostRDSForwardProps(BastionHostForwardBaseProps):
    def __init__(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        cached_in_context: typing.Optional[builtins.bool] = None,
        client_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        server_timeout: typing.Optional[jsii.Number] = None,
        should_patch: typing.Optional[builtins.bool] = None,
        rds_instance: _aws_cdk_aws_rds_ceddda9d.IDatabaseInstance,
        iam_user: typing.Optional[builtins.str] = None,
        rds_resource_identifier: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param vpc: The Vpc in which to instantiate the Bastion Host.
        :param cached_in_context: Whether the AMI ID is cached to be stable between deployments. By default, the newest image is used on each deployment. This will cause instances to be replaced whenever a new version is released, and may cause downtime if there aren't enough running instances in the AutoScalingGroup to reschedule the tasks on. If set to true, the AMI ID will be cached in ``cdk.context.json`` and the same value will be used on future runs. Your instances will not be replaced but your AMI version will grow old over time. To refresh the AMI lookup, you will have to evict the value from the cache using the ``cdk context`` command. See https://docs.aws.amazon.com/cdk/latest/guide/context.html for more information. Can not be set to ``true`` in environment-agnostic stacks. Default: false
        :param client_timeout: The HAProxy client timeout in minutes. Default: 1
        :param name: The name of the bastionHost instance. Default: "BastionHost"
        :param security_group: The security group, which is attached to the bastion host. Default: If none is provided a default security group is attached, which doesn't allow incoming traffic and allows outbound traffic to everywhere
        :param server_timeout: The HAProxy server timeout in minutes. Default: 1
        :param should_patch: Whether patching should be enabled for the bastion-host-forward instance. Default: true
        :param rds_instance: -
        :param iam_user: -
        :param rds_resource_identifier: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7dbab271b63ea7d6be765aea7463ecd9d0edb5d6e798b1a345f223a01f95939)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument cached_in_context", value=cached_in_context, expected_type=type_hints["cached_in_context"])
            check_type(argname="argument client_timeout", value=client_timeout, expected_type=type_hints["client_timeout"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument server_timeout", value=server_timeout, expected_type=type_hints["server_timeout"])
            check_type(argname="argument should_patch", value=should_patch, expected_type=type_hints["should_patch"])
            check_type(argname="argument rds_instance", value=rds_instance, expected_type=type_hints["rds_instance"])
            check_type(argname="argument iam_user", value=iam_user, expected_type=type_hints["iam_user"])
            check_type(argname="argument rds_resource_identifier", value=rds_resource_identifier, expected_type=type_hints["rds_resource_identifier"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
            "rds_instance": rds_instance,
        }
        if cached_in_context is not None:
            self._values["cached_in_context"] = cached_in_context
        if client_timeout is not None:
            self._values["client_timeout"] = client_timeout
        if name is not None:
            self._values["name"] = name
        if security_group is not None:
            self._values["security_group"] = security_group
        if server_timeout is not None:
            self._values["server_timeout"] = server_timeout
        if should_patch is not None:
            self._values["should_patch"] = should_patch
        if iam_user is not None:
            self._values["iam_user"] = iam_user
        if rds_resource_identifier is not None:
            self._values["rds_resource_identifier"] = rds_resource_identifier

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The Vpc in which to instantiate the Bastion Host.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def cached_in_context(self) -> typing.Optional[builtins.bool]:
        '''Whether the AMI ID is cached to be stable between deployments.

        By default, the newest image is used on each deployment. This will cause
        instances to be replaced whenever a new version is released, and may cause
        downtime if there aren't enough running instances in the AutoScalingGroup
        to reschedule the tasks on.

        If set to true, the AMI ID will be cached in ``cdk.context.json`` and the
        same value will be used on future runs. Your instances will not be replaced
        but your AMI version will grow old over time. To refresh the AMI lookup,
        you will have to evict the value from the cache using the ``cdk context``
        command. See https://docs.aws.amazon.com/cdk/latest/guide/context.html for
        more information.

        Can not be set to ``true`` in environment-agnostic stacks.

        :default: false
        '''
        result = self._values.get("cached_in_context")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def client_timeout(self) -> typing.Optional[jsii.Number]:
        '''The HAProxy client timeout in minutes.

        :default: 1
        '''
        result = self._values.get("client_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the bastionHost instance.

        :default: "BastionHost"
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group, which is attached to the bastion host.

        :default:

        If none is provided a default security group is attached, which
        doesn't allow incoming traffic and allows outbound traffic to everywhere
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def server_timeout(self) -> typing.Optional[jsii.Number]:
        '''The HAProxy server timeout in minutes.

        :default: 1
        '''
        result = self._values.get("server_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def should_patch(self) -> typing.Optional[builtins.bool]:
        '''Whether patching should be enabled for the bastion-host-forward instance.

        :default: true
        '''
        result = self._values.get("should_patch")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def rds_instance(self) -> _aws_cdk_aws_rds_ceddda9d.IDatabaseInstance:
        result = self._values.get("rds_instance")
        assert result is not None, "Required property 'rds_instance' is missing"
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.IDatabaseInstance, result)

    @builtins.property
    def iam_user(self) -> typing.Optional[builtins.str]:
        result = self._values.get("iam_user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rds_resource_identifier(self) -> typing.Optional[builtins.str]:
        result = self._values.get("rds_resource_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BastionHostRDSForwardProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenericBastionHostForward(
    BastionHostForward,
    metaclass=jsii.JSIIMeta,
    jsii_type="@moia-oss/bastion-host-forward.GenericBastionHostForward",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        address: builtins.str,
        port: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        cached_in_context: typing.Optional[builtins.bool] = None,
        client_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        server_timeout: typing.Optional[jsii.Number] = None,
        should_patch: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param address: The address of the service to forward to.
        :param port: The port of the service to forward to.
        :param vpc: The Vpc in which to instantiate the Bastion Host.
        :param cached_in_context: Whether the AMI ID is cached to be stable between deployments. By default, the newest image is used on each deployment. This will cause instances to be replaced whenever a new version is released, and may cause downtime if there aren't enough running instances in the AutoScalingGroup to reschedule the tasks on. If set to true, the AMI ID will be cached in ``cdk.context.json`` and the same value will be used on future runs. Your instances will not be replaced but your AMI version will grow old over time. To refresh the AMI lookup, you will have to evict the value from the cache using the ``cdk context`` command. See https://docs.aws.amazon.com/cdk/latest/guide/context.html for more information. Can not be set to ``true`` in environment-agnostic stacks. Default: false
        :param client_timeout: The HAProxy client timeout in minutes. Default: 1
        :param name: The name of the bastionHost instance. Default: "BastionHost"
        :param security_group: The security group, which is attached to the bastion host. Default: If none is provided a default security group is attached, which doesn't allow incoming traffic and allows outbound traffic to everywhere
        :param server_timeout: The HAProxy server timeout in minutes. Default: 1
        :param should_patch: Whether patching should be enabled for the bastion-host-forward instance. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32175009b96f15c03c65e2dec1ec2f47300c435cacd861547ef1867470e3dd2e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BastionHostForwardProps(
            address=address,
            port=port,
            vpc=vpc,
            cached_in_context=cached_in_context,
            client_timeout=client_timeout,
            name=name,
            security_group=security_group,
            server_timeout=server_timeout,
            should_patch=should_patch,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class BastionHostAuroraServerlessForward(
    BastionHostForward,
    metaclass=jsii.JSIIMeta,
    jsii_type="@moia-oss/bastion-host-forward.BastionHostAuroraServerlessForward",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        serverless_cluster: _aws_cdk_aws_rds_ceddda9d.IServerlessCluster,
        iam_user: typing.Optional[builtins.str] = None,
        resource_identifier: typing.Optional[builtins.str] = None,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        cached_in_context: typing.Optional[builtins.bool] = None,
        client_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        server_timeout: typing.Optional[jsii.Number] = None,
        should_patch: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param serverless_cluster: -
        :param iam_user: -
        :param resource_identifier: -
        :param vpc: The Vpc in which to instantiate the Bastion Host.
        :param cached_in_context: Whether the AMI ID is cached to be stable between deployments. By default, the newest image is used on each deployment. This will cause instances to be replaced whenever a new version is released, and may cause downtime if there aren't enough running instances in the AutoScalingGroup to reschedule the tasks on. If set to true, the AMI ID will be cached in ``cdk.context.json`` and the same value will be used on future runs. Your instances will not be replaced but your AMI version will grow old over time. To refresh the AMI lookup, you will have to evict the value from the cache using the ``cdk context`` command. See https://docs.aws.amazon.com/cdk/latest/guide/context.html for more information. Can not be set to ``true`` in environment-agnostic stacks. Default: false
        :param client_timeout: The HAProxy client timeout in minutes. Default: 1
        :param name: The name of the bastionHost instance. Default: "BastionHost"
        :param security_group: The security group, which is attached to the bastion host. Default: If none is provided a default security group is attached, which doesn't allow incoming traffic and allows outbound traffic to everywhere
        :param server_timeout: The HAProxy server timeout in minutes. Default: 1
        :param should_patch: Whether patching should be enabled for the bastion-host-forward instance. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6dbf63ea4674068f1d8735806d95e71339efd56d3120b8a70f5d5d41ba57e55)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BastionHostAuroraServerlessForwardProps(
            serverless_cluster=serverless_cluster,
            iam_user=iam_user,
            resource_identifier=resource_identifier,
            vpc=vpc,
            cached_in_context=cached_in_context,
            client_timeout=client_timeout,
            name=name,
            security_group=security_group,
            server_timeout=server_timeout,
            should_patch=should_patch,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@moia-oss/bastion-host-forward.BastionHostAuroraServerlessForwardProps",
    jsii_struct_bases=[BastionHostForwardBaseProps],
    name_mapping={
        "vpc": "vpc",
        "cached_in_context": "cachedInContext",
        "client_timeout": "clientTimeout",
        "name": "name",
        "security_group": "securityGroup",
        "server_timeout": "serverTimeout",
        "should_patch": "shouldPatch",
        "serverless_cluster": "serverlessCluster",
        "iam_user": "iamUser",
        "resource_identifier": "resourceIdentifier",
    },
)
class BastionHostAuroraServerlessForwardProps(BastionHostForwardBaseProps):
    def __init__(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        cached_in_context: typing.Optional[builtins.bool] = None,
        client_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        server_timeout: typing.Optional[jsii.Number] = None,
        should_patch: typing.Optional[builtins.bool] = None,
        serverless_cluster: _aws_cdk_aws_rds_ceddda9d.IServerlessCluster,
        iam_user: typing.Optional[builtins.str] = None,
        resource_identifier: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param vpc: The Vpc in which to instantiate the Bastion Host.
        :param cached_in_context: Whether the AMI ID is cached to be stable between deployments. By default, the newest image is used on each deployment. This will cause instances to be replaced whenever a new version is released, and may cause downtime if there aren't enough running instances in the AutoScalingGroup to reschedule the tasks on. If set to true, the AMI ID will be cached in ``cdk.context.json`` and the same value will be used on future runs. Your instances will not be replaced but your AMI version will grow old over time. To refresh the AMI lookup, you will have to evict the value from the cache using the ``cdk context`` command. See https://docs.aws.amazon.com/cdk/latest/guide/context.html for more information. Can not be set to ``true`` in environment-agnostic stacks. Default: false
        :param client_timeout: The HAProxy client timeout in minutes. Default: 1
        :param name: The name of the bastionHost instance. Default: "BastionHost"
        :param security_group: The security group, which is attached to the bastion host. Default: If none is provided a default security group is attached, which doesn't allow incoming traffic and allows outbound traffic to everywhere
        :param server_timeout: The HAProxy server timeout in minutes. Default: 1
        :param should_patch: Whether patching should be enabled for the bastion-host-forward instance. Default: true
        :param serverless_cluster: -
        :param iam_user: -
        :param resource_identifier: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b80e1470b9e027c01879a6543d472b954aba0362e06520bf1f6b428782ed2ad)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument cached_in_context", value=cached_in_context, expected_type=type_hints["cached_in_context"])
            check_type(argname="argument client_timeout", value=client_timeout, expected_type=type_hints["client_timeout"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument server_timeout", value=server_timeout, expected_type=type_hints["server_timeout"])
            check_type(argname="argument should_patch", value=should_patch, expected_type=type_hints["should_patch"])
            check_type(argname="argument serverless_cluster", value=serverless_cluster, expected_type=type_hints["serverless_cluster"])
            check_type(argname="argument iam_user", value=iam_user, expected_type=type_hints["iam_user"])
            check_type(argname="argument resource_identifier", value=resource_identifier, expected_type=type_hints["resource_identifier"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
            "serverless_cluster": serverless_cluster,
        }
        if cached_in_context is not None:
            self._values["cached_in_context"] = cached_in_context
        if client_timeout is not None:
            self._values["client_timeout"] = client_timeout
        if name is not None:
            self._values["name"] = name
        if security_group is not None:
            self._values["security_group"] = security_group
        if server_timeout is not None:
            self._values["server_timeout"] = server_timeout
        if should_patch is not None:
            self._values["should_patch"] = should_patch
        if iam_user is not None:
            self._values["iam_user"] = iam_user
        if resource_identifier is not None:
            self._values["resource_identifier"] = resource_identifier

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The Vpc in which to instantiate the Bastion Host.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def cached_in_context(self) -> typing.Optional[builtins.bool]:
        '''Whether the AMI ID is cached to be stable between deployments.

        By default, the newest image is used on each deployment. This will cause
        instances to be replaced whenever a new version is released, and may cause
        downtime if there aren't enough running instances in the AutoScalingGroup
        to reschedule the tasks on.

        If set to true, the AMI ID will be cached in ``cdk.context.json`` and the
        same value will be used on future runs. Your instances will not be replaced
        but your AMI version will grow old over time. To refresh the AMI lookup,
        you will have to evict the value from the cache using the ``cdk context``
        command. See https://docs.aws.amazon.com/cdk/latest/guide/context.html for
        more information.

        Can not be set to ``true`` in environment-agnostic stacks.

        :default: false
        '''
        result = self._values.get("cached_in_context")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def client_timeout(self) -> typing.Optional[jsii.Number]:
        '''The HAProxy client timeout in minutes.

        :default: 1
        '''
        result = self._values.get("client_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the bastionHost instance.

        :default: "BastionHost"
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group, which is attached to the bastion host.

        :default:

        If none is provided a default security group is attached, which
        doesn't allow incoming traffic and allows outbound traffic to everywhere
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def server_timeout(self) -> typing.Optional[jsii.Number]:
        '''The HAProxy server timeout in minutes.

        :default: 1
        '''
        result = self._values.get("server_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def should_patch(self) -> typing.Optional[builtins.bool]:
        '''Whether patching should be enabled for the bastion-host-forward instance.

        :default: true
        '''
        result = self._values.get("should_patch")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def serverless_cluster(self) -> _aws_cdk_aws_rds_ceddda9d.IServerlessCluster:
        result = self._values.get("serverless_cluster")
        assert result is not None, "Required property 'serverless_cluster' is missing"
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.IServerlessCluster, result)

    @builtins.property
    def iam_user(self) -> typing.Optional[builtins.str]:
        result = self._values.get("iam_user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_identifier(self) -> typing.Optional[builtins.str]:
        result = self._values.get("resource_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BastionHostAuroraServerlessForwardProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BastionHostAuroraServerlessForward",
    "BastionHostAuroraServerlessForwardProps",
    "BastionHostForward",
    "BastionHostForwardBaseProps",
    "BastionHostForwardProps",
    "BastionHostRDSForward",
    "BastionHostRDSForwardProps",
    "GenericBastionHostForward",
]

publication.publish()

def _typecheckingstub__11d2abdf217ee36451e346fc935fa9cf68c35b672a0da8fe74b9f254090f5ebc(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    address: builtins.str,
    port: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    cached_in_context: typing.Optional[builtins.bool] = None,
    client_timeout: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    server_timeout: typing.Optional[jsii.Number] = None,
    should_patch: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0aa8ec88289bd4e63d045aa01c31796f7d8df6f7e8c61e5a1635d7c38d19657b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f1513e49883dc7160b0953eba3100220e268a94d25b73bb69473c19b8a60f14(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbe10306f21028866820c653f2ff1bf09db7797c5923ab094d25cb3942a322c0(
    value: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f293a86cd803ccc93821f68fa9a4ce7a663457599c3ff2d33b88bafb430fae0(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    cached_in_context: typing.Optional[builtins.bool] = None,
    client_timeout: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    server_timeout: typing.Optional[jsii.Number] = None,
    should_patch: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30164d00a0cf052f5697cd80ac0ac4dee62a4b9c8d27d3e52b1a4b532cfc02ed(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    cached_in_context: typing.Optional[builtins.bool] = None,
    client_timeout: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    server_timeout: typing.Optional[jsii.Number] = None,
    should_patch: typing.Optional[builtins.bool] = None,
    address: builtins.str,
    port: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3847327fb9da43b4cf37d6406f666160f9f51907472bd90dff13e9b9de1d6d90(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    rds_instance: _aws_cdk_aws_rds_ceddda9d.IDatabaseInstance,
    iam_user: typing.Optional[builtins.str] = None,
    rds_resource_identifier: typing.Optional[builtins.str] = None,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    cached_in_context: typing.Optional[builtins.bool] = None,
    client_timeout: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    server_timeout: typing.Optional[jsii.Number] = None,
    should_patch: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7dbab271b63ea7d6be765aea7463ecd9d0edb5d6e798b1a345f223a01f95939(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    cached_in_context: typing.Optional[builtins.bool] = None,
    client_timeout: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    server_timeout: typing.Optional[jsii.Number] = None,
    should_patch: typing.Optional[builtins.bool] = None,
    rds_instance: _aws_cdk_aws_rds_ceddda9d.IDatabaseInstance,
    iam_user: typing.Optional[builtins.str] = None,
    rds_resource_identifier: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32175009b96f15c03c65e2dec1ec2f47300c435cacd861547ef1867470e3dd2e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    address: builtins.str,
    port: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    cached_in_context: typing.Optional[builtins.bool] = None,
    client_timeout: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    server_timeout: typing.Optional[jsii.Number] = None,
    should_patch: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6dbf63ea4674068f1d8735806d95e71339efd56d3120b8a70f5d5d41ba57e55(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    serverless_cluster: _aws_cdk_aws_rds_ceddda9d.IServerlessCluster,
    iam_user: typing.Optional[builtins.str] = None,
    resource_identifier: typing.Optional[builtins.str] = None,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    cached_in_context: typing.Optional[builtins.bool] = None,
    client_timeout: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    server_timeout: typing.Optional[jsii.Number] = None,
    should_patch: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b80e1470b9e027c01879a6543d472b954aba0362e06520bf1f6b428782ed2ad(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    cached_in_context: typing.Optional[builtins.bool] = None,
    client_timeout: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    server_timeout: typing.Optional[jsii.Number] = None,
    should_patch: typing.Optional[builtins.bool] = None,
    serverless_cluster: _aws_cdk_aws_rds_ceddda9d.IServerlessCluster,
    iam_user: typing.Optional[builtins.str] = None,
    resource_identifier: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
