'''
# Amazon OpenSearch Serverless Construct Library

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@cdklabs/generative-ai-cdk-constructs`|

This construct library extends the [automatically generated L1 constructs](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_opensearchserverless-readme.html) to provide an L2 construct for a vector collection.

## Table of contents

* [API](#api)
* [Vector Collection](#vector-collection)

## API

See the [API documentation](../../../apidocs/modules/opensearchserverless.md).

## Vector Collection

This resource creates an Amazon OpenSearch Serverless collection configured for `VECTORSEARCH`. It creates default encryption, network, and data policies for use with Amazon Bedrock Knowledge Bases. For encryption, it uses the default AWS owned KMS key. It allows network connections from the public internet, but access is restricted to specific IAM principals.

### Granting Data Access

The `grantDataAccess` method grants the specified role access to read and write the data in the collection.
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

from .._jsii import *

import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_opensearchserverless as _aws_cdk_aws_opensearchserverless_ceddda9d
import constructs as _constructs_77d1e7e8


class VectorCollection(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/generative-ai-cdk-constructs.opensearchserverless.VectorCollection",
):
    '''(experimental) Deploys an OpenSearch Serverless Collection to be used as a vector store.

    It includes all policies.

    :stability: experimental
    '''

    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8b5d04fb7b72dad69932d437e1081404a6e72cb7ba26b7a53f6a739062e8d10)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @jsii.member(jsii_name="grantDataAccess")
    def grant_data_access(self, grantee: _aws_cdk_aws_iam_ceddda9d.IRole) -> None:
        '''(experimental) Grants the specified role access to data in the collection.

        :param grantee: The role to grant access to.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c320f537c9d5613bd4eb9158b6f299c7e1d9bbb4f3f8d0c9ad66b1f31b3fb013)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantDataAccess", [grantee]))

    @builtins.property
    @jsii.member(jsii_name="aossPolicy")
    def aoss_policy(self) -> _aws_cdk_aws_iam_ceddda9d.ManagedPolicy:
        '''(experimental) An IAM policy that allows API access to the collection.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.ManagedPolicy, jsii.get(self, "aossPolicy"))

    @aoss_policy.setter
    def aoss_policy(self, value: _aws_cdk_aws_iam_ceddda9d.ManagedPolicy) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41e6b1b914ecb08f8add2426201fb5b172a5496e41d55879a9893e923d69e785)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aossPolicy", value)

    @builtins.property
    @jsii.member(jsii_name="collectionArn")
    def collection_arn(self) -> builtins.str:
        '''(experimental) The ARN of the collection.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "collectionArn"))

    @collection_arn.setter
    def collection_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__345d8f58416dc282452d28f65ded785c6ca5ea312386630b253c0b93f77bb70d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "collectionArn", value)

    @builtins.property
    @jsii.member(jsii_name="collectionId")
    def collection_id(self) -> builtins.str:
        '''(experimental) The ID of the collection.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "collectionId"))

    @collection_id.setter
    def collection_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1abc38143c045f29ad4aad4050a02395094f115c30f78638bc317f2bd10eda3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "collectionId", value)

    @builtins.property
    @jsii.member(jsii_name="collectionName")
    def collection_name(self) -> builtins.str:
        '''(experimental) The name of the collection.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "collectionName"))

    @collection_name.setter
    def collection_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d681c75e2c727fed94552b17f76e3eeb61763bf17fbeb7302ab6f36d0b6e943)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "collectionName", value)

    @builtins.property
    @jsii.member(jsii_name="dataAccessPolicy")
    def data_access_policy(
        self,
    ) -> _aws_cdk_aws_opensearchserverless_ceddda9d.CfnAccessPolicy:
        '''(experimental) An OpenSearch Access Policy that allows access to the index.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_opensearchserverless_ceddda9d.CfnAccessPolicy, jsii.get(self, "dataAccessPolicy"))

    @data_access_policy.setter
    def data_access_policy(
        self,
        value: _aws_cdk_aws_opensearchserverless_ceddda9d.CfnAccessPolicy,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__064b48f9a1698a63c4504ba3a91564cd33e089498d79ec502bdd747c6ce09294)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataAccessPolicy", value)


__all__ = [
    "VectorCollection",
]

publication.publish()

def _typecheckingstub__c8b5d04fb7b72dad69932d437e1081404a6e72cb7ba26b7a53f6a739062e8d10(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c320f537c9d5613bd4eb9158b6f299c7e1d9bbb4f3f8d0c9ad66b1f31b3fb013(
    grantee: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41e6b1b914ecb08f8add2426201fb5b172a5496e41d55879a9893e923d69e785(
    value: _aws_cdk_aws_iam_ceddda9d.ManagedPolicy,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__345d8f58416dc282452d28f65ded785c6ca5ea312386630b253c0b93f77bb70d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1abc38143c045f29ad4aad4050a02395094f115c30f78638bc317f2bd10eda3b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d681c75e2c727fed94552b17f76e3eeb61763bf17fbeb7302ab6f36d0b6e943(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__064b48f9a1698a63c4504ba3a91564cd33e089498d79ec502bdd747c6ce09294(
    value: _aws_cdk_aws_opensearchserverless_ceddda9d.CfnAccessPolicy,
) -> None:
    """Type checking stubs"""
    pass
