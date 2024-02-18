'''
# AWS Generative AI CDK Constructs

![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---


[![View on Construct Hub](https://constructs.dev/badge?package=generative-ai-cdk-constructs)](https://constructs.dev/packages/@cdklabs/generative-ai-cdk-constructs)

[![PyPI version](https://img.shields.io/pypi/v/cdklabs.generative-ai-cdk-constructs)](https://pypi.org/project/cdklabs.generative-ai-cdk-constructs/)
[![npm version](https://img.shields.io/npm/v/@cdklabs/generative-ai-cdk-constructs)](https://www.npmjs.com/package/@cdklabs/generative-ai-cdk-constructs)

## Table of contents

* [Introduction](#introduction)
* [CDK Versions](#cdk-versions)
* [Contributing](#contributing)
* [Adding new constructs](#design-guidelines-and-development-guide)
* [Getting Started](#getting-started)
* [Catalog](#catalog)
* [Sample Use Cases](#sample-use-cases)
* [Additional Resources](#additional-resources)
* [Operational Metrics Collection](#operational-metrics-collection)
* [Roadmap](#roadmap)
* [Legal Disclaimer](#legal-disclaimer)

# Introduction

The AWS Generative AI Constructs Library is an open-source extension of the [AWS Cloud Development Kit (AWS CDK)](https://docs.aws.amazon.com/cdk/v2/guide/home.html) that provides multi-service, well-architected patterns for quickly defining solutions in code to create predictable and repeatable infrastructure, called [constructs](https://docs.aws.amazon.com/cdk/v2/guide/constructs.html). The goal of AWS Generative AI CDK Constructs is to help developers build generative AI solutions using pattern-based definitions for their architecture.

The patterns defined in AWS Generative AI CDK Constructs are high level, multi-service abstractions of AWS CDK constructs that have default configurations based on well-architected best practices. The library is organized into logical modules using object-oriented techniques to create each architectural pattern model.

# CDK Versions

AWS Generative AI CDK Constructs and the AWS CDK are independent teams and have different release schedules. Each release of AWS Generative AI CDK Constructs is built against a specific version of the AWS CDK. The [CHANGELOG.md](./CHANGELOG.md) file lists the CDK version associated with each AWS Generative AI Constructs release. For instance, AWS Generative AI CDK Constructs v0.0.0 was built against AWS CDK v2.96.2. This means that to use AWS Generative AI CDK Constructs v0.0.0, your application must include AWS CDK v2.96.2 or later. You can continue to use the latest AWS CDK versions and upgrade the your AWS Generative AI CDK Constructs version when new releases become available.

# Contributing

Contributions of all kinds are welcome! Check out our [contributor guide](./CONTRIBUTING.md)

# Design guidelines and Development guide

If you want to add a new construct to the library, check out our [design guidelines](./DESIGN_GUIDELINES.md), then follow the [development guide](./DEVELOPER_GUIDE.md)

# Getting Started

#### For TypeScript:

* Create or use an existing CDK application in TypeScript.

  * `cdk init app --language typescript`
* Run `npm install @cdklabs/generative-ai-cdk-constructs`
* The package should be added to your package.json.
* Import the library:

  * `import * as genai from '@cdklabs/generative-ai-cdk-constructs';`

#### For Python:

* Create or use an existing CDK application in Python

  * `cdk init app --language python`
* Install the package:

  * `pip install cdklabs.generative-ai-cdk-constructs`
* Import the library:

  * `import cdklabs.generative_ai_cdk_constructs`

Refer to the documentation for additional guidance on a particular construct: [Catalog](#catalog)

# Catalog

The following constructs are available in the library:

| **Construct** |Description| AWS Services used |
|:-------------|:-------------|:-------------|
| [Data ingestion pipeline](./src/patterns/gen-ai/aws-rag-appsync-stepfn-opensearch/) | Ingestion pipeline providing a RAG (retrieval augmented generation) source for storing documents in a knowledge base. | Amazon OpenSearch, AWS Step Functions, Amazon Bedrock, AWS AppSync, AWS Lambda |
| [Question answering](./src/patterns/gen-ai/aws-qa-appsync-opensearch/) | Question answering with a large language model (Anthropic Claude V2.1) using a RAG (retrieval augmented generation) source and/or long context. | Amazon OpenSearch, AWS Lambda, Amazon Bedrock, AWS AppSync |
| [Summarization](./src/patterns/gen-ai/aws-summarization-appsync-stepfn/) | Document summarization with a large language model (Anthropic Claude V2.1). | AWS Lambda, Amazon Bedrock, AWS AppSync and Amazon Elasticache for Redis.  |
| [Lambda layer](./src/patterns/gen-ai/aws-langchain-common-layer/) | Python Lambda layer providing dependencies and utilities to develop generative AI applications on AWS. | AWS Lambda, Amazon Bedrock, Amazon SageMaker |
| [SageMaker model deployment (Jumpstart)](./src/patterns/gen-ai/aws-model-deployment-sagemaker/README_jumpstart.md) | Deploy a foundation model from Amazon SageMaker JumpStart to an Amazon SageMaker endpoint. | Amazon SageMaker |
| [SageMaker model deployment (Hugging Face)](./src/patterns/gen-ai/aws-model-deployment-sagemaker/README_hugging_face.md) | Deploy a foundation model from Hugging Face to an Amazon SageMaker endpoint. | Amazon SageMaker |
| [SageMaker model deployment (Custom)](./src/patterns/gen-ai/aws-model-deployment-sagemaker/README_custom_sagemaker_endpoint.md) | Deploy a foundation model from an S3 location to an Amazon SageMaker endpoint. | Amazon SageMaker |
| [Amazon Bedrock](./src/cdk-lib/bedrock/README.md) | CDK L2 Constructs for Amazon Bedrock | Amazon Bedrock, Amazon OpenSearch Serverless, AWS Lambda |
| [Amazon OpenSearch Serverless Vector Collection](./src/cdk-lib/opensearchserverless/README.md) | CDK L2 Constructs to create a vector collection | Amazon OpenSearch Vector Index |
| [Amazon OpenSearch Vector Index](./src/cdk-lib/opensearch-vectorindex/README.md) | CDK L1 Custom Resource to create a vector index | Amazon OpenSearch Serverless, AWS Lambda |

# Sample Use Cases

The official samples repository https://github.com/aws-samples/generative-ai-cdk-constructs-samples includes a collection of functional use case implementations to demonstrate the usage of AWS Generative AI CDK Constructs. These can be used in the same way as architectural patterns, and can be conceptualized as an additional "higher-level" abstraction of those patterns. Those patterns (constructs) are composed together into [stacks](https://docs.aws.amazon.com/cdk/latest/guide/stacks.html), forming a "CDK app".

# Additional Resources

| Resource |Description|
|:-------------|:-------------|
| [AWS re:Invent 2023 - Keynote with Dr. Werner Vogels](https://youtu.be/UTRBVPvzt9w?t=6252) | Dr. Werner Vogels, Amazon.com's VP and CTO, announces the AWS Generative AI CDK Constructs during his AWS re:Invent 2023 keynote. |
| [aws-cdk-stack-builder-tool](https://github.com/aws-samples/aws-cdk-stack-builder-tool) | AWS CDK Builder is a browser-based tool designed to streamline bootstrapping of Infrastructure as Code (IaC) projects using the AWS Cloud Development Kit (CDK). |
| [CDK Live! Building generative AI applications and architectures leveraging AWS CDK Constructs!](https://www.youtube.com/watch?v=NI1F4Xxqyr8) | CDK Live! episode focused on building and deploying generative AI applications and architectures on AWS using the AWS Cloud Development Kit (CDK) and the AWS Generative AI CDK Constructs. |
| [Announcing AWS Generative AI CDK Constructs!](https://aws.amazon.com/blogs/devops/announcing-generative-ai-cdk-constructs/) | Blog post announcing the release of the AWS Generative AI CDK Constructs. |
| [aws-genai-llm-chatbot](https://github.com/aws-samples/aws-genai-llm-chatbot/tree/main) | Multi-Model and Multi-RAG Powered Chatbot Using AWS CDK on AWS allowing you to experiment with a variety of Large Language Models and Multimodal Language Models, settings and prompts in your own AWS account |

# Operational Metrics Collection

Provided CDK constructs collect anonymous operational metrics to help AWS improve the quality and features of the constructs. Data collection is subject to the AWS Privacy Policy (https://aws.amazon.com/privacy/). To opt out of this feature, simply disable it by setting the construct property "enableOperationalMetric" to false for each construct used. Defaults to true.

# Roadmap

Roadmap is available through the [GitHub Project](https://github.com/orgs/awslabs/projects/136)

# Legal Disclaimer

You should consider doing your own independent assessment before using the content in this library for production purposes. This may include (amongst other things) testing, securing, and optimizing the CDK constructs and other content, provided in this library, based on your specific quality control practices and standards.

---


© Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_appsync as _aws_cdk_aws_appsync_ceddda9d
import aws_cdk.aws_cognito as _aws_cdk_aws_cognito_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_ecr as _aws_cdk_aws_ecr_ceddda9d
import aws_cdk.aws_ecr_assets as _aws_cdk_aws_ecr_assets_ceddda9d
import aws_cdk.aws_elasticache as _aws_cdk_aws_elasticache_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_opensearchserverless as _aws_cdk_aws_opensearchserverless_ceddda9d
import aws_cdk.aws_opensearchservice as _aws_cdk_aws_opensearchservice_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_sagemaker as _aws_cdk_aws_sagemaker_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import aws_cdk.aws_stepfunctions as _aws_cdk_aws_stepfunctions_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@cdklabs/generative-ai-cdk-constructs.AdapterProps",
    jsii_struct_bases=[],
    name_mapping={
        "compatible_architectures": "compatibleArchitectures",
        "compatible_runtimes": "compatibleRuntimes",
        "description": "description",
        "layer_version_name": "layerVersionName",
        "license": "license",
        "removal_policy": "removalPolicy",
    },
)
class AdapterProps:
    def __init__(
        self,
        *,
        compatible_architectures: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.Architecture]] = None,
        compatible_runtimes: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.Runtime]] = None,
        description: typing.Optional[builtins.str] = None,
        layer_version_name: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''(experimental) AdapterProps.

        :param compatible_architectures: The system architectures compatible with this layer. Default: [Architecture.X86_64]
        :param compatible_runtimes: The runtimes compatible with this Layer. Default: - All runtimes are supported.
        :param description: The description the this Lambda Layer. Default: - No description.
        :param layer_version_name: The name of the layer. Default: - A name will be generated.
        :param license: The SPDX licence identifier or URL to the license file for this layer. Default: - No license information will be recorded.
        :param removal_policy: Whether to retain this version of the layer when a new version is added or when the stack is deleted. Default: RemovalPolicy.DESTROY

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14940da981f24c52deaeac165bd230136ed11f0570a4f7e7b9cb9ce527771c1e)
            check_type(argname="argument compatible_architectures", value=compatible_architectures, expected_type=type_hints["compatible_architectures"])
            check_type(argname="argument compatible_runtimes", value=compatible_runtimes, expected_type=type_hints["compatible_runtimes"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument layer_version_name", value=layer_version_name, expected_type=type_hints["layer_version_name"])
            check_type(argname="argument license", value=license, expected_type=type_hints["license"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if compatible_architectures is not None:
            self._values["compatible_architectures"] = compatible_architectures
        if compatible_runtimes is not None:
            self._values["compatible_runtimes"] = compatible_runtimes
        if description is not None:
            self._values["description"] = description
        if layer_version_name is not None:
            self._values["layer_version_name"] = layer_version_name
        if license is not None:
            self._values["license"] = license
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def compatible_architectures(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.Architecture]]:
        '''The system architectures compatible with this layer.

        :default: [Architecture.X86_64]
        '''
        result = self._values.get("compatible_architectures")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.Architecture]], result)

    @builtins.property
    def compatible_runtimes(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.Runtime]]:
        '''The runtimes compatible with this Layer.

        :default: - All runtimes are supported.
        '''
        result = self._values.get("compatible_runtimes")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.Runtime]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description the this Lambda Layer.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def layer_version_name(self) -> typing.Optional[builtins.str]:
        '''The name of the layer.

        :default: - A name will be generated.
        '''
        result = self._values.get("layer_version_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''The SPDX licence identifier or URL to the license file for this layer.

        :default: - No license information will be recorded.
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Whether to retain this version of the layer when a new version is added or when the stack is deleted.

        :default: RemovalPolicy.DESTROY
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AdapterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ContainerImage(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdklabs/generative-ai-cdk-constructs.ContainerImage",
):
    '''(experimental) https://github.com/aws/deep-learning-containers/blob/master/available_images.md.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromAsset")
    @builtins.classmethod
    def from_asset(
        cls,
        directory: builtins.str,
        *,
        asset_name: typing.Optional[builtins.str] = None,
        build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        build_secrets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        build_ssh: typing.Optional[builtins.str] = None,
        cache_from: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecr_assets_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]]] = None,
        cache_to: typing.Optional[typing.Union[_aws_cdk_aws_ecr_assets_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]] = None,
        file: typing.Optional[builtins.str] = None,
        invalidation: typing.Optional[typing.Union[_aws_cdk_aws_ecr_assets_ceddda9d.DockerImageAssetInvalidationOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        network_mode: typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.NetworkMode] = None,
        outputs: typing.Optional[typing.Sequence[builtins.str]] = None,
        platform: typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.Platform] = None,
        target: typing.Optional[builtins.str] = None,
        extra_hash: typing.Optional[builtins.str] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        follow_symlinks: typing.Optional[_aws_cdk_ceddda9d.SymlinkFollowMode] = None,
        ignore_mode: typing.Optional[_aws_cdk_ceddda9d.IgnoreMode] = None,
    ) -> "ContainerImage":
        '''
        :param directory: -
        :param asset_name: Unique identifier of the docker image asset and its potential revisions. Required if using AppScopedStagingSynthesizer. Default: - no asset name
        :param build_args: Build args to pass to the ``docker build`` command. Since Docker build arguments are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Default: - no build args are passed
        :param build_secrets: Build secrets. Docker BuildKit must be enabled to use build secrets. Default: - no build secrets
        :param build_ssh: SSH agent socket or keys to pass to the ``docker build`` command. Docker BuildKit must be enabled to use the ssh flag Default: - no --ssh flag
        :param cache_from: Cache from options to pass to the ``docker build`` command. Default: - no cache from options are passed to the build command
        :param cache_to: Cache to options to pass to the ``docker build`` command. Default: - no cache to options are passed to the build command
        :param file: Path to the Dockerfile (relative to the directory). Default: 'Dockerfile'
        :param invalidation: Options to control which parameters are used to invalidate the asset hash. Default: - hash all parameters
        :param network_mode: Networking mode for the RUN commands during build. Support docker API 1.25+. Default: - no networking mode specified (the default networking mode ``NetworkMode.DEFAULT`` will be used)
        :param outputs: Outputs to pass to the ``docker build`` command. Default: - no outputs are passed to the build command (default outputs are used)
        :param platform: Platform to build for. *Requires Docker Buildx*. Default: - no platform specified (the current machine architecture will be used)
        :param target: Docker target to build to. Default: - no target
        :param extra_hash: Extra information to encode into the fingerprint (e.g. build instructions and other inputs). Default: - hash is only based on source content
        :param exclude: File paths matching the patterns will be excluded. See ``ignoreMode`` to set the matching behavior. Has no effect on Assets bundled using the ``bundling`` property. Default: - nothing is excluded
        :param follow_symlinks: A strategy for how to handle symlinks. Default: SymlinkFollowMode.NEVER
        :param ignore_mode: The ignore behavior to use for ``exclude`` patterns. Default: IgnoreMode.GLOB

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25f8364678c63568f662d1c08defb90957a4a2e7d3066311040cba2e3735b2fd)
            check_type(argname="argument directory", value=directory, expected_type=type_hints["directory"])
        options = _aws_cdk_aws_ecr_assets_ceddda9d.DockerImageAssetOptions(
            asset_name=asset_name,
            build_args=build_args,
            build_secrets=build_secrets,
            build_ssh=build_ssh,
            cache_from=cache_from,
            cache_to=cache_to,
            file=file,
            invalidation=invalidation,
            network_mode=network_mode,
            outputs=outputs,
            platform=platform,
            target=target,
            extra_hash=extra_hash,
            exclude=exclude,
            follow_symlinks=follow_symlinks,
            ignore_mode=ignore_mode,
        )

        return typing.cast("ContainerImage", jsii.sinvoke(cls, "fromAsset", [directory, options]))

    @jsii.member(jsii_name="fromEcrRepository")
    @builtins.classmethod
    def from_ecr_repository(
        cls,
        repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
        tag: typing.Optional[builtins.str] = None,
    ) -> "ContainerImage":
        '''
        :param repository: -
        :param tag: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d56d3018c15bc3c527de6fcfbab1fce78287d4b4a491912aa644b5edbd8864e)
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument tag", value=tag, expected_type=type_hints["tag"])
        return typing.cast("ContainerImage", jsii.sinvoke(cls, "fromEcrRepository", [repository, tag]))

    @jsii.member(jsii_name="bind")
    @abc.abstractmethod
    def bind(
        self,
        scope: _constructs_77d1e7e8.Construct,
        grantable: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> "ContainerImageConfig":
        '''
        :param scope: -
        :param grantable: -

        :stability: experimental
        '''
        ...


class _ContainerImageProxy(ContainerImage):
    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.Construct,
        grantable: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> "ContainerImageConfig":
        '''
        :param scope: -
        :param grantable: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98ebe648e608c12c055bbce76a5856ab8c5494b3267f8d897e31136265e41508)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument grantable", value=grantable, expected_type=type_hints["grantable"])
        return typing.cast("ContainerImageConfig", jsii.invoke(self, "bind", [scope, grantable]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, ContainerImage).__jsii_proxy_class__ = lambda : _ContainerImageProxy


@jsii.data_type(
    jsii_type="@cdklabs/generative-ai-cdk-constructs.ContainerImageConfig",
    jsii_struct_bases=[],
    name_mapping={"image_name": "imageName"},
)
class ContainerImageConfig:
    def __init__(self, *, image_name: builtins.str) -> None:
        '''
        :param image_name: (experimental) The image name. Images in Amazon ECR repositories can be specified by either using the full registry/repository:tag or registry/repository@digest. For example, ``012345678910.dkr.ecr.<region-name>.amazonaws.com/<repository-name>:latest`` or ``012345678910.dkr.ecr.<region-name>.amazonaws.com/<repository-name>@sha256:94afd1f2e64d908bc90dbca0035a5b567EXAMPLE``.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93de8836b2699c5ff29ea91bd61ddf2d833937fcf645c73a50bfb8c03c3b01e4)
            check_type(argname="argument image_name", value=image_name, expected_type=type_hints["image_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "image_name": image_name,
        }

    @builtins.property
    def image_name(self) -> builtins.str:
        '''(experimental) The image name. Images in Amazon ECR repositories can be specified by either using the full registry/repository:tag or registry/repository@digest.

        For example, ``012345678910.dkr.ecr.<region-name>.amazonaws.com/<repository-name>:latest`` or
        ``012345678910.dkr.ecr.<region-name>.amazonaws.com/<repository-name>@sha256:94afd1f2e64d908bc90dbca0035a5b567EXAMPLE``.

        :stability: experimental
        '''
        result = self._values.get("image_name")
        assert result is not None, "Required property 'image_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerImageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/generative-ai-cdk-constructs.CustomSageMakerEndpointProps",
    jsii_struct_bases=[],
    name_mapping={
        "container": "container",
        "endpoint_name": "endpointName",
        "instance_type": "instanceType",
        "model_data_url": "modelDataUrl",
        "model_id": "modelId",
        "environment": "environment",
        "instance_count": "instanceCount",
        "model_data_download_timeout_in_seconds": "modelDataDownloadTimeoutInSeconds",
        "role": "role",
        "startup_health_check_timeout_in_seconds": "startupHealthCheckTimeoutInSeconds",
        "volume_size_in_gb": "volumeSizeInGb",
        "vpc_config": "vpcConfig",
    },
)
class CustomSageMakerEndpointProps:
    def __init__(
        self,
        *,
        container: ContainerImage,
        endpoint_name: builtins.str,
        instance_type: "SageMakerInstanceType",
        model_data_url: builtins.str,
        model_id: builtins.str,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        instance_count: typing.Optional[jsii.Number] = None,
        model_data_download_timeout_in_seconds: typing.Optional[jsii.Number] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
        startup_health_check_timeout_in_seconds: typing.Optional[jsii.Number] = None,
        volume_size_in_gb: typing.Optional[jsii.Number] = None,
        vpc_config: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param container: 
        :param endpoint_name: 
        :param instance_type: 
        :param model_data_url: 
        :param model_id: 
        :param environment: 
        :param instance_count: 
        :param model_data_download_timeout_in_seconds: 
        :param role: 
        :param startup_health_check_timeout_in_seconds: 
        :param volume_size_in_gb: 
        :param vpc_config: 

        :stability: experimental
        '''
        if isinstance(vpc_config, dict):
            vpc_config = _aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty(**vpc_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64c88e4b8c433fb64fc5ff7b8ba1dfe89b0e7d556fee70434f79fe2f29d94734)
            check_type(argname="argument container", value=container, expected_type=type_hints["container"])
            check_type(argname="argument endpoint_name", value=endpoint_name, expected_type=type_hints["endpoint_name"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument model_data_url", value=model_data_url, expected_type=type_hints["model_data_url"])
            check_type(argname="argument model_id", value=model_id, expected_type=type_hints["model_id"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument instance_count", value=instance_count, expected_type=type_hints["instance_count"])
            check_type(argname="argument model_data_download_timeout_in_seconds", value=model_data_download_timeout_in_seconds, expected_type=type_hints["model_data_download_timeout_in_seconds"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument startup_health_check_timeout_in_seconds", value=startup_health_check_timeout_in_seconds, expected_type=type_hints["startup_health_check_timeout_in_seconds"])
            check_type(argname="argument volume_size_in_gb", value=volume_size_in_gb, expected_type=type_hints["volume_size_in_gb"])
            check_type(argname="argument vpc_config", value=vpc_config, expected_type=type_hints["vpc_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "container": container,
            "endpoint_name": endpoint_name,
            "instance_type": instance_type,
            "model_data_url": model_data_url,
            "model_id": model_id,
        }
        if environment is not None:
            self._values["environment"] = environment
        if instance_count is not None:
            self._values["instance_count"] = instance_count
        if model_data_download_timeout_in_seconds is not None:
            self._values["model_data_download_timeout_in_seconds"] = model_data_download_timeout_in_seconds
        if role is not None:
            self._values["role"] = role
        if startup_health_check_timeout_in_seconds is not None:
            self._values["startup_health_check_timeout_in_seconds"] = startup_health_check_timeout_in_seconds
        if volume_size_in_gb is not None:
            self._values["volume_size_in_gb"] = volume_size_in_gb
        if vpc_config is not None:
            self._values["vpc_config"] = vpc_config

    @builtins.property
    def container(self) -> ContainerImage:
        '''
        :stability: experimental
        '''
        result = self._values.get("container")
        assert result is not None, "Required property 'container' is missing"
        return typing.cast(ContainerImage, result)

    @builtins.property
    def endpoint_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("endpoint_name")
        assert result is not None, "Required property 'endpoint_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_type(self) -> "SageMakerInstanceType":
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast("SageMakerInstanceType", result)

    @builtins.property
    def model_data_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("model_data_url")
        assert result is not None, "Required property 'model_data_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def model_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("model_id")
        assert result is not None, "Required property 'model_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def instance_count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def model_data_download_timeout_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("model_data_download_timeout_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        '''
        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], result)

    @builtins.property
    def startup_health_check_timeout_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("startup_health_check_timeout_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volume_size_in_gb(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("volume_size_in_gb")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc_config(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty]:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc_config")
        return typing.cast(typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomSageMakerEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DeepLearningContainerImage(
    ContainerImage,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/generative-ai-cdk-constructs.DeepLearningContainerImage",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        repository_name: builtins.str,
        tag: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param repository_name: -
        :param tag: -
        :param account_id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d3668d1403c78d9ca09200041cb872341727345f79173e3de3ec628c79a40d2)
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
            check_type(argname="argument tag", value=tag, expected_type=type_hints["tag"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
        jsii.create(self.__class__, self, [repository_name, tag, account_id])

    @jsii.member(jsii_name="fromDeepLearningContainerImage")
    @builtins.classmethod
    def from_deep_learning_container_image(
        cls,
        repository_name: builtins.str,
        tag: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
    ) -> ContainerImage:
        '''
        :param repository_name: -
        :param tag: -
        :param account_id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ee4748a769dcb340a4537378546c2adacf2d41a2735729450c9cc171a8ae1af)
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
            check_type(argname="argument tag", value=tag, expected_type=type_hints["tag"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
        return typing.cast(ContainerImage, jsii.sinvoke(cls, "fromDeepLearningContainerImage", [repository_name, tag, account_id]))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.Construct,
        grantable: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> ContainerImageConfig:
        '''
        :param scope: -
        :param grantable: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61d694cb21f225b8854128d356326406cf367ffbc30d0b508a85ebb3ea487f8f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument grantable", value=grantable, expected_type=type_hints["grantable"])
        return typing.cast(ContainerImageConfig, jsii.invoke(self, "bind", [scope, grantable]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_19_0_DEEPSPEED0_7_3_CU113")
    def DJL_INFERENCE_0_19_0_DEEPSPEED0_7_3_CU113(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_19_0_DEEPSPEED0_7_3_CU113"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_20_0_DEEPSPEED0_7_5_CU116")
    def DJL_INFERENCE_0_20_0_DEEPSPEED0_7_5_CU116(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_20_0_DEEPSPEED0_7_5_CU116"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_21_0_DEEPSPEED0_8_0_CU117")
    def DJL_INFERENCE_0_21_0_DEEPSPEED0_8_0_CU117(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_21_0_DEEPSPEED0_8_0_CU117"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_21_0_DEEPSPEED0_8_3_CU117")
    def DJL_INFERENCE_0_21_0_DEEPSPEED0_8_3_CU117(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_21_0_DEEPSPEED0_8_3_CU117"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_21_0_FASTERTRANSFORMER5_3_0_CU117")
    def DJL_INFERENCE_0_21_0_FASTERTRANSFORMER5_3_0_CU117(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_21_0_FASTERTRANSFORMER5_3_0_CU117"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_22_1_DEEPSPEED0_8_3_CU118")
    def DJL_INFERENCE_0_22_1_DEEPSPEED0_8_3_CU118(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_22_1_DEEPSPEED0_8_3_CU118"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_22_1_DEEPSPEED0_9_2_CU118")
    def DJL_INFERENCE_0_22_1_DEEPSPEED0_9_2_CU118(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_22_1_DEEPSPEED0_9_2_CU118"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_22_1_FASTERTRANSFORMER5_3_0_CU118")
    def DJL_INFERENCE_0_22_1_FASTERTRANSFORMER5_3_0_CU118(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_22_1_FASTERTRANSFORMER5_3_0_CU118"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_22_1_NEURONX_SDK2_10_0")
    def DJL_INFERENCE_0_22_1_NEURONX_SDK2_10_0(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_22_1_NEURONX_SDK2_10_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_22_1_NEURONX_SDK2_9_0")
    def DJL_INFERENCE_0_22_1_NEURONX_SDK2_9_0(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_22_1_NEURONX_SDK2_9_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_23_0_DEEPSPEED0_9_5_CU118")
    def DJL_INFERENCE_0_23_0_DEEPSPEED0_9_5_CU118(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_23_0_DEEPSPEED0_9_5_CU118"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_23_0_FASTERTRANSFORMER5_3_0_CU118")
    def DJL_INFERENCE_0_23_0_FASTERTRANSFORMER5_3_0_CU118(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_23_0_FASTERTRANSFORMER5_3_0_CU118"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_23_0_NEURONX_SDK2_12_0")
    def DJL_INFERENCE_0_23_0_NEURONX_SDK2_12_0(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_23_0_NEURONX_SDK2_12_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_24_0_DEEPSPEED0_10_0_CU118")
    def DJL_INFERENCE_0_24_0_DEEPSPEED0_10_0_CU118(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_24_0_DEEPSPEED0_10_0_CU118"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_24_0_FASTERTRANSFORMER5_3_0_CU118")
    def DJL_INFERENCE_0_24_0_FASTERTRANSFORMER5_3_0_CU118(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_24_0_FASTERTRANSFORMER5_3_0_CU118"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_24_0_NEURONX_SDK2_14_1")
    def DJL_INFERENCE_0_24_0_NEURONX_SDK2_14_1(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_24_0_NEURONX_SDK2_14_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_25_0_DEEPSPEED0_11_0_CU118")
    def DJL_INFERENCE_0_25_0_DEEPSPEED0_11_0_CU118(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_25_0_DEEPSPEED0_11_0_CU118"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DJL_INFERENCE_0_25_0_NEURONX_SDK2_15_0")
    def DJL_INFERENCE_0_25_0_NEURONX_SDK2_15_0(cls) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "DJL_INFERENCE_0_25_0_NEURONX_SDK2_15_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_1_10_2_TRANSFORMERS4_17_0_CPU_PY38_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_1_10_2_TRANSFORMERS4_17_0_CPU_PY38_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_1_10_2_TRANSFORMERS4_17_0_CPU_PY38_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_1_10_2_TRANSFORMERS4_17_0_GPU_PY38_CU113_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_1_10_2_TRANSFORMERS4_17_0_GPU_PY38_CU113_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_1_10_2_TRANSFORMERS4_17_0_GPU_PY38_CU113_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_1_13_1_TRANSFORMERS4_26_0_CPU_PY39_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_1_13_1_TRANSFORMERS4_26_0_CPU_PY39_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_1_13_1_TRANSFORMERS4_26_0_CPU_PY39_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_1_13_1_TRANSFORMERS4_26_0_GPU_PY39_CU117_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_1_13_1_TRANSFORMERS4_26_0_GPU_PY39_CU117_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_1_13_1_TRANSFORMERS4_26_0_GPU_PY39_CU117_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_1_7_1_TRANSFORMERS4_6_1_CPU_PY36_UBUNTU18_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_1_7_1_TRANSFORMERS4_6_1_CPU_PY36_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_1_7_1_TRANSFORMERS4_6_1_CPU_PY36_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_1_7_1_TRANSFORMERS4_6_1_GPU_PY36_CU110_UBUNTU18_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_1_7_1_TRANSFORMERS4_6_1_GPU_PY36_CU110_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_1_7_1_TRANSFORMERS4_6_1_GPU_PY36_CU110_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_1_8_1_TRANSFORMERS4_10_2_CPU_PY36_UBUNTU18_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_1_8_1_TRANSFORMERS4_10_2_CPU_PY36_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_1_8_1_TRANSFORMERS4_10_2_CPU_PY36_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_1_8_1_TRANSFORMERS4_10_2_GPU_PY36_CU111_UBUNTU18_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_1_8_1_TRANSFORMERS4_10_2_GPU_PY36_CU111_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_1_8_1_TRANSFORMERS4_10_2_GPU_PY36_CU111_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_1_8_1_TRANSFORMERS4_6_1_CPU_PY36_UBUNTU18_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_1_8_1_TRANSFORMERS4_6_1_CPU_PY36_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_1_8_1_TRANSFORMERS4_6_1_CPU_PY36_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_1_8_1_TRANSFORMERS4_6_1_GPU_PY36_CU111_UBUNTU18_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_1_8_1_TRANSFORMERS4_6_1_GPU_PY36_CU111_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_1_8_1_TRANSFORMERS4_6_1_GPU_PY36_CU111_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_1_9_0_TRANSFORMERS4_10_2_CPU_PY38_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_1_9_0_TRANSFORMERS4_10_2_CPU_PY38_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_1_9_0_TRANSFORMERS4_10_2_CPU_PY38_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_1_9_0_TRANSFORMERS4_10_2_GPU_PY38_CU111_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_1_9_0_TRANSFORMERS4_10_2_GPU_PY38_CU111_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_1_9_0_TRANSFORMERS4_10_2_GPU_PY38_CU111_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_1_9_0_TRANSFORMERS4_11_0_CPU_PY38_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_1_9_0_TRANSFORMERS4_11_0_CPU_PY38_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_1_9_0_TRANSFORMERS4_11_0_CPU_PY38_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_1_9_0_TRANSFORMERS4_11_0_GPU_PY38_CU111_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_1_9_0_TRANSFORMERS4_11_0_GPU_PY38_CU111_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_1_9_0_TRANSFORMERS4_11_0_GPU_PY38_CU111_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_1_9_1_TRANSFORMERS4_12_3_CPU_PY38_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_1_9_1_TRANSFORMERS4_12_3_CPU_PY38_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_1_9_1_TRANSFORMERS4_12_3_CPU_PY38_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_1_9_1_TRANSFORMERS4_12_3_GPU_PY38_CU111_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_1_9_1_TRANSFORMERS4_12_3_GPU_PY38_CU111_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_1_9_1_TRANSFORMERS4_12_3_GPU_PY38_CU111_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_2_0_0_TRANSFORMERS4_28_1_CPU_PY310_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_2_0_0_TRANSFORMERS4_28_1_CPU_PY310_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_2_0_0_TRANSFORMERS4_28_1_CPU_PY310_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_2_0_0_TRANSFORMERS4_28_1_GPU_PY310_CU118_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_2_0_0_TRANSFORMERS4_28_1_GPU_PY310_CU118_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_2_0_0_TRANSFORMERS4_28_1_GPU_PY310_CU118_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_NEURONX_1_13_0_TRANSFORMERS4_28_1_NEURONX_PY38_SDK2_9_1_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_NEURONX_1_13_0_TRANSFORMERS4_28_1_NEURONX_PY38_SDK2_9_1_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_NEURONX_1_13_0_TRANSFORMERS4_28_1_NEURONX_PY38_SDK2_9_1_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_INFERENCE_NEURONX_1_13_1_TRANSFORMERS4_34_1_NEURONX_PY310_SDK2_15_0_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_INFERENCE_NEURONX_1_13_1_TRANSFORMERS4_34_1_NEURONX_PY310_SDK2_15_0_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_INFERENCE_NEURONX_1_13_1_TRANSFORMERS4_34_1_NEURONX_PY310_SDK2_15_0_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_TGI_INFERENCE_2_0_0_TGI0_6_0_GPU_PY39_CU118_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_TGI_INFERENCE_2_0_0_TGI0_6_0_GPU_PY39_CU118_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_TGI_INFERENCE_2_0_0_TGI0_6_0_GPU_PY39_CU118_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_TGI_INFERENCE_2_0_0_TGI0_8_2_GPU_PY39_CU118_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_TGI_INFERENCE_2_0_0_TGI0_8_2_GPU_PY39_CU118_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_TGI_INFERENCE_2_0_0_TGI0_8_2_GPU_PY39_CU118_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_TGI_INFERENCE_2_0_1_TGI0_9_3_GPU_PY39_CU118_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_TGI_INFERENCE_2_0_1_TGI0_9_3_GPU_PY39_CU118_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_TGI_INFERENCE_2_0_1_TGI0_9_3_GPU_PY39_CU118_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_TGI_INFERENCE_2_0_1_TGI1_0_3_GPU_PY39_CU118_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_TGI_INFERENCE_2_0_1_TGI1_0_3_GPU_PY39_CU118_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_TGI_INFERENCE_2_0_1_TGI1_0_3_GPU_PY39_CU118_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_PYTORCH_TGI_INFERENCE_2_0_1_TGI1_1_0_GPU_PY39_CU118_UBUNTU20_04")
    def HUGGINGFACE_PYTORCH_TGI_INFERENCE_2_0_1_TGI1_1_0_GPU_PY39_CU118_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_PYTORCH_TGI_INFERENCE_2_0_1_TGI1_1_0_GPU_PY39_CU118_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_11_0_TRANSFORMERS4_26_0_CPU_PY39_UBUNTU20_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_11_0_TRANSFORMERS4_26_0_CPU_PY39_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_11_0_TRANSFORMERS4_26_0_CPU_PY39_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_11_0_TRANSFORMERS4_26_0_GPU_PY39_CU112_UBUNTU20_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_11_0_TRANSFORMERS4_26_0_GPU_PY39_CU112_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_11_0_TRANSFORMERS4_26_0_GPU_PY39_CU112_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_11_1_TRANSFORMERS4_26_0_CPU_PY39_UBUNTU20_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_11_1_TRANSFORMERS4_26_0_CPU_PY39_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_11_1_TRANSFORMERS4_26_0_CPU_PY39_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_11_1_TRANSFORMERS4_26_0_GPU_PY39_CU112_UBUNTU20_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_11_1_TRANSFORMERS4_26_0_GPU_PY39_CU112_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_11_1_TRANSFORMERS4_26_0_GPU_PY39_CU112_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_4_1_TRANSFORMERS4_6_1_CPU_PY37_UBUNTU18_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_4_1_TRANSFORMERS4_6_1_CPU_PY37_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_4_1_TRANSFORMERS4_6_1_CPU_PY37_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_4_1_TRANSFORMERS4_6_1_GPU_PY37_CU110_UBUNTU18_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_4_1_TRANSFORMERS4_6_1_GPU_PY37_CU110_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_4_1_TRANSFORMERS4_6_1_GPU_PY37_CU110_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_4_3_TRANSFORMERS4_10_2_CPU_PY37_UBUNTU18_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_4_3_TRANSFORMERS4_10_2_CPU_PY37_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_4_3_TRANSFORMERS4_10_2_CPU_PY37_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_4_3_TRANSFORMERS4_10_2_GPU_PY37_CU110_UBUNTU18_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_4_3_TRANSFORMERS4_10_2_GPU_PY37_CU110_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_4_3_TRANSFORMERS4_10_2_GPU_PY37_CU110_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_10_2_CPU_PY37_UBUNTU18_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_10_2_CPU_PY37_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_10_2_CPU_PY37_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_10_2_GPU_PY37_CU112_UBUNTU18_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_10_2_GPU_PY37_CU112_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_10_2_GPU_PY37_CU112_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_11_0_CPU_PY37_UBUNTU18_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_11_0_CPU_PY37_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_11_0_CPU_PY37_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_11_0_GPU_PY37_CU112_UBUNTU18_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_11_0_GPU_PY37_CU112_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_11_0_GPU_PY37_CU112_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_12_3_CPU_PY37_UBUNTU18_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_12_3_CPU_PY37_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_12_3_CPU_PY37_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_12_3_GPU_PY37_CU112_UBUNTU18_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_12_3_GPU_PY37_CU112_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_1_TRANSFORMERS4_12_3_GPU_PY37_CU112_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_3_TRANSFORMERS4_12_3_CPU_PY37_UBUNTU18_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_3_TRANSFORMERS4_12_3_CPU_PY37_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_3_TRANSFORMERS4_12_3_CPU_PY37_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_3_TRANSFORMERS4_12_3_GPU_PY37_CU112_UBUNTU18_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_3_TRANSFORMERS4_12_3_GPU_PY37_CU112_UBUNTU18_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_5_3_TRANSFORMERS4_12_3_GPU_PY37_CU112_UBUNTU18_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_6_3_TRANSFORMERS4_17_0_CPU_PY38_UBUNTU20_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_6_3_TRANSFORMERS4_17_0_CPU_PY38_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_6_3_TRANSFORMERS4_17_0_CPU_PY38_UBUNTU20_04"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TENSORFLOW_INFERENCE_2_6_3_TRANSFORMERS4_17_0_GPU_PY38_CU112_UBUNTU20_04")
    def HUGGINGFACE_TENSORFLOW_INFERENCE_2_6_3_TRANSFORMERS4_17_0_GPU_PY38_CU112_UBUNTU20_04(
        cls,
    ) -> ContainerImage:
        '''
        :stability: experimental
        '''
        return typing.cast(ContainerImage, jsii.sget(cls, "HUGGINGFACE_TENSORFLOW_INFERENCE_2_6_3_TRANSFORMERS4_17_0_GPU_PY38_CU112_UBUNTU20_04"))


@jsii.data_type(
    jsii_type="@cdklabs/generative-ai-cdk-constructs.HuggingFaceSageMakerEndpointProps",
    jsii_struct_bases=[],
    name_mapping={
        "container": "container",
        "instance_type": "instanceType",
        "model_id": "modelId",
        "endpoint_name": "endpointName",
        "environment": "environment",
        "instance_count": "instanceCount",
        "role": "role",
        "startup_health_check_timeout_in_seconds": "startupHealthCheckTimeoutInSeconds",
        "vpc_config": "vpcConfig",
    },
)
class HuggingFaceSageMakerEndpointProps:
    def __init__(
        self,
        *,
        container: ContainerImage,
        instance_type: "SageMakerInstanceType",
        model_id: builtins.str,
        endpoint_name: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        instance_count: typing.Optional[jsii.Number] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
        startup_health_check_timeout_in_seconds: typing.Optional[jsii.Number] = None,
        vpc_config: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param container: 
        :param instance_type: 
        :param model_id: 
        :param endpoint_name: 
        :param environment: 
        :param instance_count: 
        :param role: 
        :param startup_health_check_timeout_in_seconds: 
        :param vpc_config: 

        :stability: experimental
        '''
        if isinstance(vpc_config, dict):
            vpc_config = _aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty(**vpc_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9abbb731cf44967a6628e353d6c56d0035755b62bf45acdaa8261b4c5048d1f9)
            check_type(argname="argument container", value=container, expected_type=type_hints["container"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument model_id", value=model_id, expected_type=type_hints["model_id"])
            check_type(argname="argument endpoint_name", value=endpoint_name, expected_type=type_hints["endpoint_name"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument instance_count", value=instance_count, expected_type=type_hints["instance_count"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument startup_health_check_timeout_in_seconds", value=startup_health_check_timeout_in_seconds, expected_type=type_hints["startup_health_check_timeout_in_seconds"])
            check_type(argname="argument vpc_config", value=vpc_config, expected_type=type_hints["vpc_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "container": container,
            "instance_type": instance_type,
            "model_id": model_id,
        }
        if endpoint_name is not None:
            self._values["endpoint_name"] = endpoint_name
        if environment is not None:
            self._values["environment"] = environment
        if instance_count is not None:
            self._values["instance_count"] = instance_count
        if role is not None:
            self._values["role"] = role
        if startup_health_check_timeout_in_seconds is not None:
            self._values["startup_health_check_timeout_in_seconds"] = startup_health_check_timeout_in_seconds
        if vpc_config is not None:
            self._values["vpc_config"] = vpc_config

    @builtins.property
    def container(self) -> ContainerImage:
        '''
        :stability: experimental
        '''
        result = self._values.get("container")
        assert result is not None, "Required property 'container' is missing"
        return typing.cast(ContainerImage, result)

    @builtins.property
    def instance_type(self) -> "SageMakerInstanceType":
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast("SageMakerInstanceType", result)

    @builtins.property
    def model_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("model_id")
        assert result is not None, "Required property 'model_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def endpoint_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("endpoint_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def instance_count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        '''
        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], result)

    @builtins.property
    def startup_health_check_timeout_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("startup_health_check_timeout_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc_config(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty]:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc_config")
        return typing.cast(typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HuggingFaceSageMakerEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@cdklabs/generative-ai-cdk-constructs.IInstanceAliase")
class IInstanceAliase(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="aliases")
    def aliases(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @aliases.setter
    def aliases(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @region.setter
    def region(self, value: builtins.str) -> None:
        ...


class _IInstanceAliaseProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/generative-ai-cdk-constructs.IInstanceAliase"

    @builtins.property
    @jsii.member(jsii_name="aliases")
    def aliases(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "aliases"))

    @aliases.setter
    def aliases(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5f72a06047d6784d819d9905a60d528d3adf1757fd113a494d1e278ff756cc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aliases", value)

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09be534ff54d13743d68fbae01a7a6206246397b640b98663316222b3582760e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IInstanceAliase).__jsii_proxy_class__ = lambda : _IInstanceAliaseProxy


@jsii.interface(jsii_type="@cdklabs/generative-ai-cdk-constructs.IInstanceValiant")
class IInstanceValiant(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @instance_type.setter
    def instance_type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        ...

    @environment.setter
    def environment(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="imageUri")
    def image_uri(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @image_uri.setter
    def image_uri(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IInstanceValiantProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/generative-ai-cdk-constructs.IInstanceValiant"

    @builtins.property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceType"))

    @instance_type.setter
    def instance_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__784c92c851a2dedf6e80ea471cde9f9490de2aa6021222c9354e77dce1375a9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceType", value)

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "environment"))

    @environment.setter
    def environment(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bd10265f2863a8642df6187149bcdb3e5b8d4d4a701e3c0f81e180f79133355)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environment", value)

    @builtins.property
    @jsii.member(jsii_name="imageUri")
    def image_uri(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageUri"))

    @image_uri.setter
    def image_uri(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5208b4cb02ff50a0ebbf048c64aae565c2966812ac05c66bd93c7b3c84aa63ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageUri", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IInstanceValiant).__jsii_proxy_class__ = lambda : _IInstanceValiantProxy


@jsii.interface(jsii_type="@cdklabs/generative-ai-cdk-constructs.IJumpStartModelSpec")
class IJumpStartModelSpec(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="defaultInstanceType")
    def default_instance_type(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @default_instance_type.setter
    def default_instance_type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(
        self,
    ) -> typing.Mapping[builtins.str, typing.Union[builtins.str, jsii.Number, builtins.bool]]:
        '''
        :stability: experimental
        '''
        ...

    @environment.setter
    def environment(
        self,
        value: typing.Mapping[builtins.str, typing.Union[builtins.str, jsii.Number, builtins.bool]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="instanceTypes")
    def instance_types(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @instance_types.setter
    def instance_types(self, value: typing.List[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="modelId")
    def model_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @model_id.setter
    def model_id(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @version.setter
    def version(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="artifactKey")
    def artifact_key(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @artifact_key.setter
    def artifact_key(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="instanceAliases")
    def instance_aliases(self) -> typing.Optional[typing.List[IInstanceAliase]]:
        '''
        :stability: experimental
        '''
        ...

    @instance_aliases.setter
    def instance_aliases(
        self,
        value: typing.Optional[typing.List[IInstanceAliase]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="instanceVariants")
    def instance_variants(self) -> typing.Optional[typing.List[IInstanceValiant]]:
        '''
        :stability: experimental
        '''
        ...

    @instance_variants.setter
    def instance_variants(
        self,
        value: typing.Optional[typing.List[IInstanceValiant]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="modelPackageArns")
    def model_package_arns(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        ...

    @model_package_arns.setter
    def model_package_arns(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="prepackedArtifactKey")
    def prepacked_artifact_key(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @prepacked_artifact_key.setter
    def prepacked_artifact_key(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IJumpStartModelSpecProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/generative-ai-cdk-constructs.IJumpStartModelSpec"

    @builtins.property
    @jsii.member(jsii_name="defaultInstanceType")
    def default_instance_type(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "defaultInstanceType"))

    @default_instance_type.setter
    def default_instance_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a5a0c622f349e4bb3c898657c97ff2fd43f2f1ae081b59b80a923854e9a513f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultInstanceType", value)

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(
        self,
    ) -> typing.Mapping[builtins.str, typing.Union[builtins.str, jsii.Number, builtins.bool]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Union[builtins.str, jsii.Number, builtins.bool]], jsii.get(self, "environment"))

    @environment.setter
    def environment(
        self,
        value: typing.Mapping[builtins.str, typing.Union[builtins.str, jsii.Number, builtins.bool]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2073cfea003f3e88c802dd137c85fd6e32f9da1475fd6187a6f87ace6a655672)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environment", value)

    @builtins.property
    @jsii.member(jsii_name="instanceTypes")
    def instance_types(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "instanceTypes"))

    @instance_types.setter
    def instance_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aef2d73f0172f5d063f633b101b7066b0fbe43a8824831786cf98be28ecd7f30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceTypes", value)

    @builtins.property
    @jsii.member(jsii_name="modelId")
    def model_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "modelId"))

    @model_id.setter
    def model_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0aa0d5de10cb8693f8f2a7f933f95ad652052122b9c5fbb256a6a6eb62687607)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modelId", value)

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__230bf6b942aecadf2cddb2400e4b8fa93d7b5324764d21f3c3745c62d2c05093)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value)

    @builtins.property
    @jsii.member(jsii_name="artifactKey")
    def artifact_key(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "artifactKey"))

    @artifact_key.setter
    def artifact_key(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e18f266234ad99daa9e9e8bc62ef14e306dceb86e8896985bbb9c334a1a680d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "artifactKey", value)

    @builtins.property
    @jsii.member(jsii_name="instanceAliases")
    def instance_aliases(self) -> typing.Optional[typing.List[IInstanceAliase]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[IInstanceAliase]], jsii.get(self, "instanceAliases"))

    @instance_aliases.setter
    def instance_aliases(
        self,
        value: typing.Optional[typing.List[IInstanceAliase]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab8b9681e067fc772bfa8ae21e9b889922f76498043ac3dc59607d18b1c99b6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceAliases", value)

    @builtins.property
    @jsii.member(jsii_name="instanceVariants")
    def instance_variants(self) -> typing.Optional[typing.List[IInstanceValiant]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[IInstanceValiant]], jsii.get(self, "instanceVariants"))

    @instance_variants.setter
    def instance_variants(
        self,
        value: typing.Optional[typing.List[IInstanceValiant]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a37af151d413380fdbb03c303f6e418d5e5ca5225e04d5264a9a4ea57136b320)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceVariants", value)

    @builtins.property
    @jsii.member(jsii_name="modelPackageArns")
    def model_package_arns(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "modelPackageArns"))

    @model_package_arns.setter
    def model_package_arns(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b5a37e8a274c0f3fc20705440c0c3341b45281869a1e4e347af5d91621fcaa1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modelPackageArns", value)

    @builtins.property
    @jsii.member(jsii_name="prepackedArtifactKey")
    def prepacked_artifact_key(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prepackedArtifactKey"))

    @prepacked_artifact_key.setter
    def prepacked_artifact_key(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03c90f1f4cdb0e78188cc1b2b4752b6e641e3139cd9ddbcd4cf9be7e0e0a09dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prepackedArtifactKey", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IJumpStartModelSpec).__jsii_proxy_class__ = lambda : _IJumpStartModelSpecProxy


class JumpStartModel(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/generative-ai-cdk-constructs.JumpStartModel",
):
    '''
    :stability: experimental
    '''

    def __init__(self, name: builtins.str) -> None:
        '''
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__951253bb0ca138e826c6fe2a480e29d1949fa737e804147291d2ca257fc68fbc)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        jsii.create(self.__class__, self, [name])

    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(cls, name: builtins.str) -> "JumpStartModel":
        '''
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5af7b97de0c920bbdd298f2015ccefdbeb43ecd7756bcf540abe8209e26d7adb)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("JumpStartModel", jsii.sinvoke(cls, "of", [name]))

    @jsii.member(jsii_name="bind")
    def bind(self) -> IJumpStartModelSpec:
        '''
        :stability: experimental
        '''
        return typing.cast(IJumpStartModelSpec, jsii.invoke(self, "bind", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_BASE_1_0_0")
    def HUGGINGFACE_ASR_WHISPER_BASE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_BASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_BASE_1_0_1")
    def HUGGINGFACE_ASR_WHISPER_BASE_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_BASE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_BASE_2_0_0")
    def HUGGINGFACE_ASR_WHISPER_BASE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_BASE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_LARGE_1_0_0")
    def HUGGINGFACE_ASR_WHISPER_LARGE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_LARGE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_LARGE_1_0_1")
    def HUGGINGFACE_ASR_WHISPER_LARGE_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_LARGE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_LARGE_2_0_0")
    def HUGGINGFACE_ASR_WHISPER_LARGE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_LARGE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_LARGE_V2_1_0_0")
    def HUGGINGFACE_ASR_WHISPER_LARGE_V2_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_LARGE_V2_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_LARGE_V2_1_0_1")
    def HUGGINGFACE_ASR_WHISPER_LARGE_V2_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_LARGE_V2_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_LARGE_V2_2_0_0")
    def HUGGINGFACE_ASR_WHISPER_LARGE_V2_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_LARGE_V2_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_MEDIUM_1_0_0")
    def HUGGINGFACE_ASR_WHISPER_MEDIUM_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_MEDIUM_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_MEDIUM_1_0_1")
    def HUGGINGFACE_ASR_WHISPER_MEDIUM_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_MEDIUM_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_MEDIUM_2_0_0")
    def HUGGINGFACE_ASR_WHISPER_MEDIUM_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_MEDIUM_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_SMALL_1_0_0")
    def HUGGINGFACE_ASR_WHISPER_SMALL_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_SMALL_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_SMALL_1_0_1")
    def HUGGINGFACE_ASR_WHISPER_SMALL_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_SMALL_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_SMALL_2_0_0")
    def HUGGINGFACE_ASR_WHISPER_SMALL_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_SMALL_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_TINY_1_0_0")
    def HUGGINGFACE_ASR_WHISPER_TINY_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_TINY_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_TINY_1_0_1")
    def HUGGINGFACE_ASR_WHISPER_TINY_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_TINY_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ASR_WHISPER_TINY_2_0_0")
    def HUGGINGFACE_ASR_WHISPER_TINY_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ASR_WHISPER_TINY_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_BASE_CASED_1_0_0")
    def HUGGINGFACE_EQA_BERT_BASE_CASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_BASE_CASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_BASE_CASED_1_0_1")
    def HUGGINGFACE_EQA_BERT_BASE_CASED_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_BASE_CASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_BASE_CASED_1_0_2")
    def HUGGINGFACE_EQA_BERT_BASE_CASED_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_BASE_CASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_BASE_CASED_2_0_0")
    def HUGGINGFACE_EQA_BERT_BASE_CASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_BASE_CASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_CASED_1_0_0")
    def HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_CASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_CASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_CASED_1_0_1")
    def HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_CASED_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_CASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_CASED_1_0_2")
    def HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_CASED_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_CASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_CASED_2_0_0")
    def HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_CASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_CASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_UNCASED_1_0_0")
    def HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_UNCASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_UNCASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_UNCASED_1_0_1")
    def HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_UNCASED_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_UNCASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_UNCASED_1_0_2")
    def HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_UNCASED_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_UNCASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_UNCASED_2_0_0")
    def HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_UNCASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_BASE_MULTILINGUAL_UNCASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_BASE_UNCASED_1_0_0")
    def HUGGINGFACE_EQA_BERT_BASE_UNCASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_BASE_UNCASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_BASE_UNCASED_1_0_1")
    def HUGGINGFACE_EQA_BERT_BASE_UNCASED_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_BASE_UNCASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_BASE_UNCASED_1_0_2")
    def HUGGINGFACE_EQA_BERT_BASE_UNCASED_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_BASE_UNCASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_BASE_UNCASED_2_0_0")
    def HUGGINGFACE_EQA_BERT_BASE_UNCASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_BASE_UNCASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_LARGE_CASED_1_0_0")
    def HUGGINGFACE_EQA_BERT_LARGE_CASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_LARGE_CASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_LARGE_CASED_1_0_1")
    def HUGGINGFACE_EQA_BERT_LARGE_CASED_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_LARGE_CASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_LARGE_CASED_1_0_2")
    def HUGGINGFACE_EQA_BERT_LARGE_CASED_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_LARGE_CASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_LARGE_CASED_2_0_0")
    def HUGGINGFACE_EQA_BERT_LARGE_CASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_LARGE_CASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_0")
    def HUGGINGFACE_EQA_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_1")
    def HUGGINGFACE_EQA_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_2")
    def HUGGINGFACE_EQA_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_2(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_LARGE_CASED_WHOLE_WORD_MASKING_2_0_0")
    def HUGGINGFACE_EQA_BERT_LARGE_CASED_WHOLE_WORD_MASKING_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_LARGE_CASED_WHOLE_WORD_MASKING_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_LARGE_UNCASED_1_0_0")
    def HUGGINGFACE_EQA_BERT_LARGE_UNCASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_LARGE_UNCASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_LARGE_UNCASED_1_0_1")
    def HUGGINGFACE_EQA_BERT_LARGE_UNCASED_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_LARGE_UNCASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_LARGE_UNCASED_1_0_2")
    def HUGGINGFACE_EQA_BERT_LARGE_UNCASED_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_LARGE_UNCASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_LARGE_UNCASED_2_0_0")
    def HUGGINGFACE_EQA_BERT_LARGE_UNCASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_LARGE_UNCASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_0")
    def HUGGINGFACE_EQA_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_1")
    def HUGGINGFACE_EQA_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_2")
    def HUGGINGFACE_EQA_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_2(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_2_0_0")
    def HUGGINGFACE_EQA_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_DISTILBERT_BASE_CASED_1_0_0")
    def HUGGINGFACE_EQA_DISTILBERT_BASE_CASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_DISTILBERT_BASE_CASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_DISTILBERT_BASE_CASED_1_0_1")
    def HUGGINGFACE_EQA_DISTILBERT_BASE_CASED_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_DISTILBERT_BASE_CASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_DISTILBERT_BASE_CASED_1_0_2")
    def HUGGINGFACE_EQA_DISTILBERT_BASE_CASED_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_DISTILBERT_BASE_CASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_DISTILBERT_BASE_CASED_2_0_0")
    def HUGGINGFACE_EQA_DISTILBERT_BASE_CASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_DISTILBERT_BASE_CASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_0")
    def HUGGINGFACE_EQA_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_1")
    def HUGGINGFACE_EQA_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_2")
    def HUGGINGFACE_EQA_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_2(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_DISTILBERT_BASE_MULTILINGUAL_CASED_2_0_0")
    def HUGGINGFACE_EQA_DISTILBERT_BASE_MULTILINGUAL_CASED_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_DISTILBERT_BASE_MULTILINGUAL_CASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_DISTILBERT_BASE_UNCASED_1_0_0")
    def HUGGINGFACE_EQA_DISTILBERT_BASE_UNCASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_DISTILBERT_BASE_UNCASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_DISTILBERT_BASE_UNCASED_1_0_1")
    def HUGGINGFACE_EQA_DISTILBERT_BASE_UNCASED_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_DISTILBERT_BASE_UNCASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_DISTILBERT_BASE_UNCASED_1_0_2")
    def HUGGINGFACE_EQA_DISTILBERT_BASE_UNCASED_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_DISTILBERT_BASE_UNCASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_DISTILBERT_BASE_UNCASED_2_0_0")
    def HUGGINGFACE_EQA_DISTILBERT_BASE_UNCASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_DISTILBERT_BASE_UNCASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_DISTILROBERTA_BASE_1_0_0")
    def HUGGINGFACE_EQA_DISTILROBERTA_BASE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_DISTILROBERTA_BASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_DISTILROBERTA_BASE_1_0_1")
    def HUGGINGFACE_EQA_DISTILROBERTA_BASE_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_DISTILROBERTA_BASE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_DISTILROBERTA_BASE_1_0_2")
    def HUGGINGFACE_EQA_DISTILROBERTA_BASE_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_DISTILROBERTA_BASE_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_DISTILROBERTA_BASE_2_0_0")
    def HUGGINGFACE_EQA_DISTILROBERTA_BASE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_DISTILROBERTA_BASE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_ROBERTA_BASE_1_0_0")
    def HUGGINGFACE_EQA_ROBERTA_BASE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_ROBERTA_BASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_ROBERTA_BASE_1_0_1")
    def HUGGINGFACE_EQA_ROBERTA_BASE_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_ROBERTA_BASE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_ROBERTA_BASE_1_0_2")
    def HUGGINGFACE_EQA_ROBERTA_BASE_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_ROBERTA_BASE_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_ROBERTA_BASE_2_0_0")
    def HUGGINGFACE_EQA_ROBERTA_BASE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_ROBERTA_BASE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_ROBERTA_BASE_OPENAI_DETECTOR_1_0_0")
    def HUGGINGFACE_EQA_ROBERTA_BASE_OPENAI_DETECTOR_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_ROBERTA_BASE_OPENAI_DETECTOR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_ROBERTA_BASE_OPENAI_DETECTOR_1_0_1")
    def HUGGINGFACE_EQA_ROBERTA_BASE_OPENAI_DETECTOR_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_ROBERTA_BASE_OPENAI_DETECTOR_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_ROBERTA_BASE_OPENAI_DETECTOR_1_0_2")
    def HUGGINGFACE_EQA_ROBERTA_BASE_OPENAI_DETECTOR_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_ROBERTA_BASE_OPENAI_DETECTOR_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_ROBERTA_BASE_OPENAI_DETECTOR_2_0_0")
    def HUGGINGFACE_EQA_ROBERTA_BASE_OPENAI_DETECTOR_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_ROBERTA_BASE_OPENAI_DETECTOR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_ROBERTA_LARGE_1_0_0")
    def HUGGINGFACE_EQA_ROBERTA_LARGE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_ROBERTA_LARGE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_ROBERTA_LARGE_1_0_1")
    def HUGGINGFACE_EQA_ROBERTA_LARGE_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_ROBERTA_LARGE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_ROBERTA_LARGE_1_0_2")
    def HUGGINGFACE_EQA_ROBERTA_LARGE_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_ROBERTA_LARGE_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_EQA_ROBERTA_LARGE_2_0_0")
    def HUGGINGFACE_EQA_ROBERTA_LARGE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_EQA_ROBERTA_LARGE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_FILLMASK_BERT_BASE_UNCASED_1_0_0")
    def HUGGINGFACE_FILLMASK_BERT_BASE_UNCASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_FILLMASK_BERT_BASE_UNCASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_FILLMASK_BERT_BASE_UNCASED_2_0_0")
    def HUGGINGFACE_FILLMASK_BERT_BASE_UNCASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_FILLMASK_BERT_BASE_UNCASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_BILINGUAL_RINNA_4B_INSTRUCTION_PPO_BF16_1_0_0")
    def HUGGINGFACE_LLM_BILINGUAL_RINNA_4_B_INSTRUCTION_PPO_BF16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_BILINGUAL_RINNA_4B_INSTRUCTION_PPO_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_BILINGUAL_RINNA_4B_INSTRUCTION_PPO_BF16_1_1_0")
    def HUGGINGFACE_LLM_BILINGUAL_RINNA_4_B_INSTRUCTION_PPO_BF16_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_BILINGUAL_RINNA_4B_INSTRUCTION_PPO_BF16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_BILINGUAL_RINNA_4B_INSTRUCTION_PPO_BF16_2_0_0")
    def HUGGINGFACE_LLM_BILINGUAL_RINNA_4_B_INSTRUCTION_PPO_BF16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_BILINGUAL_RINNA_4B_INSTRUCTION_PPO_BF16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_180B_BF16_1_0_0")
    def HUGGINGFACE_LLM_FALCON_180_B_BF16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_180B_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_180B_BF16_1_1_0")
    def HUGGINGFACE_LLM_FALCON_180_B_BF16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_180B_BF16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_180B_BF16_1_2_0")
    def HUGGINGFACE_LLM_FALCON_180_B_BF16_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_180B_BF16_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_180B_BF16_1_3_0")
    def HUGGINGFACE_LLM_FALCON_180_B_BF16_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_180B_BF16_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_180B_BF16_1_4_0")
    def HUGGINGFACE_LLM_FALCON_180_B_BF16_1_4_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_180B_BF16_1_4_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_180B_CHAT_BF16_1_0_0")
    def HUGGINGFACE_LLM_FALCON_180_B_CHAT_BF16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_180B_CHAT_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_180B_CHAT_BF16_1_1_0")
    def HUGGINGFACE_LLM_FALCON_180_B_CHAT_BF16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_180B_CHAT_BF16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_180B_CHAT_BF16_1_2_0")
    def HUGGINGFACE_LLM_FALCON_180_B_CHAT_BF16_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_180B_CHAT_BF16_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_BF16_1_0_0")
    def HUGGINGFACE_LLM_FALCON_40_B_BF16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_BF16_1_1_0")
    def HUGGINGFACE_LLM_FALCON_40_B_BF16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_BF16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_BF16_1_2_0")
    def HUGGINGFACE_LLM_FALCON_40_B_BF16_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_BF16_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_BF16_1_3_0")
    def HUGGINGFACE_LLM_FALCON_40_B_BF16_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_BF16_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_BF16_1_3_1")
    def HUGGINGFACE_LLM_FALCON_40_B_BF16_1_3_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_BF16_1_3_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_BF16_1_3_2")
    def HUGGINGFACE_LLM_FALCON_40_B_BF16_1_3_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_BF16_1_3_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_BF16_1_3_3")
    def HUGGINGFACE_LLM_FALCON_40_B_BF16_1_3_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_BF16_1_3_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_BF16_2_0_0")
    def HUGGINGFACE_LLM_FALCON_40_B_BF16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_BF16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_BF16_2_0_1")
    def HUGGINGFACE_LLM_FALCON_40_B_BF16_2_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_BF16_2_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_1_0_0")
    def HUGGINGFACE_LLM_FALCON_40_B_INSTRUCT_BF16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_1_1_0")
    def HUGGINGFACE_LLM_FALCON_40_B_INSTRUCT_BF16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_1_2_0")
    def HUGGINGFACE_LLM_FALCON_40_B_INSTRUCT_BF16_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_1_3_0")
    def HUGGINGFACE_LLM_FALCON_40_B_INSTRUCT_BF16_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_1_3_1")
    def HUGGINGFACE_LLM_FALCON_40_B_INSTRUCT_BF16_1_3_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_1_3_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_1_3_2")
    def HUGGINGFACE_LLM_FALCON_40_B_INSTRUCT_BF16_1_3_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_1_3_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_1_3_3")
    def HUGGINGFACE_LLM_FALCON_40_B_INSTRUCT_BF16_1_3_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_1_3_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_2_0_0")
    def HUGGINGFACE_LLM_FALCON_40_B_INSTRUCT_BF16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_2_0_1")
    def HUGGINGFACE_LLM_FALCON_40_B_INSTRUCT_BF16_2_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_40B_INSTRUCT_BF16_2_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_BF16_1_0_0")
    def HUGGINGFACE_LLM_FALCON_7_B_BF16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_BF16_1_1_0")
    def HUGGINGFACE_LLM_FALCON_7_B_BF16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_BF16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_BF16_1_1_1")
    def HUGGINGFACE_LLM_FALCON_7_B_BF16_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_BF16_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_BF16_1_2_0")
    def HUGGINGFACE_LLM_FALCON_7_B_BF16_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_BF16_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_BF16_1_2_1")
    def HUGGINGFACE_LLM_FALCON_7_B_BF16_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_BF16_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_BF16_1_3_0")
    def HUGGINGFACE_LLM_FALCON_7_B_BF16_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_BF16_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_BF16_1_3_1")
    def HUGGINGFACE_LLM_FALCON_7_B_BF16_1_3_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_BF16_1_3_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_BF16_1_3_2")
    def HUGGINGFACE_LLM_FALCON_7_B_BF16_1_3_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_BF16_1_3_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_BF16_2_0_0")
    def HUGGINGFACE_LLM_FALCON_7_B_BF16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_BF16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_BF16_2_0_1")
    def HUGGINGFACE_LLM_FALCON_7_B_BF16_2_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_BF16_2_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_1_0_0")
    def HUGGINGFACE_LLM_FALCON_7_B_INSTRUCT_BF16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_1_1_0")
    def HUGGINGFACE_LLM_FALCON_7_B_INSTRUCT_BF16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_1_1_1")
    def HUGGINGFACE_LLM_FALCON_7_B_INSTRUCT_BF16_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_1_2_0")
    def HUGGINGFACE_LLM_FALCON_7_B_INSTRUCT_BF16_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_1_2_1")
    def HUGGINGFACE_LLM_FALCON_7_B_INSTRUCT_BF16_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_1_3_0")
    def HUGGINGFACE_LLM_FALCON_7_B_INSTRUCT_BF16_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_1_3_1")
    def HUGGINGFACE_LLM_FALCON_7_B_INSTRUCT_BF16_1_3_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_1_3_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_1_3_2")
    def HUGGINGFACE_LLM_FALCON_7_B_INSTRUCT_BF16_1_3_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_1_3_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_2_0_0")
    def HUGGINGFACE_LLM_FALCON_7_B_INSTRUCT_BF16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_2_0_1")
    def HUGGINGFACE_LLM_FALCON_7_B_INSTRUCT_BF16_2_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_FALCON_7B_INSTRUCT_BF16_2_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_MISTRAL_7B_1_0_0")
    def HUGGINGFACE_LLM_MISTRAL_7_B_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_MISTRAL_7B_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_MISTRAL_7B_1_1_0")
    def HUGGINGFACE_LLM_MISTRAL_7_B_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_MISTRAL_7B_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_MISTRAL_7B_2_0_0")
    def HUGGINGFACE_LLM_MISTRAL_7_B_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_MISTRAL_7B_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_MISTRAL_7B_2_0_1")
    def HUGGINGFACE_LLM_MISTRAL_7_B_2_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_MISTRAL_7B_2_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_MISTRAL_7B_INSTRUCT_1_0_0")
    def HUGGINGFACE_LLM_MISTRAL_7_B_INSTRUCT_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_MISTRAL_7B_INSTRUCT_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_MISTRAL_7B_INSTRUCT_2_0_0")
    def HUGGINGFACE_LLM_MISTRAL_7_B_INSTRUCT_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_MISTRAL_7B_INSTRUCT_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_MIXTRAL_8X7B_1_0_0")
    def HUGGINGFACE_LLM_MIXTRAL_8_X7_B_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_MIXTRAL_8X7B_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_MIXTRAL_8X7B_1_0_1")
    def HUGGINGFACE_LLM_MIXTRAL_8_X7_B_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_MIXTRAL_8X7B_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_MIXTRAL_8X7B_INSTRUCT_1_0_0")
    def HUGGINGFACE_LLM_MIXTRAL_8_X7_B_INSTRUCT_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_MIXTRAL_8X7B_INSTRUCT_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_MIXTRAL_8X7B_INSTRUCT_1_0_1")
    def HUGGINGFACE_LLM_MIXTRAL_8_X7_B_INSTRUCT_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_MIXTRAL_8X7B_INSTRUCT_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_RINNA_3_6B_INSTRUCTION_PPO_BF16_1_0_0")
    def HUGGINGFACE_LLM_RINNA_3_6_B_INSTRUCTION_PPO_BF16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_RINNA_3_6B_INSTRUCTION_PPO_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_RINNA_3_6B_INSTRUCTION_PPO_BF16_1_1_0")
    def HUGGINGFACE_LLM_RINNA_3_6_B_INSTRUCTION_PPO_BF16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_RINNA_3_6B_INSTRUCTION_PPO_BF16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_RINNA_3_6B_INSTRUCTION_PPO_BF16_1_1_1")
    def HUGGINGFACE_LLM_RINNA_3_6_B_INSTRUCTION_PPO_BF16_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_RINNA_3_6B_INSTRUCTION_PPO_BF16_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_RINNA_3_6B_INSTRUCTION_PPO_BF16_1_2_0")
    def HUGGINGFACE_LLM_RINNA_3_6_B_INSTRUCTION_PPO_BF16_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_RINNA_3_6B_INSTRUCTION_PPO_BF16_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_RINNA_3_6B_INSTRUCTION_PPO_BF16_1_3_0")
    def HUGGINGFACE_LLM_RINNA_3_6_B_INSTRUCTION_PPO_BF16_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_RINNA_3_6B_INSTRUCTION_PPO_BF16_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_LLM_RINNA_3_6B_INSTRUCTION_PPO_BF16_2_0_0")
    def HUGGINGFACE_LLM_RINNA_3_6_B_INSTRUCTION_PPO_BF16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_LLM_RINNA_3_6B_INSTRUCTION_PPO_BF16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_NER_DISTILBERT_BASE_CASED_FINETUNED_CONLL03_ENGLISH_1_0_0")
    def HUGGINGFACE_NER_DISTILBERT_BASE_CASED_FINETUNED_CONLL03_ENGLISH_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_NER_DISTILBERT_BASE_CASED_FINETUNED_CONLL03_ENGLISH_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_NER_DISTILBERT_BASE_CASED_FINETUNED_CONLL03_ENGLISH_1_1_0")
    def HUGGINGFACE_NER_DISTILBERT_BASE_CASED_FINETUNED_CONLL03_ENGLISH_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_NER_DISTILBERT_BASE_CASED_FINETUNED_CONLL03_ENGLISH_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_NER_DISTILBERT_BASE_CASED_FINETUNED_CONLL03_ENGLISH_2_0_0")
    def HUGGINGFACE_NER_DISTILBERT_BASE_CASED_FINETUNED_CONLL03_ENGLISH_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_NER_DISTILBERT_BASE_CASED_FINETUNED_CONLL03_ENGLISH_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_NER_DISTILBERT_BASE_UNCASED_FINETUNED_CONLL03_ENGLISH_1_0_0")
    def HUGGINGFACE_NER_DISTILBERT_BASE_UNCASED_FINETUNED_CONLL03_ENGLISH_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_NER_DISTILBERT_BASE_UNCASED_FINETUNED_CONLL03_ENGLISH_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_NER_DISTILBERT_BASE_UNCASED_FINETUNED_CONLL03_ENGLISH_1_1_0")
    def HUGGINGFACE_NER_DISTILBERT_BASE_UNCASED_FINETUNED_CONLL03_ENGLISH_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_NER_DISTILBERT_BASE_UNCASED_FINETUNED_CONLL03_ENGLISH_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_NER_DISTILBERT_BASE_UNCASED_FINETUNED_CONLL03_ENGLISH_2_0_0")
    def HUGGINGFACE_NER_DISTILBERT_BASE_UNCASED_FINETUNED_CONLL03_ENGLISH_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_NER_DISTILBERT_BASE_UNCASED_FINETUNED_CONLL03_ENGLISH_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_ALL_MINILM_L6_V2_1_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_ALL_MINILM_L6_V2_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_ALL_MINILM_L6_V2_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_ALL_MINILM_L6_V2_1_1_0")
    def HUGGINGFACE_SENTENCESIMILARITY_ALL_MINILM_L6_V2_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_ALL_MINILM_L6_V2_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_ALL_MINILM_L6_V2_1_1_1")
    def HUGGINGFACE_SENTENCESIMILARITY_ALL_MINILM_L6_V2_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_ALL_MINILM_L6_V2_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_ALL_MINILM_L6_V2_2_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_ALL_MINILM_L6_V2_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_ALL_MINILM_L6_V2_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_BGE_BASE_EN_1_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_BGE_BASE_EN_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_BGE_BASE_EN_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_BGE_BASE_EN_1_0_1")
    def HUGGINGFACE_SENTENCESIMILARITY_BGE_BASE_EN_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_BGE_BASE_EN_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_BGE_BASE_EN_2_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_BGE_BASE_EN_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_BGE_BASE_EN_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_BGE_LARGE_EN_1_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_BGE_LARGE_EN_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_BGE_LARGE_EN_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_BGE_LARGE_EN_1_0_1")
    def HUGGINGFACE_SENTENCESIMILARITY_BGE_LARGE_EN_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_BGE_LARGE_EN_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_BGE_LARGE_EN_2_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_BGE_LARGE_EN_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_BGE_LARGE_EN_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_BGE_SMALL_EN_1_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_BGE_SMALL_EN_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_BGE_SMALL_EN_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_BGE_SMALL_EN_1_0_1")
    def HUGGINGFACE_SENTENCESIMILARITY_BGE_SMALL_EN_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_BGE_SMALL_EN_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_BGE_SMALL_EN_2_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_BGE_SMALL_EN_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_BGE_SMALL_EN_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_1_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_1_0_1")
    def HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_2_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_V2_1_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_V2_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_V2_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_V2_1_0_1")
    def HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_V2_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_V2_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_V2_2_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_V2_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_E5_BASE_V2_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_1_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_1_0_1")
    def HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_2_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_V2_1_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_V2_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_V2_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_V2_1_0_1")
    def HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_V2_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_V2_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_V2_2_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_V2_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_E5_LARGE_V2_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_E5_SMALL_V2_1_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_E5_SMALL_V2_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_E5_SMALL_V2_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_E5_SMALL_V2_1_0_1")
    def HUGGINGFACE_SENTENCESIMILARITY_E5_SMALL_V2_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_E5_SMALL_V2_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_E5_SMALL_V2_2_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_E5_SMALL_V2_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_E5_SMALL_V2_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_GTE_BASE_1_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_GTE_BASE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_GTE_BASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_GTE_BASE_1_0_1")
    def HUGGINGFACE_SENTENCESIMILARITY_GTE_BASE_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_GTE_BASE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_GTE_BASE_2_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_GTE_BASE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_GTE_BASE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_GTE_LARGE_1_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_GTE_LARGE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_GTE_LARGE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_GTE_LARGE_1_0_1")
    def HUGGINGFACE_SENTENCESIMILARITY_GTE_LARGE_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_GTE_LARGE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_GTE_LARGE_2_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_GTE_LARGE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_GTE_LARGE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_GTE_SMALL_1_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_GTE_SMALL_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_GTE_SMALL_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_GTE_SMALL_1_0_1")
    def HUGGINGFACE_SENTENCESIMILARITY_GTE_SMALL_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_GTE_SMALL_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_GTE_SMALL_2_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_GTE_SMALL_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_GTE_SMALL_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_BASE_1_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_BASE_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_BASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_BASE_1_0_1")
    def HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_BASE_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_BASE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_BASE_2_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_BASE_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_BASE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_LARGE_1_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_LARGE_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_LARGE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_LARGE_1_0_1")
    def HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_LARGE_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_LARGE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_LARGE_2_0_0")
    def HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_LARGE_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SENTENCESIMILARITY_MULTILINGUAL_E5_LARGE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_CASED_1_0_0")
    def HUGGINGFACE_SPC_BERT_BASE_CASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_CASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_CASED_1_1_0")
    def HUGGINGFACE_SPC_BERT_BASE_CASED_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_CASED_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_CASED_1_2_0")
    def HUGGINGFACE_SPC_BERT_BASE_CASED_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_CASED_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_CASED_1_2_1")
    def HUGGINGFACE_SPC_BERT_BASE_CASED_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_CASED_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_CASED_1_2_2")
    def HUGGINGFACE_SPC_BERT_BASE_CASED_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_CASED_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_CASED_1_2_3")
    def HUGGINGFACE_SPC_BERT_BASE_CASED_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_CASED_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_CASED_2_0_0")
    def HUGGINGFACE_SPC_BERT_BASE_CASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_CASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_0_0")
    def HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_1_0")
    def HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_2_0")
    def HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_2_1")
    def HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_2_2")
    def HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_2_3")
    def HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_2_0_0")
    def HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_CASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_0_0")
    def HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_1_0")
    def HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_2_0")
    def HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_2_1")
    def HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_2_2")
    def HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_2_3")
    def HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_2_0_0")
    def HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_MULTILINGUAL_UNCASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_0_0")
    def HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_1_0")
    def HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_2_0")
    def HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_2_1")
    def HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_2_2")
    def HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_2_3")
    def HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_UNCASED_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_BASE_UNCASED_2_0_0")
    def HUGGINGFACE_SPC_BERT_BASE_UNCASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_BASE_UNCASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_CASED_1_0_0")
    def HUGGINGFACE_SPC_BERT_LARGE_CASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_CASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_CASED_1_1_0")
    def HUGGINGFACE_SPC_BERT_LARGE_CASED_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_CASED_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_CASED_1_2_0")
    def HUGGINGFACE_SPC_BERT_LARGE_CASED_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_CASED_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_CASED_1_2_1")
    def HUGGINGFACE_SPC_BERT_LARGE_CASED_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_CASED_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_CASED_1_2_2")
    def HUGGINGFACE_SPC_BERT_LARGE_CASED_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_CASED_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_CASED_1_2_3")
    def HUGGINGFACE_SPC_BERT_LARGE_CASED_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_CASED_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_CASED_2_0_0")
    def HUGGINGFACE_SPC_BERT_LARGE_CASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_CASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_0")
    def HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_1_0")
    def HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_2_0")
    def HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_2_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_2_1")
    def HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_2_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_2_2")
    def HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_2_2(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_2_3")
    def HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_2_3(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_2_0_0")
    def HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_0_0")
    def HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_1_0")
    def HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_2_0")
    def HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_2_1")
    def HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_2_2")
    def HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_2_3")
    def HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_UNCASED_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_UNCASED_2_0_0")
    def HUGGINGFACE_SPC_BERT_LARGE_UNCASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_UNCASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_0")
    def HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_1_0")
    def HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_2_0")
    def HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_2_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_2_1")
    def HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_2_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_2_2")
    def HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_2_2(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_2_3")
    def HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_2_3(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_2_0_0")
    def HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_0_0")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_1_0")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_2_0")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_2_1")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_2_2")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_2_3")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_2_0_0")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_CASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_0")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_1_0")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_2_0")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_2_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_2_1")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_2_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_2_2")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_2_2(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_2_3")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_2_3(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_2_0_0")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_MULTILINGUAL_CASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_0_0")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_1_0")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_2_0")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_2_1")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_2_2")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_2_3")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_2_0_0")
    def HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILBERT_BASE_UNCASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_0_0")
    def HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_1_0")
    def HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_2_0")
    def HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_2_1")
    def HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_2_2")
    def HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_2_3")
    def HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILROBERTA_BASE_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_DISTILROBERTA_BASE_2_0_0")
    def HUGGINGFACE_SPC_DISTILROBERTA_BASE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_DISTILROBERTA_BASE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_BASE_1_0_0")
    def HUGGINGFACE_SPC_ROBERTA_BASE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_BASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_BASE_1_1_0")
    def HUGGINGFACE_SPC_ROBERTA_BASE_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_BASE_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_BASE_1_2_0")
    def HUGGINGFACE_SPC_ROBERTA_BASE_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_BASE_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_BASE_1_2_1")
    def HUGGINGFACE_SPC_ROBERTA_BASE_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_BASE_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_BASE_1_2_2")
    def HUGGINGFACE_SPC_ROBERTA_BASE_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_BASE_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_BASE_1_2_3")
    def HUGGINGFACE_SPC_ROBERTA_BASE_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_BASE_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_BASE_2_0_0")
    def HUGGINGFACE_SPC_ROBERTA_BASE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_BASE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_0_0")
    def HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_1_0")
    def HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_2_0")
    def HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_2_1")
    def HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_2_2")
    def HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_2_3")
    def HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_2_0_0")
    def HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_BASE_OPENAI_DETECTOR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_LARGE_1_0_0")
    def HUGGINGFACE_SPC_ROBERTA_LARGE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_LARGE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_LARGE_1_1_0")
    def HUGGINGFACE_SPC_ROBERTA_LARGE_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_LARGE_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_LARGE_1_2_0")
    def HUGGINGFACE_SPC_ROBERTA_LARGE_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_LARGE_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_LARGE_1_2_1")
    def HUGGINGFACE_SPC_ROBERTA_LARGE_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_LARGE_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_LARGE_1_2_2")
    def HUGGINGFACE_SPC_ROBERTA_LARGE_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_LARGE_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_LARGE_1_2_3")
    def HUGGINGFACE_SPC_ROBERTA_LARGE_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_LARGE_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_LARGE_2_0_0")
    def HUGGINGFACE_SPC_ROBERTA_LARGE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_LARGE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_0_0")
    def HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_1_0")
    def HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_2_0")
    def HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_2_1")
    def HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_2_2")
    def HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_2_3")
    def HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_2_0_0")
    def HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_ROBERTA_LARGE_OPENAI_DETECTOR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_0_0")
    def HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_1_0")
    def HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_2_0")
    def HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_2_1")
    def HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_2_2")
    def HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_2_3")
    def HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_2_0_0")
    def HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_CLM_ENDE_1024_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_0_0")
    def HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_1_0")
    def HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_2_0")
    def HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_2_1")
    def HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_2_2")
    def HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_2_3")
    def HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_2_0_0")
    def HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_ENDE_1024_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_0_0")
    def HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_1_0")
    def HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_2_0")
    def HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_2_1")
    def HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_2_2")
    def HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_2_3")
    def HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_2_0_0")
    def HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_ENRO_1024_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_0_0")
    def HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_1_0")
    def HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_2_0")
    def HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_2_1")
    def HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_2_2")
    def HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_2_3")
    def HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_2_0_0")
    def HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_TLM_XNLI15_1024_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_0_0")
    def HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_1_0")
    def HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_2_0")
    def HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_2_1")
    def HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_2_2")
    def HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_2_3")
    def HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_2_0_0")
    def HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SPC_XLM_MLM_XNLI15_1024_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_BART_LARGE_CNN_SAMSUM_1_0_0")
    def HUGGINGFACE_SUMMARIZATION_BART_LARGE_CNN_SAMSUM_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_BART_LARGE_CNN_SAMSUM_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_BART_LARGE_CNN_SAMSUM_1_1_0")
    def HUGGINGFACE_SUMMARIZATION_BART_LARGE_CNN_SAMSUM_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_BART_LARGE_CNN_SAMSUM_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_BART_LARGE_CNN_SAMSUM_1_2_0")
    def HUGGINGFACE_SUMMARIZATION_BART_LARGE_CNN_SAMSUM_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_BART_LARGE_CNN_SAMSUM_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_BART_LARGE_CNN_SAMSUM_2_0_0")
    def HUGGINGFACE_SUMMARIZATION_BART_LARGE_CNN_SAMSUM_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_BART_LARGE_CNN_SAMSUM_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_BERT_SMALL2BERT_SMALL_FINETUNED_CNN_DAILY_MAIL_SUMMARIZATION_1_0_0")
    def HUGGINGFACE_SUMMARIZATION_BERT_SMALL2_BERT_SMALL_FINETUNED_CNN_DAILY_MAIL_SUMMARIZATION_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_BERT_SMALL2BERT_SMALL_FINETUNED_CNN_DAILY_MAIL_SUMMARIZATION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_BERT_SMALL2BERT_SMALL_FINETUNED_CNN_DAILY_MAIL_SUMMARIZATION_1_1_0")
    def HUGGINGFACE_SUMMARIZATION_BERT_SMALL2_BERT_SMALL_FINETUNED_CNN_DAILY_MAIL_SUMMARIZATION_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_BERT_SMALL2BERT_SMALL_FINETUNED_CNN_DAILY_MAIL_SUMMARIZATION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_BERT_SMALL2BERT_SMALL_FINETUNED_CNN_DAILY_MAIL_SUMMARIZATION_1_2_0")
    def HUGGINGFACE_SUMMARIZATION_BERT_SMALL2_BERT_SMALL_FINETUNED_CNN_DAILY_MAIL_SUMMARIZATION_1_2_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_BERT_SMALL2BERT_SMALL_FINETUNED_CNN_DAILY_MAIL_SUMMARIZATION_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_BERT_SMALL2BERT_SMALL_FINETUNED_CNN_DAILY_MAIL_SUMMARIZATION_2_0_0")
    def HUGGINGFACE_SUMMARIZATION_BERT_SMALL2_BERT_SMALL_FINETUNED_CNN_DAILY_MAIL_SUMMARIZATION_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_BERT_SMALL2BERT_SMALL_FINETUNED_CNN_DAILY_MAIL_SUMMARIZATION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_ARXIV_1_0_0")
    def HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_ARXIV_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_ARXIV_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_ARXIV_1_1_0")
    def HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_ARXIV_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_ARXIV_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_ARXIV_1_2_0")
    def HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_ARXIV_1_2_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_ARXIV_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_ARXIV_2_0_0")
    def HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_ARXIV_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_ARXIV_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_PUBMED_1_0_0")
    def HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_PUBMED_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_PUBMED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_PUBMED_1_1_0")
    def HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_PUBMED_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_PUBMED_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_PUBMED_1_2_0")
    def HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_PUBMED_1_2_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_PUBMED_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_PUBMED_2_0_0")
    def HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_PUBMED_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_BIGBIRD_PEGASUS_LARGE_PUBMED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_12_6_1_0_0")
    def HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_12_6_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_12_6_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_12_6_1_1_0")
    def HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_12_6_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_12_6_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_12_6_1_2_0")
    def HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_12_6_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_12_6_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_12_6_2_0_0")
    def HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_12_6_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_12_6_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_6_6_1_0_0")
    def HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_6_6_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_6_6_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_6_6_1_1_0")
    def HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_6_6_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_6_6_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_6_6_1_2_0")
    def HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_6_6_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_6_6_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_6_6_2_0_0")
    def HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_6_6_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_DISTILBART_CNN_6_6_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_1_1_1_0_0")
    def HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_1_1_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_1_1_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_1_1_1_1_0")
    def HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_1_1_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_1_1_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_1_1_1_2_0")
    def HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_1_1_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_1_1_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_1_1_2_0_0")
    def HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_1_1_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_1_1_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_12_3_1_0_0")
    def HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_12_3_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_12_3_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_12_3_1_1_0")
    def HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_12_3_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_12_3_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_12_3_1_2_0")
    def HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_12_3_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_12_3_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_12_3_2_0_0")
    def HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_12_3_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_SUMMARIZATION_DISTILBART_XSUM_12_3_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_BASE_CASED_1_0_0")
    def HUGGINGFACE_TC_BERT_BASE_CASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_BASE_CASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_BASE_CASED_1_0_1")
    def HUGGINGFACE_TC_BERT_BASE_CASED_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_BASE_CASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_BASE_CASED_1_0_2")
    def HUGGINGFACE_TC_BERT_BASE_CASED_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_BASE_CASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_BASE_CASED_2_0_0")
    def HUGGINGFACE_TC_BERT_BASE_CASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_BASE_CASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_CASED_1_0_0")
    def HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_CASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_CASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_CASED_1_0_1")
    def HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_CASED_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_CASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_CASED_1_0_2")
    def HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_CASED_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_CASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_CASED_2_0_0")
    def HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_CASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_CASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_UNCASED_1_0_0")
    def HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_UNCASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_UNCASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_UNCASED_1_0_1")
    def HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_UNCASED_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_UNCASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_UNCASED_1_0_2")
    def HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_UNCASED_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_UNCASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_UNCASED_2_0_0")
    def HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_UNCASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_BASE_MULTILINGUAL_UNCASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_BASE_UNCASED_1_0_0")
    def HUGGINGFACE_TC_BERT_BASE_UNCASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_BASE_UNCASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_BASE_UNCASED_1_0_1")
    def HUGGINGFACE_TC_BERT_BASE_UNCASED_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_BASE_UNCASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_BASE_UNCASED_1_0_2")
    def HUGGINGFACE_TC_BERT_BASE_UNCASED_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_BASE_UNCASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_BASE_UNCASED_2_0_0")
    def HUGGINGFACE_TC_BERT_BASE_UNCASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_BASE_UNCASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_LARGE_CASED_1_0_0")
    def HUGGINGFACE_TC_BERT_LARGE_CASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_LARGE_CASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_LARGE_CASED_1_0_1")
    def HUGGINGFACE_TC_BERT_LARGE_CASED_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_LARGE_CASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_LARGE_CASED_1_0_2")
    def HUGGINGFACE_TC_BERT_LARGE_CASED_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_LARGE_CASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_LARGE_CASED_2_0_0")
    def HUGGINGFACE_TC_BERT_LARGE_CASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_LARGE_CASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_0")
    def HUGGINGFACE_TC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_1")
    def HUGGINGFACE_TC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_2")
    def HUGGINGFACE_TC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_2(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_2_0_0")
    def HUGGINGFACE_TC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_LARGE_CASED_WHOLE_WORD_MASKING_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_LARGE_UNCASED_1_0_0")
    def HUGGINGFACE_TC_BERT_LARGE_UNCASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_LARGE_UNCASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_LARGE_UNCASED_1_0_1")
    def HUGGINGFACE_TC_BERT_LARGE_UNCASED_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_LARGE_UNCASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_LARGE_UNCASED_1_0_2")
    def HUGGINGFACE_TC_BERT_LARGE_UNCASED_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_LARGE_UNCASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_LARGE_UNCASED_2_0_0")
    def HUGGINGFACE_TC_BERT_LARGE_UNCASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_LARGE_UNCASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_0")
    def HUGGINGFACE_TC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_1")
    def HUGGINGFACE_TC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_2")
    def HUGGINGFACE_TC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_2(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_2_0_0")
    def HUGGINGFACE_TC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_BERT_LARGE_UNCASED_WHOLE_WORD_MASKING_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_DISTILBERT_BASE_CASED_1_0_0")
    def HUGGINGFACE_TC_DISTILBERT_BASE_CASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_DISTILBERT_BASE_CASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_DISTILBERT_BASE_CASED_1_0_1")
    def HUGGINGFACE_TC_DISTILBERT_BASE_CASED_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_DISTILBERT_BASE_CASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_DISTILBERT_BASE_CASED_1_0_2")
    def HUGGINGFACE_TC_DISTILBERT_BASE_CASED_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_DISTILBERT_BASE_CASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_DISTILBERT_BASE_CASED_2_0_0")
    def HUGGINGFACE_TC_DISTILBERT_BASE_CASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_DISTILBERT_BASE_CASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_0")
    def HUGGINGFACE_TC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_1")
    def HUGGINGFACE_TC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_2")
    def HUGGINGFACE_TC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_2(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_DISTILBERT_BASE_MULTILINGUAL_CASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_DISTILBERT_BASE_MULTILINGUAL_CASED_2_0_0")
    def HUGGINGFACE_TC_DISTILBERT_BASE_MULTILINGUAL_CASED_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_DISTILBERT_BASE_MULTILINGUAL_CASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_DISTILBERT_BASE_UNCASED_1_0_0")
    def HUGGINGFACE_TC_DISTILBERT_BASE_UNCASED_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_DISTILBERT_BASE_UNCASED_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_DISTILBERT_BASE_UNCASED_1_0_1")
    def HUGGINGFACE_TC_DISTILBERT_BASE_UNCASED_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_DISTILBERT_BASE_UNCASED_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_DISTILBERT_BASE_UNCASED_1_0_2")
    def HUGGINGFACE_TC_DISTILBERT_BASE_UNCASED_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_DISTILBERT_BASE_UNCASED_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_DISTILBERT_BASE_UNCASED_2_0_0")
    def HUGGINGFACE_TC_DISTILBERT_BASE_UNCASED_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_DISTILBERT_BASE_UNCASED_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_DISTILROBERTA_BASE_1_0_0")
    def HUGGINGFACE_TC_DISTILROBERTA_BASE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_DISTILROBERTA_BASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_DISTILROBERTA_BASE_1_0_1")
    def HUGGINGFACE_TC_DISTILROBERTA_BASE_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_DISTILROBERTA_BASE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_DISTILROBERTA_BASE_1_0_2")
    def HUGGINGFACE_TC_DISTILROBERTA_BASE_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_DISTILROBERTA_BASE_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_DISTILROBERTA_BASE_2_0_0")
    def HUGGINGFACE_TC_DISTILROBERTA_BASE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_DISTILROBERTA_BASE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_MODELS_1_0_0")
    def HUGGINGFACE_TC_MODELS_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_MODELS_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_MODELS_1_0_1")
    def HUGGINGFACE_TC_MODELS_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_MODELS_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_MODELS_1_0_2")
    def HUGGINGFACE_TC_MODELS_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_MODELS_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_MODELS_2_0_0")
    def HUGGINGFACE_TC_MODELS_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_MODELS_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_ROBERTA_BASE_1_0_0")
    def HUGGINGFACE_TC_ROBERTA_BASE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_ROBERTA_BASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_ROBERTA_BASE_1_0_1")
    def HUGGINGFACE_TC_ROBERTA_BASE_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_ROBERTA_BASE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_ROBERTA_BASE_1_0_2")
    def HUGGINGFACE_TC_ROBERTA_BASE_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_ROBERTA_BASE_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_ROBERTA_BASE_2_0_0")
    def HUGGINGFACE_TC_ROBERTA_BASE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_ROBERTA_BASE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_ROBERTA_BASE_OPENAI_DETECTOR_1_0_0")
    def HUGGINGFACE_TC_ROBERTA_BASE_OPENAI_DETECTOR_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_ROBERTA_BASE_OPENAI_DETECTOR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_ROBERTA_BASE_OPENAI_DETECTOR_1_0_1")
    def HUGGINGFACE_TC_ROBERTA_BASE_OPENAI_DETECTOR_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_ROBERTA_BASE_OPENAI_DETECTOR_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_ROBERTA_BASE_OPENAI_DETECTOR_1_0_2")
    def HUGGINGFACE_TC_ROBERTA_BASE_OPENAI_DETECTOR_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_ROBERTA_BASE_OPENAI_DETECTOR_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_ROBERTA_BASE_OPENAI_DETECTOR_2_0_0")
    def HUGGINGFACE_TC_ROBERTA_BASE_OPENAI_DETECTOR_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_ROBERTA_BASE_OPENAI_DETECTOR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_ROBERTA_LARGE_1_0_0")
    def HUGGINGFACE_TC_ROBERTA_LARGE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_ROBERTA_LARGE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_ROBERTA_LARGE_1_0_1")
    def HUGGINGFACE_TC_ROBERTA_LARGE_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_ROBERTA_LARGE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_ROBERTA_LARGE_1_0_2")
    def HUGGINGFACE_TC_ROBERTA_LARGE_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_ROBERTA_LARGE_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_ROBERTA_LARGE_2_0_0")
    def HUGGINGFACE_TC_ROBERTA_LARGE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_ROBERTA_LARGE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_ROBERTA_LARGE_OPENAI_DETECTOR_1_0_0")
    def HUGGINGFACE_TC_ROBERTA_LARGE_OPENAI_DETECTOR_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_ROBERTA_LARGE_OPENAI_DETECTOR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_ROBERTA_LARGE_OPENAI_DETECTOR_1_0_1")
    def HUGGINGFACE_TC_ROBERTA_LARGE_OPENAI_DETECTOR_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_ROBERTA_LARGE_OPENAI_DETECTOR_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_ROBERTA_LARGE_OPENAI_DETECTOR_1_0_2")
    def HUGGINGFACE_TC_ROBERTA_LARGE_OPENAI_DETECTOR_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_ROBERTA_LARGE_OPENAI_DETECTOR_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_ROBERTA_LARGE_OPENAI_DETECTOR_2_0_0")
    def HUGGINGFACE_TC_ROBERTA_LARGE_OPENAI_DETECTOR_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_ROBERTA_LARGE_OPENAI_DETECTOR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_XLM_CLM_ENDE_1024_1_0_0")
    def HUGGINGFACE_TC_XLM_CLM_ENDE_1024_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_XLM_CLM_ENDE_1024_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_XLM_CLM_ENDE_1024_1_0_1")
    def HUGGINGFACE_TC_XLM_CLM_ENDE_1024_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_XLM_CLM_ENDE_1024_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_XLM_CLM_ENDE_1024_1_0_2")
    def HUGGINGFACE_TC_XLM_CLM_ENDE_1024_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_XLM_CLM_ENDE_1024_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_XLM_CLM_ENDE_1024_2_0_0")
    def HUGGINGFACE_TC_XLM_CLM_ENDE_1024_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_XLM_CLM_ENDE_1024_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_XLM_MLM_ENDE_1024_1_0_0")
    def HUGGINGFACE_TC_XLM_MLM_ENDE_1024_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_XLM_MLM_ENDE_1024_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_XLM_MLM_ENDE_1024_1_0_1")
    def HUGGINGFACE_TC_XLM_MLM_ENDE_1024_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_XLM_MLM_ENDE_1024_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_XLM_MLM_ENDE_1024_1_0_2")
    def HUGGINGFACE_TC_XLM_MLM_ENDE_1024_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_XLM_MLM_ENDE_1024_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_XLM_MLM_ENDE_1024_2_0_0")
    def HUGGINGFACE_TC_XLM_MLM_ENDE_1024_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_XLM_MLM_ENDE_1024_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_XLM_MLM_ENRO_1024_1_0_0")
    def HUGGINGFACE_TC_XLM_MLM_ENRO_1024_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_XLM_MLM_ENRO_1024_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_XLM_MLM_ENRO_1024_1_0_1")
    def HUGGINGFACE_TC_XLM_MLM_ENRO_1024_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_XLM_MLM_ENRO_1024_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_XLM_MLM_ENRO_1024_1_0_2")
    def HUGGINGFACE_TC_XLM_MLM_ENRO_1024_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_XLM_MLM_ENRO_1024_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_XLM_MLM_ENRO_1024_2_0_0")
    def HUGGINGFACE_TC_XLM_MLM_ENRO_1024_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_XLM_MLM_ENRO_1024_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_XLM_MLM_TLM_XNLI15_1024_1_0_0")
    def HUGGINGFACE_TC_XLM_MLM_TLM_XNLI15_1024_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_XLM_MLM_TLM_XNLI15_1024_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_XLM_MLM_TLM_XNLI15_1024_1_0_1")
    def HUGGINGFACE_TC_XLM_MLM_TLM_XNLI15_1024_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_XLM_MLM_TLM_XNLI15_1024_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_XLM_MLM_TLM_XNLI15_1024_1_0_2")
    def HUGGINGFACE_TC_XLM_MLM_TLM_XNLI15_1024_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_XLM_MLM_TLM_XNLI15_1024_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TC_XLM_MLM_TLM_XNLI15_1024_2_0_0")
    def HUGGINGFACE_TC_XLM_MLM_TLM_XNLI15_1024_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TC_XLM_MLM_TLM_XNLI15_1024_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_0_0")
    def HUGGINGFACE_TEXT2_TEXT_BART4_CSC_BASE_CHINESE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_0_1")
    def HUGGINGFACE_TEXT2_TEXT_BART4_CSC_BASE_CHINESE_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_0_2")
    def HUGGINGFACE_TEXT2_TEXT_BART4_CSC_BASE_CHINESE_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_0_3")
    def HUGGINGFACE_TEXT2_TEXT_BART4_CSC_BASE_CHINESE_1_0_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_1_0")
    def HUGGINGFACE_TEXT2_TEXT_BART4_CSC_BASE_CHINESE_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_1_1")
    def HUGGINGFACE_TEXT2_TEXT_BART4_CSC_BASE_CHINESE_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_2_0")
    def HUGGINGFACE_TEXT2_TEXT_BART4_CSC_BASE_CHINESE_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_2_1")
    def HUGGINGFACE_TEXT2_TEXT_BART4_CSC_BASE_CHINESE_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_2_2")
    def HUGGINGFACE_TEXT2_TEXT_BART4_CSC_BASE_CHINESE_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BART4CSC_BASE_CHINESE_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_1_1_0")
    def HUGGINGFACE_TEXT2_TEXT_BIGSCIENCE_T0_PP_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_1_1_1")
    def HUGGINGFACE_TEXT2_TEXT_BIGSCIENCE_T0_PP_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_1_1_2")
    def HUGGINGFACE_TEXT2_TEXT_BIGSCIENCE_T0_PP_1_1_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_1_1_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_2_0_0")
    def HUGGINGFACE_TEXT2_TEXT_BIGSCIENCE_T0_PP_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_BNB_INT8_1_1_0")
    def HUGGINGFACE_TEXT2_TEXT_BIGSCIENCE_T0_PP_BNB_INT8_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_BNB_INT8_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_BNB_INT8_1_1_1")
    def HUGGINGFACE_TEXT2_TEXT_BIGSCIENCE_T0_PP_BNB_INT8_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_BNB_INT8_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_BNB_INT8_1_1_2")
    def HUGGINGFACE_TEXT2_TEXT_BIGSCIENCE_T0_PP_BNB_INT8_1_1_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_BNB_INT8_1_1_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_FP16_1_1_0")
    def HUGGINGFACE_TEXT2_TEXT_BIGSCIENCE_T0_PP_FP16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_FP16_1_1_1")
    def HUGGINGFACE_TEXT2_TEXT_BIGSCIENCE_T0_PP_FP16_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_FP16_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_FP16_1_1_2")
    def HUGGINGFACE_TEXT2_TEXT_BIGSCIENCE_T0_PP_FP16_1_1_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_BIGSCIENCE_T0PP_FP16_1_1_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_0_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_0_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_0_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_0_3")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_1_0_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_1_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_2_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_2_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_2_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_2_3")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_2_4")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_1_2_4(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_2_4"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_2_5")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_1_2_5(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_2_5"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_3_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_3_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_1_3_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_3_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_3_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_1_3_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_1_3_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_2_0_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_0_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_SAMSUM_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_0_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_SAMSUM_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_0_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_SAMSUM_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_0_3")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_SAMSUM_1_0_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_1_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_SAMSUM_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_1_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_SAMSUM_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_2_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_SAMSUM_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_2_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_SAMSUM_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_2_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_SAMSUM_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_2_0_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_BASE_SAMSUM_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_BASE_SAMSUM_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_0_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_LARGE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_0_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_LARGE_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_0_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_LARGE_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_0_3")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_LARGE_1_0_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_1_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_LARGE_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_1_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_LARGE_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_1_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_LARGE_1_1_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_1_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_1_3")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_LARGE_1_1_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_1_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_1_4")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_LARGE_1_1_4(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_1_4"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_1_5")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_LARGE_1_1_5(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_1_5"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_1_6")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_LARGE_1_1_6(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_1_6"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_2_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_LARGE_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_2_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_LARGE_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_2_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_LARGE_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_2_0_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_LARGE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_LARGE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_0_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_SMALL_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_0_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_SMALL_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_0_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_SMALL_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_0_3")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_SMALL_1_0_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_1_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_SMALL_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_2_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_SMALL_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_2_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_SMALL_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_2_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_SMALL_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_2_3")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_SMALL_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_2_4")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_SMALL_1_2_4(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_2_4"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_2_5")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_SMALL_1_2_5(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_2_5"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_3_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_SMALL_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_3_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_SMALL_1_3_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_3_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_3_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_SMALL_1_3_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_1_3_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_2_0_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_SMALL_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_SMALL_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_0_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XL_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_0_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XL_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_0_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XL_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_0_3")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XL_1_0_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_1_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XL_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_1_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XL_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_1_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XL_1_1_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_1_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_1_3")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XL_1_1_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_1_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_1_4")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XL_1_1_4(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_1_4"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_1_5")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XL_1_1_5(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_1_5"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_1_6")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XL_1_1_6(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_1_6"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_2_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XL_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_2_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XL_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_2_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XL_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_2_0_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XL_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XL_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_1_1_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XXL_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_1_1_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XXL_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_1_1_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XXL_1_1_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_1_1_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_2_0_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XXL_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_BNB_INT8_1_0_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XXL_BNB_INT8_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_BNB_INT8_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_BNB_INT8_1_2_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XXL_BNB_INT8_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_BNB_INT8_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_BNB_INT8_1_2_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XXL_BNB_INT8_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_BNB_INT8_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_BNB_INT8_1_2_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XXL_BNB_INT8_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_BNB_INT8_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_FP16_1_1_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XXL_FP16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_FP16_1_1_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XXL_FP16_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_FP16_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_FP16_1_1_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_T5_XXL_FP16_1_1_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_T5_XXL_FP16_1_1_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_UL2_BF16_1_1_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_UL2_BF16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_UL2_BF16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_UL2_BF16_1_1_1")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_UL2_BF16_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_UL2_BF16_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_UL2_BF16_1_1_2")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_UL2_BF16_1_1_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_UL2_BF16_1_1_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_FLAN_UL2_BF16_2_0_0")
    def HUGGINGFACE_TEXT2_TEXT_FLAN_UL2_BF16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_FLAN_UL2_BF16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_0_0")
    def HUGGINGFACE_TEXT2_TEXT_PEGASUS_PARAPHRASE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_0_1")
    def HUGGINGFACE_TEXT2_TEXT_PEGASUS_PARAPHRASE_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_0_2")
    def HUGGINGFACE_TEXT2_TEXT_PEGASUS_PARAPHRASE_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_0_3")
    def HUGGINGFACE_TEXT2_TEXT_PEGASUS_PARAPHRASE_1_0_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_1_0")
    def HUGGINGFACE_TEXT2_TEXT_PEGASUS_PARAPHRASE_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_1_1")
    def HUGGINGFACE_TEXT2_TEXT_PEGASUS_PARAPHRASE_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_2_0")
    def HUGGINGFACE_TEXT2_TEXT_PEGASUS_PARAPHRASE_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_2_1")
    def HUGGINGFACE_TEXT2_TEXT_PEGASUS_PARAPHRASE_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_2_2")
    def HUGGINGFACE_TEXT2_TEXT_PEGASUS_PARAPHRASE_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_PEGASUS_PARAPHRASE_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_0_0")
    def HUGGINGFACE_TEXT2_TEXT_QCPG_SENTENCES_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_0_1")
    def HUGGINGFACE_TEXT2_TEXT_QCPG_SENTENCES_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_0_2")
    def HUGGINGFACE_TEXT2_TEXT_QCPG_SENTENCES_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_0_3")
    def HUGGINGFACE_TEXT2_TEXT_QCPG_SENTENCES_1_0_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_1_0")
    def HUGGINGFACE_TEXT2_TEXT_QCPG_SENTENCES_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_1_1")
    def HUGGINGFACE_TEXT2_TEXT_QCPG_SENTENCES_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_2_0")
    def HUGGINGFACE_TEXT2_TEXT_QCPG_SENTENCES_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_2_1")
    def HUGGINGFACE_TEXT2_TEXT_QCPG_SENTENCES_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_2_2")
    def HUGGINGFACE_TEXT2_TEXT_QCPG_SENTENCES_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_2_0_0")
    def HUGGINGFACE_TEXT2_TEXT_QCPG_SENTENCES_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_QCPG_SENTENCES_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_0_0")
    def HUGGINGFACE_TEXT2_TEXT_T5_ONE_LINE_SUMMARY_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_0_1")
    def HUGGINGFACE_TEXT2_TEXT_T5_ONE_LINE_SUMMARY_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_0_2")
    def HUGGINGFACE_TEXT2_TEXT_T5_ONE_LINE_SUMMARY_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_0_3")
    def HUGGINGFACE_TEXT2_TEXT_T5_ONE_LINE_SUMMARY_1_0_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_1_0")
    def HUGGINGFACE_TEXT2_TEXT_T5_ONE_LINE_SUMMARY_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_1_1")
    def HUGGINGFACE_TEXT2_TEXT_T5_ONE_LINE_SUMMARY_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_2_0")
    def HUGGINGFACE_TEXT2_TEXT_T5_ONE_LINE_SUMMARY_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_2_1")
    def HUGGINGFACE_TEXT2_TEXT_T5_ONE_LINE_SUMMARY_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_2_2")
    def HUGGINGFACE_TEXT2_TEXT_T5_ONE_LINE_SUMMARY_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_2_0_0")
    def HUGGINGFACE_TEXT2_TEXT_T5_ONE_LINE_SUMMARY_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXT2TEXT_T5_ONE_LINE_SUMMARY_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTEMBEDDING_ALL_MINILM_L6_V2_1_0_0")
    def HUGGINGFACE_TEXTEMBEDDING_ALL_MINILM_L6_V2_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTEMBEDDING_ALL_MINILM_L6_V2_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_1_0_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B1_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_1_0_1")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B1_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_1_0_2")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B1_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_1_0_3")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B1_1_0_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_1_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_1_1_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B1_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_1_2_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B1_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_1_2_1")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B1_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_1_3_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B1_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_2_0_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B1_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B1_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_1_0_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B7_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_1_0_1")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B7_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_1_0_2")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B7_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_1_0_3")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B7_1_0_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_1_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_1_1_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B7_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_1_2_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B7_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_1_2_1")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B7_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_1_3_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B7_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_2_0_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_1_B7_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_1B7_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_560M_1_0_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_560_M_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_560M_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_560M_1_0_1")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_560_M_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_560M_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_560M_1_0_2")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_560_M_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_560M_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_560M_1_0_3")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_560_M_1_0_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_560M_1_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_560M_1_1_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_560_M_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_560M_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_560M_1_2_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_560_M_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_560M_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_560M_1_2_1")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_560_M_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_560M_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_560M_1_3_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_560_M_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_560M_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOM_560M_2_0_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOM_560_M_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOM_560M_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B1_1_0_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOMZ_1_B1_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B1_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B1_1_1_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOMZ_1_B1_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B1_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B1_1_1_1")
    def HUGGINGFACE_TEXTGENERATION_BLOOMZ_1_B1_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B1_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B1_1_2_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOMZ_1_B1_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B1_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B1_2_0_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOMZ_1_B1_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B1_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B7_1_0_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOMZ_1_B7_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B7_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B7_1_1_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOMZ_1_B7_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B7_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B7_1_1_1")
    def HUGGINGFACE_TEXTGENERATION_BLOOMZ_1_B7_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B7_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B7_1_2_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOMZ_1_B7_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B7_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B7_2_0_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOMZ_1_B7_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOMZ_1B7_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOMZ_560M_1_0_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOMZ_560_M_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOMZ_560M_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOMZ_560M_1_1_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOMZ_560_M_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOMZ_560M_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOMZ_560M_1_1_1")
    def HUGGINGFACE_TEXTGENERATION_BLOOMZ_560_M_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOMZ_560M_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOMZ_560M_1_2_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOMZ_560_M_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOMZ_560M_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_BLOOMZ_560M_2_0_0")
    def HUGGINGFACE_TEXTGENERATION_BLOOMZ_560_M_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_BLOOMZ_560M_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_0_0")
    def HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_1_0")
    def HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_2_0")
    def HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_2_1")
    def HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_2_2")
    def HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_2_3")
    def HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_3_0")
    def HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_4_0")
    def HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_4_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_4_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_4_1")
    def HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_4_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_4_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_5_0")
    def HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_5_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DISTILGPT2_1_5_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DISTILGPT2_2_0_0")
    def HUGGINGFACE_TEXTGENERATION_DISTILGPT2_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DISTILGPT2_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DOLLY_V2_12B_BF16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION_DOLLY_V2_12_B_BF16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DOLLY_V2_12B_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DOLLY_V2_12B_BF16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION_DOLLY_V2_12_B_BF16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DOLLY_V2_12B_BF16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DOLLY_V2_12B_BF16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION_DOLLY_V2_12_B_BF16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DOLLY_V2_12B_BF16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DOLLY_V2_3B_BF16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION_DOLLY_V2_3_B_BF16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DOLLY_V2_3B_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DOLLY_V2_3B_BF16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION_DOLLY_V2_3_B_BF16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DOLLY_V2_3B_BF16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DOLLY_V2_3B_BF16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION_DOLLY_V2_3_B_BF16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DOLLY_V2_3B_BF16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DOLLY_V2_7B_BF16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION_DOLLY_V2_7_B_BF16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DOLLY_V2_7B_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DOLLY_V2_7B_BF16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION_DOLLY_V2_7_B_BF16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DOLLY_V2_7B_BF16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_DOLLY_V2_7B_BF16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION_DOLLY_V2_7_B_BF16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_DOLLY_V2_7B_BF16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_FALCON_40B_BF16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION_FALCON_40_B_BF16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_FALCON_40B_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_FALCON_40B_INSTRUCT_BF16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION_FALCON_40_B_INSTRUCT_BF16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_FALCON_40B_INSTRUCT_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_FALCON_7B_BF16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION_FALCON_7_B_BF16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_FALCON_7B_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_FALCON_7B_INSTRUCT_BF16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION_FALCON_7_B_INSTRUCT_BF16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_FALCON_7B_INSTRUCT_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_GPT2_1_0_0")
    def HUGGINGFACE_TEXTGENERATION_GPT2_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_GPT2_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_GPT2_1_1_0")
    def HUGGINGFACE_TEXTGENERATION_GPT2_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_GPT2_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_GPT2_1_2_0")
    def HUGGINGFACE_TEXTGENERATION_GPT2_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_GPT2_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_GPT2_1_2_1")
    def HUGGINGFACE_TEXTGENERATION_GPT2_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_GPT2_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_GPT2_1_2_2")
    def HUGGINGFACE_TEXTGENERATION_GPT2_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_GPT2_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_GPT2_1_2_3")
    def HUGGINGFACE_TEXTGENERATION_GPT2_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_GPT2_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_GPT2_1_3_0")
    def HUGGINGFACE_TEXTGENERATION_GPT2_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_GPT2_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_GPT2_1_4_0")
    def HUGGINGFACE_TEXTGENERATION_GPT2_1_4_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_GPT2_1_4_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_GPT2_1_4_1")
    def HUGGINGFACE_TEXTGENERATION_GPT2_1_4_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_GPT2_1_4_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_GPT2_1_5_0")
    def HUGGINGFACE_TEXTGENERATION_GPT2_1_5_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_GPT2_1_5_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_GPT2_2_0_0")
    def HUGGINGFACE_TEXTGENERATION_GPT2_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_GPT2_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_MODELS_1_0_0")
    def HUGGINGFACE_TEXTGENERATION_MODELS_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_MODELS_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_MODELS_1_0_1")
    def HUGGINGFACE_TEXTGENERATION_MODELS_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_MODELS_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_MODELS_1_0_2")
    def HUGGINGFACE_TEXTGENERATION_MODELS_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_MODELS_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_MODELS_1_1_0")
    def HUGGINGFACE_TEXTGENERATION_MODELS_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_MODELS_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_MODELS_1_2_0")
    def HUGGINGFACE_TEXTGENERATION_MODELS_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_MODELS_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_MODELS_1_2_1")
    def HUGGINGFACE_TEXTGENERATION_MODELS_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_MODELS_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_MODELS_1_3_0")
    def HUGGINGFACE_TEXTGENERATION_MODELS_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_MODELS_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_1_0_0")
    def HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_1_1_0")
    def HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_1_1_1")
    def HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_1_2_0")
    def HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_2_0_0")
    def HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_3_0_0")
    def HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_3_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION_OPEN_LLAMA_3_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_176B_INT8_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_176_B_INT8_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_176B_INT8_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_176B_INT8_1_0_1")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_176_B_INT8_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_176B_INT8_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_176B_INT8_1_0_2")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_176_B_INT8_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_176B_INT8_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_3_B_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_3_B_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_1_2_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_3_B_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_1_2_1")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_3_B_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_1_2_2")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_3_B_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_1_3_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_3_B_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_3_B_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_3_B_FP16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_FP16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_3_B_FP16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_FP16_1_2_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_3_B_FP16_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_FP16_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_FP16_1_2_1")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_3_B_FP16_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_FP16_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_FP16_1_2_2")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_3_B_FP16_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_FP16_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_FP16_1_3_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_3_B_FP16_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_FP16_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_FP16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_3_B_FP16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_3B_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_7_B1_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_7_B1_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_1_2_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_7_B1_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_1_2_1")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_7_B1_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_1_2_2")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_7_B1_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_1_3_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_7_B1_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_7_B1_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_7_B1_FP16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_FP16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_7_B1_FP16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_FP16_1_2_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_7_B1_FP16_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_FP16_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_FP16_1_2_1")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_7_B1_FP16_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_FP16_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_FP16_1_2_2")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_7_B1_FP16_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_FP16_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_FP16_1_3_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_7_B1_FP16_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_FP16_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_FP16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOM_7_B1_FP16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOM_7B1_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOMZ_176B_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOMZ_176_B_FP16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOMZ_176B_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOMZ_176B_FP16_1_0_1")
    def HUGGINGFACE_TEXTGENERATION1_BLOOMZ_176_B_FP16_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOMZ_176B_FP16_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOMZ_176B_FP16_1_0_2")
    def HUGGINGFACE_TEXTGENERATION1_BLOOMZ_176_B_FP16_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOMZ_176B_FP16_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3B_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3_B_FP16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3B_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3B_FP16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3_B_FP16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3B_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3B_FP16_1_2_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3_B_FP16_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3B_FP16_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3B_FP16_1_2_1")
    def HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3_B_FP16_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3B_FP16_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3B_FP16_1_2_2")
    def HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3_B_FP16_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3B_FP16_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3B_FP16_1_3_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3_B_FP16_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3B_FP16_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3B_FP16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3_B_FP16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOMZ_3B_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7B1_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7_B1_FP16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7B1_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7B1_FP16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7_B1_FP16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7B1_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7B1_FP16_1_2_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7_B1_FP16_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7B1_FP16_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7B1_FP16_1_2_1")
    def HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7_B1_FP16_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7B1_FP16_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7B1_FP16_1_2_2")
    def HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7_B1_FP16_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7B1_FP16_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7B1_FP16_1_3_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7_B1_FP16_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7B1_FP16_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7B1_FP16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7_B1_FP16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_BLOOMZ_7B1_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_2_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_2_1")
    def HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_2_2")
    def HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_3_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_2_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_2_1")
    def HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_2_2")
    def HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_3_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_2_XL_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_1_1")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_2_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_2_1")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_2_2")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_2_3")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_2_4")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_1_2_4(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_2_4"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_3_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_FP16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_FP16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_1_1")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_FP16_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_2_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_FP16_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_2_1")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_FP16_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_2_2")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_FP16_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_2_3")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_FP16_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_2_4")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_FP16_1_2_4(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_2_4"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_3_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_FP16_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_J_6_B_FP16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_J_6B_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3_B_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3_B_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_1_2_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3_B_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_1_2_1")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3_B_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_1_2_2")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3_B_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_1_3_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3_B_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3_B_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3_B_FP16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_FP16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3_B_FP16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_FP16_1_2_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3_B_FP16_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_FP16_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_FP16_1_2_1")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3_B_FP16_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_FP16_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_FP16_1_2_2")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3_B_FP16_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_FP16_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_FP16_1_3_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3_B_FP16_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_FP16_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_FP16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3_B_FP16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_1_3B_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125_M_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125_M_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_1_2_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125_M_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_1_2_1")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125_M_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_1_2_2")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125_M_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_1_3_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125_M_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125_M_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125_M_FP16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_FP16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125_M_FP16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_FP16_1_2_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125_M_FP16_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_FP16_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_FP16_1_2_1")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125_M_FP16_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_FP16_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_FP16_1_2_2")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125_M_FP16_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_FP16_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_FP16_1_3_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125_M_FP16_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_FP16_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_FP16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125_M_FP16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_125M_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7_B_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7_B_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_1_2_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7_B_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_1_2_1")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7_B_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_1_2_2")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7_B_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_1_3_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7_B_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7_B_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7_B_FP16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_FP16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7_B_FP16_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_FP16_1_2_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7_B_FP16_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_FP16_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_FP16_1_2_1")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7_B_FP16_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_FP16_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_FP16_1_2_2")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7_B_FP16_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_FP16_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_FP16_1_3_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7_B_FP16_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_FP16_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_FP16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7_B_FP16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_GPT_NEO_2_7B_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_LIGHTGPT_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_LIGHTGPT_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_LIGHTGPT_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_LIGHTGPT_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_LIGHTGPT_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_LIGHTGPT_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_LIGHTGPT_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_LIGHTGPT_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_LIGHTGPT_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_MPT_7B_BF16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_MPT_7_B_BF16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_MPT_7B_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_MPT_7B_BF16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_MPT_7_B_BF16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_MPT_7B_BF16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_MPT_7B_INSTRUCT_BF16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_MPT_7_B_INSTRUCT_BF16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_MPT_7B_INSTRUCT_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_MPT_7B_INSTRUCT_BF16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_MPT_7_B_INSTRUCT_BF16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_MPT_7B_INSTRUCT_BF16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_MPT_7B_STORYWRITER_BF16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_MPT_7_B_STORYWRITER_BF16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_MPT_7B_STORYWRITER_BF16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_MPT_7B_STORYWRITER_BF16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_MPT_7_B_STORYWRITER_BF16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_MPT_7B_STORYWRITER_BF16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_3B_V1_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_3_B_V1_FP16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_3B_V1_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_3B_V1_FP16_1_0_1")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_3_B_V1_FP16_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_3B_V1_FP16_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_3B_V1_FP16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_3_B_V1_FP16_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_3B_V1_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_3B_V1_FP16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_3_B_V1_FP16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_3B_V1_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_7B_V1_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_7_B_V1_FP16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_7B_V1_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_7B_V1_FP16_1_0_1")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_7_B_V1_FP16_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_7B_V1_FP16_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_7B_V1_FP16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_7_B_V1_FP16_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_7B_V1_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_7B_V1_FP16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_7_B_V1_FP16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_BASE_7B_V1_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_3B_V1_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_3_B_V1_FP16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_3B_V1_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_3B_V1_FP16_1_0_1")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_3_B_V1_FP16_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_3B_V1_FP16_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_3B_V1_FP16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_3_B_V1_FP16_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_3B_V1_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_3B_V1_FP16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_3_B_V1_FP16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_3B_V1_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_7B_V1_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_7_B_V1_FP16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_7B_V1_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_7B_V1_FP16_1_0_1")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_7_B_V1_FP16_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_7B_V1_FP16_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_7B_V1_FP16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_7_B_V1_FP16_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_7B_V1_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_7B_V1_FP16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_7_B_V1_FP16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_CHAT_7B_V1_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_3B_V1_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_3_B_V1_FP16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_3B_V1_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_3B_V1_FP16_1_0_1")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_3_B_V1_FP16_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_3B_V1_FP16_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_3B_V1_FP16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_3_B_V1_FP16_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_3B_V1_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_3B_V1_FP16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_3_B_V1_FP16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_3B_V1_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_7B_V1_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_7_B_V1_FP16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_7B_V1_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_7B_V1_FP16_1_0_1")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_7_B_V1_FP16_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_7B_V1_FP16_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_7B_V1_FP16_1_1_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_7_B_V1_FP16_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_7B_V1_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_7B_V1_FP16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_7_B_V1_FP16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION1_REDPAJAMA_INCITE_INSTRUCT_7B_V1_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION2_GPT_NEOX_20B_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION2_GPT_NEOX_20_B_FP16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION2_GPT_NEOX_20B_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION2_GPT_NEOX_20B_FP16_1_0_1")
    def HUGGINGFACE_TEXTGENERATION2_GPT_NEOX_20_B_FP16_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION2_GPT_NEOX_20B_FP16_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION2_GPT_NEOX_20B_FP16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION2_GPT_NEOX_20_B_FP16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION2_GPT_NEOX_20B_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION2_GPT_NEOX_20B_FP16_3_0_0")
    def HUGGINGFACE_TEXTGENERATION2_GPT_NEOX_20_B_FP16_3_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION2_GPT_NEOX_20B_FP16_3_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION2_GPT_NEOXT_CHAT_BASE_20B_FP16_1_0_0")
    def HUGGINGFACE_TEXTGENERATION2_GPT_NEOXT_CHAT_BASE_20_B_FP16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION2_GPT_NEOXT_CHAT_BASE_20B_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION2_GPT_NEOXT_CHAT_BASE_20B_FP16_1_0_1")
    def HUGGINGFACE_TEXTGENERATION2_GPT_NEOXT_CHAT_BASE_20_B_FP16_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION2_GPT_NEOXT_CHAT_BASE_20B_FP16_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION2_GPT_NEOXT_CHAT_BASE_20B_FP16_2_0_0")
    def HUGGINGFACE_TEXTGENERATION2_GPT_NEOXT_CHAT_BASE_20_B_FP16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION2_GPT_NEOXT_CHAT_BASE_20B_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TEXTGENERATION2_GPT_NEOXT_CHAT_BASE_20B_FP16_3_0_0")
    def HUGGINGFACE_TEXTGENERATION2_GPT_NEOXT_CHAT_BASE_20_B_FP16_3_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TEXTGENERATION2_GPT_NEOXT_CHAT_BASE_20B_FP16_3_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TRANSLATION_OPUS_MT_EN_ES_1_0_0")
    def HUGGINGFACE_TRANSLATION_OPUS_MT_EN_ES_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TRANSLATION_OPUS_MT_EN_ES_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TRANSLATION_OPUS_MT_EN_ES_1_1_0")
    def HUGGINGFACE_TRANSLATION_OPUS_MT_EN_ES_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TRANSLATION_OPUS_MT_EN_ES_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TRANSLATION_OPUS_MT_EN_ES_2_0_0")
    def HUGGINGFACE_TRANSLATION_OPUS_MT_EN_ES_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TRANSLATION_OPUS_MT_EN_ES_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TRANSLATION_OPUS_MT_EN_VI_1_0_0")
    def HUGGINGFACE_TRANSLATION_OPUS_MT_EN_VI_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TRANSLATION_OPUS_MT_EN_VI_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TRANSLATION_OPUS_MT_EN_VI_1_1_0")
    def HUGGINGFACE_TRANSLATION_OPUS_MT_EN_VI_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TRANSLATION_OPUS_MT_EN_VI_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TRANSLATION_OPUS_MT_EN_VI_2_0_0")
    def HUGGINGFACE_TRANSLATION_OPUS_MT_EN_VI_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TRANSLATION_OPUS_MT_EN_VI_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TRANSLATION_T5_BASE_1_0_0")
    def HUGGINGFACE_TRANSLATION_T5_BASE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TRANSLATION_T5_BASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TRANSLATION_T5_BASE_1_1_0")
    def HUGGINGFACE_TRANSLATION_T5_BASE_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TRANSLATION_T5_BASE_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TRANSLATION_T5_BASE_2_0_0")
    def HUGGINGFACE_TRANSLATION_T5_BASE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TRANSLATION_T5_BASE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TRANSLATION_T5_LARGE_1_0_0")
    def HUGGINGFACE_TRANSLATION_T5_LARGE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TRANSLATION_T5_LARGE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TRANSLATION_T5_LARGE_1_1_0")
    def HUGGINGFACE_TRANSLATION_T5_LARGE_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TRANSLATION_T5_LARGE_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TRANSLATION_T5_LARGE_2_0_0")
    def HUGGINGFACE_TRANSLATION_T5_LARGE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TRANSLATION_T5_LARGE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TRANSLATION_T5_SMALL_1_0_0")
    def HUGGINGFACE_TRANSLATION_T5_SMALL_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TRANSLATION_T5_SMALL_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TRANSLATION_T5_SMALL_1_1_0")
    def HUGGINGFACE_TRANSLATION_T5_SMALL_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TRANSLATION_T5_SMALL_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TRANSLATION_T5_SMALL_2_0_0")
    def HUGGINGFACE_TRANSLATION_T5_SMALL_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TRANSLATION_T5_SMALL_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_22H_VINTEDOIS_DIFFUSION_V0_1_1_0_0")
    def HUGGINGFACE_TXT2_IMG_22_H_VINTEDOIS_DIFFUSION_V0_1_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_22H_VINTEDOIS_DIFFUSION_V0_1_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_22H_VINTEDOIS_DIFFUSION_V0_1_1_1_0")
    def HUGGINGFACE_TXT2_IMG_22_H_VINTEDOIS_DIFFUSION_V0_1_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_22H_VINTEDOIS_DIFFUSION_V0_1_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_22H_VINTEDOIS_DIFFUSION_V0_1_2_0_0")
    def HUGGINGFACE_TXT2_IMG_22_H_VINTEDOIS_DIFFUSION_V0_1_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_22H_VINTEDOIS_DIFFUSION_V0_1_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_AKIKAGURA_MKGEN_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_AKIKAGURA_MKGEN_DIFFUSION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_AKIKAGURA_MKGEN_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_AKIKAGURA_MKGEN_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_AKIKAGURA_MKGEN_DIFFUSION_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_AKIKAGURA_MKGEN_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_AKIKAGURA_MKGEN_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_AKIKAGURA_MKGEN_DIFFUSION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_AKIKAGURA_MKGEN_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_ALXDFY_NOGGLES_FASTDB_4800_1_0_0")
    def HUGGINGFACE_TXT2_IMG_ALXDFY_NOGGLES_FASTDB_4800_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_ALXDFY_NOGGLES_FASTDB_4800_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_ALXDFY_NOGGLES_FASTDB_4800_1_1_0")
    def HUGGINGFACE_TXT2_IMG_ALXDFY_NOGGLES_FASTDB_4800_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_ALXDFY_NOGGLES_FASTDB_4800_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_ALXDFY_NOGGLES_FASTDB_4800_2_0_0")
    def HUGGINGFACE_TXT2_IMG_ALXDFY_NOGGLES_FASTDB_4800_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_ALXDFY_NOGGLES_FASTDB_4800_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_ALXDFY_NOGGLES9000_1_0_0")
    def HUGGINGFACE_TXT2_IMG_ALXDFY_NOGGLES9000_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_ALXDFY_NOGGLES9000_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_ALXDFY_NOGGLES9000_1_1_0")
    def HUGGINGFACE_TXT2_IMG_ALXDFY_NOGGLES9000_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_ALXDFY_NOGGLES9000_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_ALXDFY_NOGGLES9000_2_0_0")
    def HUGGINGFACE_TXT2_IMG_ALXDFY_NOGGLES9000_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_ALXDFY_NOGGLES9000_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_ANDITE_ANYTHING_V4_0_1_0_0")
    def HUGGINGFACE_TXT2_IMG_ANDITE_ANYTHING_V4_0_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_ANDITE_ANYTHING_V4_0_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_ANDITE_ANYTHING_V4_0_1_1_0")
    def HUGGINGFACE_TXT2_IMG_ANDITE_ANYTHING_V4_0_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_ANDITE_ANYTHING_V4_0_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_ANDITE_ANYTHING_V4_0_2_0_0")
    def HUGGINGFACE_TXT2_IMG_ANDITE_ANYTHING_V4_0_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_ANDITE_ANYTHING_V4_0_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_ASTRALITEHEART_PONY_DIFFUSION_V2_1_0_0")
    def HUGGINGFACE_TXT2_IMG_ASTRALITEHEART_PONY_DIFFUSION_V2_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_ASTRALITEHEART_PONY_DIFFUSION_V2_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_ASTRALITEHEART_PONY_DIFFUSION_V2_1_1_0")
    def HUGGINGFACE_TXT2_IMG_ASTRALITEHEART_PONY_DIFFUSION_V2_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_ASTRALITEHEART_PONY_DIFFUSION_V2_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_ASTRALITEHEART_PONY_DIFFUSION_V2_2_0_0")
    def HUGGINGFACE_TXT2_IMG_ASTRALITEHEART_PONY_DIFFUSION_V2_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_ASTRALITEHEART_PONY_DIFFUSION_V2_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_AVRIK_ABSTRACT_ANIM_SPRITESHEETS_1_0_0")
    def HUGGINGFACE_TXT2_IMG_AVRIK_ABSTRACT_ANIM_SPRITESHEETS_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_AVRIK_ABSTRACT_ANIM_SPRITESHEETS_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_AVRIK_ABSTRACT_ANIM_SPRITESHEETS_1_1_0")
    def HUGGINGFACE_TXT2_IMG_AVRIK_ABSTRACT_ANIM_SPRITESHEETS_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_AVRIK_ABSTRACT_ANIM_SPRITESHEETS_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_AVRIK_ABSTRACT_ANIM_SPRITESHEETS_2_0_0")
    def HUGGINGFACE_TXT2_IMG_AVRIK_ABSTRACT_ANIM_SPRITESHEETS_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_AVRIK_ABSTRACT_ANIM_SPRITESHEETS_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_AYBEECEEDEE_KNOLLINGCASE_1_0_0")
    def HUGGINGFACE_TXT2_IMG_AYBEECEEDEE_KNOLLINGCASE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_AYBEECEEDEE_KNOLLINGCASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_AYBEECEEDEE_KNOLLINGCASE_1_1_0")
    def HUGGINGFACE_TXT2_IMG_AYBEECEEDEE_KNOLLINGCASE_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_AYBEECEEDEE_KNOLLINGCASE_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_AYBEECEEDEE_KNOLLINGCASE_2_0_0")
    def HUGGINGFACE_TXT2_IMG_AYBEECEEDEE_KNOLLINGCASE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_AYBEECEEDEE_KNOLLINGCASE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_BINGSU_MY_K_ANYTHING_V3_0_1_0_0")
    def HUGGINGFACE_TXT2_IMG_BINGSU_MY_K_ANYTHING_V3_0_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_BINGSU_MY_K_ANYTHING_V3_0_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_BINGSU_MY_K_ANYTHING_V3_0_1_1_0")
    def HUGGINGFACE_TXT2_IMG_BINGSU_MY_K_ANYTHING_V3_0_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_BINGSU_MY_K_ANYTHING_V3_0_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_BINGSU_MY_K_ANYTHING_V3_0_2_0_0")
    def HUGGINGFACE_TXT2_IMG_BINGSU_MY_K_ANYTHING_V3_0_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_BINGSU_MY_K_ANYTHING_V3_0_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_BINGSU_MY_KOREAN_STABLE_DIFFUSION_V1_5_1_0_0")
    def HUGGINGFACE_TXT2_IMG_BINGSU_MY_KOREAN_STABLE_DIFFUSION_V1_5_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_BINGSU_MY_KOREAN_STABLE_DIFFUSION_V1_5_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_BINGSU_MY_KOREAN_STABLE_DIFFUSION_V1_5_1_1_0")
    def HUGGINGFACE_TXT2_IMG_BINGSU_MY_KOREAN_STABLE_DIFFUSION_V1_5_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_BINGSU_MY_KOREAN_STABLE_DIFFUSION_V1_5_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_BINGSU_MY_KOREAN_STABLE_DIFFUSION_V1_5_2_0_0")
    def HUGGINGFACE_TXT2_IMG_BINGSU_MY_KOREAN_STABLE_DIFFUSION_V1_5_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_BINGSU_MY_KOREAN_STABLE_DIFFUSION_V1_5_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_BUNTOPSIH_NOVGORANSTEFANOVSKI_1_0_0")
    def HUGGINGFACE_TXT2_IMG_BUNTOPSIH_NOVGORANSTEFANOVSKI_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_BUNTOPSIH_NOVGORANSTEFANOVSKI_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_BUNTOPSIH_NOVGORANSTEFANOVSKI_1_1_0")
    def HUGGINGFACE_TXT2_IMG_BUNTOPSIH_NOVGORANSTEFANOVSKI_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_BUNTOPSIH_NOVGORANSTEFANOVSKI_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_BUNTOPSIH_NOVGORANSTEFANOVSKI_2_0_0")
    def HUGGINGFACE_TXT2_IMG_BUNTOPSIH_NOVGORANSTEFANOVSKI_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_BUNTOPSIH_NOVGORANSTEFANOVSKI_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_CLAUDFUEN_PHOTOREALISTIC_FUEN_V1_1_0_0")
    def HUGGINGFACE_TXT2_IMG_CLAUDFUEN_PHOTOREALISTIC_FUEN_V1_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_CLAUDFUEN_PHOTOREALISTIC_FUEN_V1_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_CLAUDFUEN_PHOTOREALISTIC_FUEN_V1_1_1_0")
    def HUGGINGFACE_TXT2_IMG_CLAUDFUEN_PHOTOREALISTIC_FUEN_V1_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_CLAUDFUEN_PHOTOREALISTIC_FUEN_V1_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_CLAUDFUEN_PHOTOREALISTIC_FUEN_V1_2_0_0")
    def HUGGINGFACE_TXT2_IMG_CLAUDFUEN_PHOTOREALISTIC_FUEN_V1_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_CLAUDFUEN_PHOTOREALISTIC_FUEN_V1_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_CODER119_VECTORARTZ_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_CODER119_VECTORARTZ_DIFFUSION_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_CODER119_VECTORARTZ_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_CODER119_VECTORARTZ_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_CODER119_VECTORARTZ_DIFFUSION_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_CODER119_VECTORARTZ_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_CODER119_VECTORARTZ_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_CODER119_VECTORARTZ_DIFFUSION_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_CODER119_VECTORARTZ_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_CONFLICTX_COMPLEX_LINEART_1_0_0")
    def HUGGINGFACE_TXT2_IMG_CONFLICTX_COMPLEX_LINEART_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_CONFLICTX_COMPLEX_LINEART_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_CONFLICTX_COMPLEX_LINEART_1_1_0")
    def HUGGINGFACE_TXT2_IMG_CONFLICTX_COMPLEX_LINEART_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_CONFLICTX_COMPLEX_LINEART_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_CONFLICTX_COMPLEX_LINEART_2_0_0")
    def HUGGINGFACE_TXT2_IMG_CONFLICTX_COMPLEX_LINEART_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_CONFLICTX_COMPLEX_LINEART_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DALLINMACKAY_CATS_MUSICAL_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_DALLINMACKAY_CATS_MUSICAL_DIFFUSION_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DALLINMACKAY_CATS_MUSICAL_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DALLINMACKAY_CATS_MUSICAL_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_DALLINMACKAY_CATS_MUSICAL_DIFFUSION_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DALLINMACKAY_CATS_MUSICAL_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DALLINMACKAY_CATS_MUSICAL_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_DALLINMACKAY_CATS_MUSICAL_DIFFUSION_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DALLINMACKAY_CATS_MUSICAL_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DALLINMACKAY_JWST_DEEP_SPACE_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_DALLINMACKAY_JWST_DEEP_SPACE_DIFFUSION_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DALLINMACKAY_JWST_DEEP_SPACE_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DALLINMACKAY_JWST_DEEP_SPACE_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_DALLINMACKAY_JWST_DEEP_SPACE_DIFFUSION_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DALLINMACKAY_JWST_DEEP_SPACE_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DALLINMACKAY_JWST_DEEP_SPACE_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_DALLINMACKAY_JWST_DEEP_SPACE_DIFFUSION_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DALLINMACKAY_JWST_DEEP_SPACE_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DALLINMACKAY_TRON_LEGACY_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_DALLINMACKAY_TRON_LEGACY_DIFFUSION_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DALLINMACKAY_TRON_LEGACY_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DALLINMACKAY_TRON_LEGACY_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_DALLINMACKAY_TRON_LEGACY_DIFFUSION_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DALLINMACKAY_TRON_LEGACY_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DALLINMACKAY_TRON_LEGACY_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_DALLINMACKAY_TRON_LEGACY_DIFFUSION_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DALLINMACKAY_TRON_LEGACY_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DALLINMACKAY_VAN_GOGH_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_DALLINMACKAY_VAN_GOGH_DIFFUSION_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DALLINMACKAY_VAN_GOGH_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DALLINMACKAY_VAN_GOGH_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_DALLINMACKAY_VAN_GOGH_DIFFUSION_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DALLINMACKAY_VAN_GOGH_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DALLINMACKAY_VAN_GOGH_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_DALLINMACKAY_VAN_GOGH_DIFFUSION_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DALLINMACKAY_VAN_GOGH_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DGSPITZER_CYBERPUNK_ANIME_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_DGSPITZER_CYBERPUNK_ANIME_DIFFUSION_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DGSPITZER_CYBERPUNK_ANIME_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DGSPITZER_CYBERPUNK_ANIME_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_DGSPITZER_CYBERPUNK_ANIME_DIFFUSION_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DGSPITZER_CYBERPUNK_ANIME_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DGSPITZER_CYBERPUNK_ANIME_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_DGSPITZER_CYBERPUNK_ANIME_DIFFUSION_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DGSPITZER_CYBERPUNK_ANIME_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DREAMLIKE_ART_DREAMLIKE_DIFFUSION_1_0_1_0_0")
    def HUGGINGFACE_TXT2_IMG_DREAMLIKE_ART_DREAMLIKE_DIFFUSION_1_0_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DREAMLIKE_ART_DREAMLIKE_DIFFUSION_1_0_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DREAMLIKE_ART_DREAMLIKE_DIFFUSION_1_0_1_1_0")
    def HUGGINGFACE_TXT2_IMG_DREAMLIKE_ART_DREAMLIKE_DIFFUSION_1_0_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DREAMLIKE_ART_DREAMLIKE_DIFFUSION_1_0_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_DREAMLIKE_ART_DREAMLIKE_DIFFUSION_1_0_2_0_0")
    def HUGGINGFACE_TXT2_IMG_DREAMLIKE_ART_DREAMLIKE_DIFFUSION_1_0_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_DREAMLIKE_ART_DREAMLIKE_DIFFUSION_1_0_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_EIMISS_EIMISANIMEDIFFUSION_1_0V_1_0_0")
    def HUGGINGFACE_TXT2_IMG_EIMISS_EIMISANIMEDIFFUSION_1_0_V_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_EIMISS_EIMISANIMEDIFFUSION_1_0V_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_EIMISS_EIMISANIMEDIFFUSION_1_0V_1_1_0")
    def HUGGINGFACE_TXT2_IMG_EIMISS_EIMISANIMEDIFFUSION_1_0_V_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_EIMISS_EIMISANIMEDIFFUSION_1_0V_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_EIMISS_EIMISANIMEDIFFUSION_1_0V_2_0_0")
    def HUGGINGFACE_TXT2_IMG_EIMISS_EIMISANIMEDIFFUSION_1_0_V_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_EIMISS_EIMISANIMEDIFFUSION_1_0V_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_ENVVI_INKPUNK_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_ENVVI_INKPUNK_DIFFUSION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_ENVVI_INKPUNK_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_ENVVI_INKPUNK_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_ENVVI_INKPUNK_DIFFUSION_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_ENVVI_INKPUNK_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_ENVVI_INKPUNK_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_ENVVI_INKPUNK_DIFFUSION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_ENVVI_INKPUNK_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_EVEL_YOSHIN_1_0_0")
    def HUGGINGFACE_TXT2_IMG_EVEL_YOSHIN_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_EVEL_YOSHIN_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_EVEL_YOSHIN_1_1_0")
    def HUGGINGFACE_TXT2_IMG_EVEL_YOSHIN_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_EVEL_YOSHIN_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_EVEL_YOSHIN_2_0_0")
    def HUGGINGFACE_TXT2_IMG_EVEL_YOSHIN_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_EVEL_YOSHIN_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_EXTRAPHY_MUSTAFA_KEMAL_ATATURK_1_0_0")
    def HUGGINGFACE_TXT2_IMG_EXTRAPHY_MUSTAFA_KEMAL_ATATURK_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_EXTRAPHY_MUSTAFA_KEMAL_ATATURK_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_EXTRAPHY_MUSTAFA_KEMAL_ATATURK_1_1_0")
    def HUGGINGFACE_TXT2_IMG_EXTRAPHY_MUSTAFA_KEMAL_ATATURK_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_EXTRAPHY_MUSTAFA_KEMAL_ATATURK_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_EXTRAPHY_MUSTAFA_KEMAL_ATATURK_2_0_0")
    def HUGGINGFACE_TXT2_IMG_EXTRAPHY_MUSTAFA_KEMAL_ATATURK_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_EXTRAPHY_MUSTAFA_KEMAL_ATATURK_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FFFILONI_MR_MEN_AND_LITTLE_MISSES_1_0_0")
    def HUGGINGFACE_TXT2_IMG_FFFILONI_MR_MEN_AND_LITTLE_MISSES_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FFFILONI_MR_MEN_AND_LITTLE_MISSES_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FFFILONI_MR_MEN_AND_LITTLE_MISSES_1_1_0")
    def HUGGINGFACE_TXT2_IMG_FFFILONI_MR_MEN_AND_LITTLE_MISSES_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FFFILONI_MR_MEN_AND_LITTLE_MISSES_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FFFILONI_MR_MEN_AND_LITTLE_MISSES_2_0_0")
    def HUGGINGFACE_TXT2_IMG_FFFILONI_MR_MEN_AND_LITTLE_MISSES_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FFFILONI_MR_MEN_AND_LITTLE_MISSES_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FICTIVERSE_ELRISITAS_1_0_0")
    def HUGGINGFACE_TXT2_IMG_FICTIVERSE_ELRISITAS_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FICTIVERSE_ELRISITAS_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FICTIVERSE_ELRISITAS_1_1_0")
    def HUGGINGFACE_TXT2_IMG_FICTIVERSE_ELRISITAS_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FICTIVERSE_ELRISITAS_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FICTIVERSE_ELRISITAS_2_0_0")
    def HUGGINGFACE_TXT2_IMG_FICTIVERSE_ELRISITAS_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FICTIVERSE_ELRISITAS_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_BALLOONART_MODEL_1_0_0")
    def HUGGINGFACE_TXT2_IMG_FICTIVERSE_STABLE_DIFFUSION_BALLOONART_MODEL_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_BALLOONART_MODEL_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_BALLOONART_MODEL_1_1_0")
    def HUGGINGFACE_TXT2_IMG_FICTIVERSE_STABLE_DIFFUSION_BALLOONART_MODEL_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_BALLOONART_MODEL_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_BALLOONART_MODEL_2_0_0")
    def HUGGINGFACE_TXT2_IMG_FICTIVERSE_STABLE_DIFFUSION_BALLOONART_MODEL_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_BALLOONART_MODEL_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_MICROSCOPIC_MODEL_1_0_0")
    def HUGGINGFACE_TXT2_IMG_FICTIVERSE_STABLE_DIFFUSION_MICROSCOPIC_MODEL_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_MICROSCOPIC_MODEL_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_MICROSCOPIC_MODEL_1_1_0")
    def HUGGINGFACE_TXT2_IMG_FICTIVERSE_STABLE_DIFFUSION_MICROSCOPIC_MODEL_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_MICROSCOPIC_MODEL_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_MICROSCOPIC_MODEL_2_0_0")
    def HUGGINGFACE_TXT2_IMG_FICTIVERSE_STABLE_DIFFUSION_MICROSCOPIC_MODEL_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_MICROSCOPIC_MODEL_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_PAPERCUT_MODEL_1_0_0")
    def HUGGINGFACE_TXT2_IMG_FICTIVERSE_STABLE_DIFFUSION_PAPERCUT_MODEL_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_PAPERCUT_MODEL_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_PAPERCUT_MODEL_1_1_0")
    def HUGGINGFACE_TXT2_IMG_FICTIVERSE_STABLE_DIFFUSION_PAPERCUT_MODEL_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_PAPERCUT_MODEL_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_PAPERCUT_MODEL_2_0_0")
    def HUGGINGFACE_TXT2_IMG_FICTIVERSE_STABLE_DIFFUSION_PAPERCUT_MODEL_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_PAPERCUT_MODEL_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_VOXELART_MODEL_1_0_0")
    def HUGGINGFACE_TXT2_IMG_FICTIVERSE_STABLE_DIFFUSION_VOXELART_MODEL_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_VOXELART_MODEL_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_VOXELART_MODEL_1_1_0")
    def HUGGINGFACE_TXT2_IMG_FICTIVERSE_STABLE_DIFFUSION_VOXELART_MODEL_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_VOXELART_MODEL_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_VOXELART_MODEL_2_0_0")
    def HUGGINGFACE_TXT2_IMG_FICTIVERSE_STABLE_DIFFUSION_VOXELART_MODEL_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_FICTIVERSE_STABLE_DIFFUSION_VOXELART_MODEL_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_HAOR_EVT_V3_1_0_0")
    def HUGGINGFACE_TXT2_IMG_HAOR_EVT_V3_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_HAOR_EVT_V3_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_HAOR_EVT_V3_1_1_0")
    def HUGGINGFACE_TXT2_IMG_HAOR_EVT_V3_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_HAOR_EVT_V3_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_HAOR_EVT_V3_2_0_0")
    def HUGGINGFACE_TXT2_IMG_HAOR_EVT_V3_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_HAOR_EVT_V3_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_HASSANBLEND_HASSANBLEND1_4_1_0_0")
    def HUGGINGFACE_TXT2_IMG_HASSANBLEND_HASSANBLEND1_4_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_HASSANBLEND_HASSANBLEND1_4_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_HASSANBLEND_HASSANBLEND1_4_1_1_0")
    def HUGGINGFACE_TXT2_IMG_HASSANBLEND_HASSANBLEND1_4_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_HASSANBLEND_HASSANBLEND1_4_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_HASSANBLEND_HASSANBLEND1_4_2_0_0")
    def HUGGINGFACE_TXT2_IMG_HASSANBLEND_HASSANBLEND1_4_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_HASSANBLEND_HASSANBLEND1_4_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1B_CHINESE_EN_V0_1_1_0_0")
    def HUGGINGFACE_TXT2_IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1_B_CHINESE_EN_V0_1_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1B_CHINESE_EN_V0_1_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1B_CHINESE_EN_V0_1_1_1_0")
    def HUGGINGFACE_TXT2_IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1_B_CHINESE_EN_V0_1_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1B_CHINESE_EN_V0_1_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1B_CHINESE_EN_V0_1_2_0_0")
    def HUGGINGFACE_TXT2_IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1_B_CHINESE_EN_V0_1_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1B_CHINESE_EN_V0_1_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1B_CHINESE_V0_1_1_0_0")
    def HUGGINGFACE_TXT2_IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1_B_CHINESE_V0_1_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1B_CHINESE_V0_1_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1B_CHINESE_V0_1_1_1_0")
    def HUGGINGFACE_TXT2_IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1_B_CHINESE_V0_1_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1B_CHINESE_V0_1_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1B_CHINESE_V0_1_2_0_0")
    def HUGGINGFACE_TXT2_IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1_B_CHINESE_V0_1_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_IDEA_CCNL_TAIYI_STABLE_DIFFUSION_1B_CHINESE_V0_1_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_IFANSNEK_JOHNDIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_IFANSNEK_JOHNDIFFUSION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_IFANSNEK_JOHNDIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_IFANSNEK_JOHNDIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_IFANSNEK_JOHNDIFFUSION_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_IFANSNEK_JOHNDIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_IFANSNEK_JOHNDIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_IFANSNEK_JOHNDIFFUSION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_IFANSNEK_JOHNDIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_JERSONM89_AVATAR_1_0_0")
    def HUGGINGFACE_TXT2_IMG_JERSONM89_AVATAR_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_JERSONM89_AVATAR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_JERSONM89_AVATAR_1_1_0")
    def HUGGINGFACE_TXT2_IMG_JERSONM89_AVATAR_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_JERSONM89_AVATAR_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_JERSONM89_AVATAR_2_0_0")
    def HUGGINGFACE_TXT2_IMG_JERSONM89_AVATAR_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_JERSONM89_AVATAR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_JVKAPE_ICONSMI_APPICONSMODELFORSD_1_0_0")
    def HUGGINGFACE_TXT2_IMG_JVKAPE_ICONSMI_APPICONSMODELFORSD_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_JVKAPE_ICONSMI_APPICONSMODELFORSD_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_JVKAPE_ICONSMI_APPICONSMODELFORSD_1_1_0")
    def HUGGINGFACE_TXT2_IMG_JVKAPE_ICONSMI_APPICONSMODELFORSD_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_JVKAPE_ICONSMI_APPICONSMODELFORSD_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_JVKAPE_ICONSMI_APPICONSMODELFORSD_2_0_0")
    def HUGGINGFACE_TXT2_IMG_JVKAPE_ICONSMI_APPICONSMODELFORSD_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_JVKAPE_ICONSMI_APPICONSMODELFORSD_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_KATAKANA_2D_MIX_1_0_0")
    def HUGGINGFACE_TXT2_IMG_KATAKANA_2_D_MIX_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_KATAKANA_2D_MIX_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_KATAKANA_2D_MIX_1_1_0")
    def HUGGINGFACE_TXT2_IMG_KATAKANA_2_D_MIX_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_KATAKANA_2D_MIX_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_KATAKANA_2D_MIX_2_0_0")
    def HUGGINGFACE_TXT2_IMG_KATAKANA_2_D_MIX_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_KATAKANA_2D_MIX_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_LACAMBRE_VULVINE_LOOK_V02_1_0_0")
    def HUGGINGFACE_TXT2_IMG_LACAMBRE_VULVINE_LOOK_V02_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_LACAMBRE_VULVINE_LOOK_V02_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_LACAMBRE_VULVINE_LOOK_V02_1_1_0")
    def HUGGINGFACE_TXT2_IMG_LACAMBRE_VULVINE_LOOK_V02_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_LACAMBRE_VULVINE_LOOK_V02_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_LACAMBRE_VULVINE_LOOK_V02_2_0_0")
    def HUGGINGFACE_TXT2_IMG_LACAMBRE_VULVINE_LOOK_V02_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_LACAMBRE_VULVINE_LOOK_V02_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_LANGBOAT_GUOHUA_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_LANGBOAT_GUOHUA_DIFFUSION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_LANGBOAT_GUOHUA_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_LANGBOAT_GUOHUA_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_LANGBOAT_GUOHUA_DIFFUSION_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_LANGBOAT_GUOHUA_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_LANGBOAT_GUOHUA_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_LANGBOAT_GUOHUA_DIFFUSION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_LANGBOAT_GUOHUA_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_LINAQRUF_ANYTHING_V3_0_1_0_0")
    def HUGGINGFACE_TXT2_IMG_LINAQRUF_ANYTHING_V3_0_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_LINAQRUF_ANYTHING_V3_0_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_LINAQRUF_ANYTHING_V3_0_1_1_0")
    def HUGGINGFACE_TXT2_IMG_LINAQRUF_ANYTHING_V3_0_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_LINAQRUF_ANYTHING_V3_0_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_LINAQRUF_ANYTHING_V3_0_2_0_0")
    def HUGGINGFACE_TXT2_IMG_LINAQRUF_ANYTHING_V3_0_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_LINAQRUF_ANYTHING_V3_0_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_MIKESMODELS_WALTZ_WITH_BASHIR_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_MIKESMODELS_WALTZ_WITH_BASHIR_DIFFUSION_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_MIKESMODELS_WALTZ_WITH_BASHIR_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_MIKESMODELS_WALTZ_WITH_BASHIR_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_MIKESMODELS_WALTZ_WITH_BASHIR_DIFFUSION_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_MIKESMODELS_WALTZ_WITH_BASHIR_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_MIKESMODELS_WALTZ_WITH_BASHIR_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_MIKESMODELS_WALTZ_WITH_BASHIR_DIFFUSION_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_MIKESMODELS_WALTZ_WITH_BASHIR_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_MITCHTECH_KLINGON_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_MITCHTECH_KLINGON_DIFFUSION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_MITCHTECH_KLINGON_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_MITCHTECH_KLINGON_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_MITCHTECH_KLINGON_DIFFUSION_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_MITCHTECH_KLINGON_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_MITCHTECH_KLINGON_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_MITCHTECH_KLINGON_DIFFUSION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_MITCHTECH_KLINGON_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_MITCHTECH_VULCAN_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_MITCHTECH_VULCAN_DIFFUSION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_MITCHTECH_VULCAN_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_MITCHTECH_VULCAN_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_MITCHTECH_VULCAN_DIFFUSION_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_MITCHTECH_VULCAN_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_MITCHTECH_VULCAN_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_MITCHTECH_VULCAN_DIFFUSION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_MITCHTECH_VULCAN_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_MITSUA_MITSUA_DIFFUSION_CC0_1_0_0")
    def HUGGINGFACE_TXT2_IMG_MITSUA_MITSUA_DIFFUSION_CC0_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_MITSUA_MITSUA_DIFFUSION_CC0_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_MITSUA_MITSUA_DIFFUSION_CC0_1_1_0")
    def HUGGINGFACE_TXT2_IMG_MITSUA_MITSUA_DIFFUSION_CC0_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_MITSUA_MITSUA_DIFFUSION_CC0_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_MITSUA_MITSUA_DIFFUSION_CC0_2_0_0")
    def HUGGINGFACE_TXT2_IMG_MITSUA_MITSUA_DIFFUSION_CC0_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_MITSUA_MITSUA_DIFFUSION_CC0_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NACLBIT_TRINART_STABLE_DIFFUSION_V2_1_0_0")
    def HUGGINGFACE_TXT2_IMG_NACLBIT_TRINART_STABLE_DIFFUSION_V2_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NACLBIT_TRINART_STABLE_DIFFUSION_V2_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NACLBIT_TRINART_STABLE_DIFFUSION_V2_1_1_0")
    def HUGGINGFACE_TXT2_IMG_NACLBIT_TRINART_STABLE_DIFFUSION_V2_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NACLBIT_TRINART_STABLE_DIFFUSION_V2_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NACLBIT_TRINART_STABLE_DIFFUSION_V2_2_0_0")
    def HUGGINGFACE_TXT2_IMG_NACLBIT_TRINART_STABLE_DIFFUSION_V2_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NACLBIT_TRINART_STABLE_DIFFUSION_V2_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_ARCANE_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_ARCANE_DIFFUSION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_ARCANE_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_ARCANE_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_ARCANE_DIFFUSION_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_ARCANE_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_ARCANE_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_ARCANE_DIFFUSION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_ARCANE_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_ARCHER_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_ARCHER_DIFFUSION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_ARCHER_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_ARCHER_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_ARCHER_DIFFUSION_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_ARCHER_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_ARCHER_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_ARCHER_DIFFUSION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_ARCHER_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_CLASSIC_ANIM_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_CLASSIC_ANIM_DIFFUSION_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_CLASSIC_ANIM_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_CLASSIC_ANIM_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_CLASSIC_ANIM_DIFFUSION_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_CLASSIC_ANIM_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_CLASSIC_ANIM_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_CLASSIC_ANIM_DIFFUSION_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_CLASSIC_ANIM_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_ELDEN_RING_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_ELDEN_RING_DIFFUSION_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_ELDEN_RING_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_ELDEN_RING_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_ELDEN_RING_DIFFUSION_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_ELDEN_RING_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_ELDEN_RING_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_ELDEN_RING_DIFFUSION_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_ELDEN_RING_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_FUTURE_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_FUTURE_DIFFUSION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_FUTURE_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_FUTURE_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_FUTURE_DIFFUSION_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_FUTURE_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_FUTURE_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_FUTURE_DIFFUSION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_FUTURE_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_GHIBLI_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_GHIBLI_DIFFUSION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_GHIBLI_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_GHIBLI_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_GHIBLI_DIFFUSION_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_GHIBLI_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_GHIBLI_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_GHIBLI_DIFFUSION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_GHIBLI_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_MO_DI_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_MO_DI_DIFFUSION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_MO_DI_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_MO_DI_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_MO_DI_DIFFUSION_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_MO_DI_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_MO_DI_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_MO_DI_DIFFUSION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_MO_DI_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_NITRO_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_NITRO_DIFFUSION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_NITRO_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_NITRO_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_NITRO_DIFFUSION_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_NITRO_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_NITRO_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_NITRO_DIFFUSION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_NITRO_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_REDSHIFT_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_REDSHIFT_DIFFUSION_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_REDSHIFT_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_REDSHIFT_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_REDSHIFT_DIFFUSION_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_REDSHIFT_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_REDSHIFT_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_REDSHIFT_DIFFUSION_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_REDSHIFT_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_SPIDER_VERSE_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_SPIDER_VERSE_DIFFUSION_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_SPIDER_VERSE_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_SPIDER_VERSE_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_SPIDER_VERSE_DIFFUSION_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_SPIDER_VERSE_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NITROSOCKE_SPIDER_VERSE_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_NITROSOCKE_SPIDER_VERSE_DIFFUSION_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NITROSOCKE_SPIDER_VERSE_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NOUSR_ROBO_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_NOUSR_ROBO_DIFFUSION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NOUSR_ROBO_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NOUSR_ROBO_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_NOUSR_ROBO_DIFFUSION_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NOUSR_ROBO_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_NOUSR_ROBO_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_NOUSR_ROBO_DIFFUSION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_NOUSR_ROBO_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_OGKALU_COMIC_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_OGKALU_COMIC_DIFFUSION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_OGKALU_COMIC_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_OGKALU_COMIC_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_OGKALU_COMIC_DIFFUSION_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_OGKALU_COMIC_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_OGKALU_COMIC_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_OGKALU_COMIC_DIFFUSION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_OGKALU_COMIC_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_OPENJOURNEY_OPENJOURNEY_1_0_0")
    def HUGGINGFACE_TXT2_IMG_OPENJOURNEY_OPENJOURNEY_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_OPENJOURNEY_OPENJOURNEY_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_OPENJOURNEY_OPENJOURNEY_1_1_0")
    def HUGGINGFACE_TXT2_IMG_OPENJOURNEY_OPENJOURNEY_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_OPENJOURNEY_OPENJOURNEY_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_OPENJOURNEY_OPENJOURNEY_2_0_0")
    def HUGGINGFACE_TXT2_IMG_OPENJOURNEY_OPENJOURNEY_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_OPENJOURNEY_OPENJOURNEY_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PIESPOSITO_OPENPOTIONBOTTLE_V2_1_0_0")
    def HUGGINGFACE_TXT2_IMG_PIESPOSITO_OPENPOTIONBOTTLE_V2_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PIESPOSITO_OPENPOTIONBOTTLE_V2_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PIESPOSITO_OPENPOTIONBOTTLE_V2_1_1_0")
    def HUGGINGFACE_TXT2_IMG_PIESPOSITO_OPENPOTIONBOTTLE_V2_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PIESPOSITO_OPENPOTIONBOTTLE_V2_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PIESPOSITO_OPENPOTIONBOTTLE_V2_2_0_0")
    def HUGGINGFACE_TXT2_IMG_PIESPOSITO_OPENPOTIONBOTTLE_V2_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PIESPOSITO_OPENPOTIONBOTTLE_V2_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PLASMO_VOXEL_ISH_1_0_0")
    def HUGGINGFACE_TXT2_IMG_PLASMO_VOXEL_ISH_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PLASMO_VOXEL_ISH_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PLASMO_VOXEL_ISH_1_1_0")
    def HUGGINGFACE_TXT2_IMG_PLASMO_VOXEL_ISH_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PLASMO_VOXEL_ISH_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PLASMO_VOXEL_ISH_2_0_0")
    def HUGGINGFACE_TXT2_IMG_PLASMO_VOXEL_ISH_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PLASMO_VOXEL_ISH_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PLASMO_WOOLITIZE_1_0_0")
    def HUGGINGFACE_TXT2_IMG_PLASMO_WOOLITIZE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PLASMO_WOOLITIZE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PLASMO_WOOLITIZE_1_1_0")
    def HUGGINGFACE_TXT2_IMG_PLASMO_WOOLITIZE_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PLASMO_WOOLITIZE_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PLASMO_WOOLITIZE_2_0_0")
    def HUGGINGFACE_TXT2_IMG_PLASMO_WOOLITIZE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PLASMO_WOOLITIZE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PROGAMERGOV_MIN_ILLUST_BACKGROUND_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_PROGAMERGOV_MIN_ILLUST_BACKGROUND_DIFFUSION_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PROGAMERGOV_MIN_ILLUST_BACKGROUND_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PROGAMERGOV_MIN_ILLUST_BACKGROUND_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_PROGAMERGOV_MIN_ILLUST_BACKGROUND_DIFFUSION_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PROGAMERGOV_MIN_ILLUST_BACKGROUND_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PROGAMERGOV_MIN_ILLUST_BACKGROUND_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_PROGAMERGOV_MIN_ILLUST_BACKGROUND_DIFFUSION_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PROGAMERGOV_MIN_ILLUST_BACKGROUND_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PROMPTHERO_LINKEDIN_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_PROMPTHERO_LINKEDIN_DIFFUSION_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PROMPTHERO_LINKEDIN_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PROMPTHERO_LINKEDIN_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_PROMPTHERO_LINKEDIN_DIFFUSION_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PROMPTHERO_LINKEDIN_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PROMPTHERO_LINKEDIN_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_PROMPTHERO_LINKEDIN_DIFFUSION_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PROMPTHERO_LINKEDIN_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PROMPTHERO_OPENJOURNEY_1_0_0")
    def HUGGINGFACE_TXT2_IMG_PROMPTHERO_OPENJOURNEY_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PROMPTHERO_OPENJOURNEY_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PROMPTHERO_OPENJOURNEY_1_1_0")
    def HUGGINGFACE_TXT2_IMG_PROMPTHERO_OPENJOURNEY_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PROMPTHERO_OPENJOURNEY_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_PROMPTHERO_OPENJOURNEY_2_0_0")
    def HUGGINGFACE_TXT2_IMG_PROMPTHERO_OPENJOURNEY_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_PROMPTHERO_OPENJOURNEY_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_QILEX_MAGIC_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_QILEX_MAGIC_DIFFUSION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_QILEX_MAGIC_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_QILEX_MAGIC_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_QILEX_MAGIC_DIFFUSION_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_QILEX_MAGIC_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_QILEX_MAGIC_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_QILEX_MAGIC_DIFFUSION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_QILEX_MAGIC_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_RABIDGREMLIN_SD_DB_EPIC_SPACE_MACHINE_1_0_0")
    def HUGGINGFACE_TXT2_IMG_RABIDGREMLIN_SD_DB_EPIC_SPACE_MACHINE_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_RABIDGREMLIN_SD_DB_EPIC_SPACE_MACHINE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_RABIDGREMLIN_SD_DB_EPIC_SPACE_MACHINE_1_1_0")
    def HUGGINGFACE_TXT2_IMG_RABIDGREMLIN_SD_DB_EPIC_SPACE_MACHINE_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_RABIDGREMLIN_SD_DB_EPIC_SPACE_MACHINE_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_RABIDGREMLIN_SD_DB_EPIC_SPACE_MACHINE_2_0_0")
    def HUGGINGFACE_TXT2_IMG_RABIDGREMLIN_SD_DB_EPIC_SPACE_MACHINE_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_RABIDGREMLIN_SD_DB_EPIC_SPACE_MACHINE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_RAYHELL_POPUPBOOK_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_RAYHELL_POPUPBOOK_DIFFUSION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_RAYHELL_POPUPBOOK_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_RAYHELL_POPUPBOOK_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_RAYHELL_POPUPBOOK_DIFFUSION_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_RAYHELL_POPUPBOOK_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_RAYHELL_POPUPBOOK_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_RAYHELL_POPUPBOOK_DIFFUSION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_RAYHELL_POPUPBOOK_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_RUNWAYML_STABLE_DIFFUSION_V1_5_1_0_0")
    def HUGGINGFACE_TXT2_IMG_RUNWAYML_STABLE_DIFFUSION_V1_5_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_RUNWAYML_STABLE_DIFFUSION_V1_5_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_RUNWAYML_STABLE_DIFFUSION_V1_5_1_1_0")
    def HUGGINGFACE_TXT2_IMG_RUNWAYML_STABLE_DIFFUSION_V1_5_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_RUNWAYML_STABLE_DIFFUSION_V1_5_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_RUNWAYML_STABLE_DIFFUSION_V1_5_2_0_0")
    def HUGGINGFACE_TXT2_IMG_RUNWAYML_STABLE_DIFFUSION_V1_5_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_RUNWAYML_STABLE_DIFFUSION_V1_5_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_S3NH_BEKSINSKI_STYLE_STABLE_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_S3_NH_BEKSINSKI_STYLE_STABLE_DIFFUSION_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_S3NH_BEKSINSKI_STYLE_STABLE_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_S3NH_BEKSINSKI_STYLE_STABLE_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_S3_NH_BEKSINSKI_STYLE_STABLE_DIFFUSION_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_S3NH_BEKSINSKI_STYLE_STABLE_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_S3NH_BEKSINSKI_STYLE_STABLE_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_S3_NH_BEKSINSKI_STYLE_STABLE_DIFFUSION_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_S3NH_BEKSINSKI_STYLE_STABLE_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_ORIGINAL_CHARACTER_CYCLPS_1_0_0")
    def HUGGINGFACE_TXT2_IMG_SD_DREAMBOOTH_LIBRARY_ORIGINAL_CHARACTER_CYCLPS_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_ORIGINAL_CHARACTER_CYCLPS_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_ORIGINAL_CHARACTER_CYCLPS_1_1_0")
    def HUGGINGFACE_TXT2_IMG_SD_DREAMBOOTH_LIBRARY_ORIGINAL_CHARACTER_CYCLPS_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_ORIGINAL_CHARACTER_CYCLPS_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_ORIGINAL_CHARACTER_CYCLPS_2_0_0")
    def HUGGINGFACE_TXT2_IMG_SD_DREAMBOOTH_LIBRARY_ORIGINAL_CHARACTER_CYCLPS_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_ORIGINAL_CHARACTER_CYCLPS_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_PERSONA_5_SHIGENORI_STYLE_1_0_0")
    def HUGGINGFACE_TXT2_IMG_SD_DREAMBOOTH_LIBRARY_PERSONA_5_SHIGENORI_STYLE_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_PERSONA_5_SHIGENORI_STYLE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_PERSONA_5_SHIGENORI_STYLE_1_1_0")
    def HUGGINGFACE_TXT2_IMG_SD_DREAMBOOTH_LIBRARY_PERSONA_5_SHIGENORI_STYLE_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_PERSONA_5_SHIGENORI_STYLE_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_PERSONA_5_SHIGENORI_STYLE_2_0_0")
    def HUGGINGFACE_TXT2_IMG_SD_DREAMBOOTH_LIBRARY_PERSONA_5_SHIGENORI_STYLE_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_PERSONA_5_SHIGENORI_STYLE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_SERAPHM_1_0_0")
    def HUGGINGFACE_TXT2_IMG_SD_DREAMBOOTH_LIBRARY_SERAPHM_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_SERAPHM_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_SERAPHM_1_1_0")
    def HUGGINGFACE_TXT2_IMG_SD_DREAMBOOTH_LIBRARY_SERAPHM_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_SERAPHM_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_SERAPHM_2_0_0")
    def HUGGINGFACE_TXT2_IMG_SD_DREAMBOOTH_LIBRARY_SERAPHM_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_SD_DREAMBOOTH_LIBRARY_SERAPHM_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_SHIRAYU_SD_TOHOKU_V1_1_0_0")
    def HUGGINGFACE_TXT2_IMG_SHIRAYU_SD_TOHOKU_V1_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_SHIRAYU_SD_TOHOKU_V1_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_SHIRAYU_SD_TOHOKU_V1_1_1_0")
    def HUGGINGFACE_TXT2_IMG_SHIRAYU_SD_TOHOKU_V1_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_SHIRAYU_SD_TOHOKU_V1_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_SHIRAYU_SD_TOHOKU_V1_2_0_0")
    def HUGGINGFACE_TXT2_IMG_SHIRAYU_SD_TOHOKU_V1_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_SHIRAYU_SD_TOHOKU_V1_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_THELASTBEN_HRRZG_STYLE_768PX_1_0_0")
    def HUGGINGFACE_TXT2_IMG_THELASTBEN_HRRZG_STYLE_768_PX_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_THELASTBEN_HRRZG_STYLE_768PX_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_THELASTBEN_HRRZG_STYLE_768PX_1_1_0")
    def HUGGINGFACE_TXT2_IMG_THELASTBEN_HRRZG_STYLE_768_PX_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_THELASTBEN_HRRZG_STYLE_768PX_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_THELASTBEN_HRRZG_STYLE_768PX_2_0_0")
    def HUGGINGFACE_TXT2_IMG_THELASTBEN_HRRZG_STYLE_768_PX_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_THELASTBEN_HRRZG_STYLE_768PX_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_TIMOTHEPEARCE_GINA_THE_CAT_1_0_0")
    def HUGGINGFACE_TXT2_IMG_TIMOTHEPEARCE_GINA_THE_CAT_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_TIMOTHEPEARCE_GINA_THE_CAT_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_TIMOTHEPEARCE_GINA_THE_CAT_1_1_0")
    def HUGGINGFACE_TXT2_IMG_TIMOTHEPEARCE_GINA_THE_CAT_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_TIMOTHEPEARCE_GINA_THE_CAT_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_TIMOTHEPEARCE_GINA_THE_CAT_2_0_0")
    def HUGGINGFACE_TXT2_IMG_TIMOTHEPEARCE_GINA_THE_CAT_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_TIMOTHEPEARCE_GINA_THE_CAT_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_TRYSTAR_CLONEDIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_TRYSTAR_CLONEDIFFUSION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_TRYSTAR_CLONEDIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_TRYSTAR_CLONEDIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_TRYSTAR_CLONEDIFFUSION_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_TRYSTAR_CLONEDIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_TRYSTAR_CLONEDIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_TRYSTAR_CLONEDIFFUSION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_TRYSTAR_CLONEDIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_TUWONGA_DBLUTH_1_0_0")
    def HUGGINGFACE_TXT2_IMG_TUWONGA_DBLUTH_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_TUWONGA_DBLUTH_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_TUWONGA_DBLUTH_1_1_0")
    def HUGGINGFACE_TXT2_IMG_TUWONGA_DBLUTH_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_TUWONGA_DBLUTH_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_TUWONGA_DBLUTH_2_0_0")
    def HUGGINGFACE_TXT2_IMG_TUWONGA_DBLUTH_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_TUWONGA_DBLUTH_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_TUWONGA_ROTOSCOPEE_1_0_0")
    def HUGGINGFACE_TXT2_IMG_TUWONGA_ROTOSCOPEE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_TUWONGA_ROTOSCOPEE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_TUWONGA_ROTOSCOPEE_1_1_0")
    def HUGGINGFACE_TXT2_IMG_TUWONGA_ROTOSCOPEE_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_TUWONGA_ROTOSCOPEE_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_TUWONGA_ROTOSCOPEE_2_0_0")
    def HUGGINGFACE_TXT2_IMG_TUWONGA_ROTOSCOPEE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_TUWONGA_ROTOSCOPEE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_VOLRATH50_FANTASY_CARD_DIFFUSION_1_0_0")
    def HUGGINGFACE_TXT2_IMG_VOLRATH50_FANTASY_CARD_DIFFUSION_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_VOLRATH50_FANTASY_CARD_DIFFUSION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_VOLRATH50_FANTASY_CARD_DIFFUSION_1_1_0")
    def HUGGINGFACE_TXT2_IMG_VOLRATH50_FANTASY_CARD_DIFFUSION_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_VOLRATH50_FANTASY_CARD_DIFFUSION_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_VOLRATH50_FANTASY_CARD_DIFFUSION_2_0_0")
    def HUGGINGFACE_TXT2_IMG_VOLRATH50_FANTASY_CARD_DIFFUSION_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_VOLRATH50_FANTASY_CARD_DIFFUSION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_YAYAB_SD_ONEPIECE_DIFFUSERS4_1_0_0")
    def HUGGINGFACE_TXT2_IMG_YAYAB_SD_ONEPIECE_DIFFUSERS4_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_YAYAB_SD_ONEPIECE_DIFFUSERS4_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_YAYAB_SD_ONEPIECE_DIFFUSERS4_1_1_0")
    def HUGGINGFACE_TXT2_IMG_YAYAB_SD_ONEPIECE_DIFFUSERS4_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_YAYAB_SD_ONEPIECE_DIFFUSERS4_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_TXT2IMG_YAYAB_SD_ONEPIECE_DIFFUSERS4_2_0_0")
    def HUGGINGFACE_TXT2_IMG_YAYAB_SD_ONEPIECE_DIFFUSERS4_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_TXT2IMG_YAYAB_SD_ONEPIECE_DIFFUSERS4_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_DEBERTA_BASE_1_0_0")
    def HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_DEBERTA_BASE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_DEBERTA_BASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_DEBERTA_BASE_2_0_0")
    def HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_DEBERTA_BASE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_DEBERTA_BASE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_DISTILROBERTA_BASE_1_0_0")
    def HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_DISTILROBERTA_BASE_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_DISTILROBERTA_BASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_DISTILROBERTA_BASE_2_0_0")
    def HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_DISTILROBERTA_BASE_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_DISTILROBERTA_BASE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_MINILM2_L6_H768_1_0_0")
    def HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_MINILM2_L6_H768_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_MINILM2_L6_H768_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_MINILM2_L6_H768_2_0_0")
    def HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_MINILM2_L6_H768_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_MINILM2_L6_H768_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_ROBERTA_BASE_1_0_0")
    def HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_ROBERTA_BASE_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_ROBERTA_BASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_ROBERTA_BASE_2_0_0")
    def HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_ROBERTA_BASE_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_CROSS_ENCODER_NLI_ROBERTA_BASE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_DIGITALEPIDEMIOLOGYLAB_COVID_TWITTER_BERT_V2_MNLI_1_0_0")
    def HUGGINGFACE_ZSTC_DIGITALEPIDEMIOLOGYLAB_COVID_TWITTER_BERT_V2_MNLI_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_DIGITALEPIDEMIOLOGYLAB_COVID_TWITTER_BERT_V2_MNLI_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_DIGITALEPIDEMIOLOGYLAB_COVID_TWITTER_BERT_V2_MNLI_2_0_0")
    def HUGGINGFACE_ZSTC_DIGITALEPIDEMIOLOGYLAB_COVID_TWITTER_BERT_V2_MNLI_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_DIGITALEPIDEMIOLOGYLAB_COVID_TWITTER_BERT_V2_MNLI_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_ELELDAR_THEME_CLASSIFICATION_1_0_0")
    def HUGGINGFACE_ZSTC_ELELDAR_THEME_CLASSIFICATION_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_ELELDAR_THEME_CLASSIFICATION_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_ELELDAR_THEME_CLASSIFICATION_2_0_0")
    def HUGGINGFACE_ZSTC_ELELDAR_THEME_CLASSIFICATION_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_ELELDAR_THEME_CLASSIFICATION_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_ALLNLI_TR_1_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_ALLNLI_TR_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_ALLNLI_TR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_ALLNLI_TR_2_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_ALLNLI_TR_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_ALLNLI_TR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_MULTINLI_TR_1_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_MULTINLI_TR_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_MULTINLI_TR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_MULTINLI_TR_2_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_MULTINLI_TR_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_MULTINLI_TR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_SNLI_TR_1_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_SNLI_TR_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_SNLI_TR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_SNLI_TR_2_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_SNLI_TR_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_MULTILINGUAL_CASED_SNLI_TR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_ALLNLI_TR_1_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_ALLNLI_TR_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_ALLNLI_TR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_ALLNLI_TR_2_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_ALLNLI_TR_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_ALLNLI_TR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_MULTINLI_TR_1_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_MULTINLI_TR_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_MULTINLI_TR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_MULTINLI_TR_2_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_MULTINLI_TR_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_MULTINLI_TR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_SNLI_TR_1_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_SNLI_TR_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_SNLI_TR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_SNLI_TR_2_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_SNLI_TR_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_BERT_BASE_TURKISH_CASED_SNLI_TR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_ALLNLI_TR_1_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_ALLNLI_TR_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_ALLNLI_TR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_ALLNLI_TR_2_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_ALLNLI_TR_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_ALLNLI_TR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_MULTINLI_TR_1_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_MULTINLI_TR_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_MULTINLI_TR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_MULTINLI_TR_2_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_MULTINLI_TR_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_MULTINLI_TR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_SNLI_TR_1_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_SNLI_TR_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_SNLI_TR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_SNLI_TR_2_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_SNLI_TR_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_CONVBERT_BASE_TURKISH_MC4_CASED_SNLI_TR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_ALLNLI_TR_1_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_ALLNLI_TR_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_ALLNLI_TR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_ALLNLI_TR_2_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_ALLNLI_TR_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_ALLNLI_TR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_MULTINLI_TR_1_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_MULTINLI_TR_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_MULTINLI_TR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_MULTINLI_TR_2_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_MULTINLI_TR_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_MULTINLI_TR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_SNLI_TR_1_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_SNLI_TR_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_SNLI_TR_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_SNLI_TR_2_0_0")
    def HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_SNLI_TR_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_EMRECAN_DISTILBERT_BASE_TURKISH_CASED_SNLI_TR_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_FACEBOOK_BART_LARGE_MNLI_1_0_0")
    def HUGGINGFACE_ZSTC_FACEBOOK_BART_LARGE_MNLI_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_FACEBOOK_BART_LARGE_MNLI_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_FACEBOOK_BART_LARGE_MNLI_2_0_0")
    def HUGGINGFACE_ZSTC_FACEBOOK_BART_LARGE_MNLI_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_FACEBOOK_BART_LARGE_MNLI_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_JIVA_XLM_ROBERTA_LARGE_IT_MNLI_1_0_0")
    def HUGGINGFACE_ZSTC_JIVA_XLM_ROBERTA_LARGE_IT_MNLI_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_JIVA_XLM_ROBERTA_LARGE_IT_MNLI_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_JIVA_XLM_ROBERTA_LARGE_IT_MNLI_2_0_0")
    def HUGGINGFACE_ZSTC_JIVA_XLM_ROBERTA_LARGE_IT_MNLI_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_JIVA_XLM_ROBERTA_LARGE_IT_MNLI_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_LIGHTETERNAL_NLI_XLM_R_GREEK_1_0_0")
    def HUGGINGFACE_ZSTC_LIGHTETERNAL_NLI_XLM_R_GREEK_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_LIGHTETERNAL_NLI_XLM_R_GREEK_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_LIGHTETERNAL_NLI_XLM_R_GREEK_2_0_0")
    def HUGGINGFACE_ZSTC_LIGHTETERNAL_NLI_XLM_R_GREEK_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_LIGHTETERNAL_NLI_XLM_R_GREEK_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_MORITZLAURER_DEBERTA_V3_LARGE_MNLI_FEVER_ANLI_LING_WANLI_1_0_0")
    def HUGGINGFACE_ZSTC_MORITZLAURER_DEBERTA_V3_LARGE_MNLI_FEVER_ANLI_LING_WANLI_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_MORITZLAURER_DEBERTA_V3_LARGE_MNLI_FEVER_ANLI_LING_WANLI_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_MORITZLAURER_DEBERTA_V3_LARGE_MNLI_FEVER_ANLI_LING_WANLI_2_0_0")
    def HUGGINGFACE_ZSTC_MORITZLAURER_DEBERTA_V3_LARGE_MNLI_FEVER_ANLI_LING_WANLI_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_MORITZLAURER_DEBERTA_V3_LARGE_MNLI_FEVER_ANLI_LING_WANLI_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_MORITZLAURER_MDEBERTA_V3_BASE_XNLI_MULTILINGUAL_NLI_2MIL7_1_0_0")
    def HUGGINGFACE_ZSTC_MORITZLAURER_MDEBERTA_V3_BASE_XNLI_MULTILINGUAL_NLI_2_MIL7_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_MORITZLAURER_MDEBERTA_V3_BASE_XNLI_MULTILINGUAL_NLI_2MIL7_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_MORITZLAURER_MDEBERTA_V3_BASE_XNLI_MULTILINGUAL_NLI_2MIL7_2_0_0")
    def HUGGINGFACE_ZSTC_MORITZLAURER_MDEBERTA_V3_BASE_XNLI_MULTILINGUAL_NLI_2_MIL7_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_MORITZLAURER_MDEBERTA_V3_BASE_XNLI_MULTILINGUAL_NLI_2MIL7_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_NARSIL_BART_LARGE_MNLI_OPTI_1_0_0")
    def HUGGINGFACE_ZSTC_NARSIL_BART_LARGE_MNLI_OPTI_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_NARSIL_BART_LARGE_MNLI_OPTI_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_NARSIL_BART_LARGE_MNLI_OPTI_2_0_0")
    def HUGGINGFACE_ZSTC_NARSIL_BART_LARGE_MNLI_OPTI_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_NARSIL_BART_LARGE_MNLI_OPTI_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_NARSIL_DEBERTA_LARGE_MNLI_ZERO_CLS_1_0_0")
    def HUGGINGFACE_ZSTC_NARSIL_DEBERTA_LARGE_MNLI_ZERO_CLS_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_NARSIL_DEBERTA_LARGE_MNLI_ZERO_CLS_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_NARSIL_DEBERTA_LARGE_MNLI_ZERO_CLS_2_0_0")
    def HUGGINGFACE_ZSTC_NARSIL_DEBERTA_LARGE_MNLI_ZERO_CLS_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_NARSIL_DEBERTA_LARGE_MNLI_ZERO_CLS_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_NAVTECA_BART_LARGE_MNLI_1_0_0")
    def HUGGINGFACE_ZSTC_NAVTECA_BART_LARGE_MNLI_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_NAVTECA_BART_LARGE_MNLI_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_NAVTECA_BART_LARGE_MNLI_2_0_0")
    def HUGGINGFACE_ZSTC_NAVTECA_BART_LARGE_MNLI_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_NAVTECA_BART_LARGE_MNLI_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_RECOGNAI_BERT_BASE_SPANISH_WWM_CASED_XNLI_1_0_0")
    def HUGGINGFACE_ZSTC_RECOGNAI_BERT_BASE_SPANISH_WWM_CASED_XNLI_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_RECOGNAI_BERT_BASE_SPANISH_WWM_CASED_XNLI_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_RECOGNAI_BERT_BASE_SPANISH_WWM_CASED_XNLI_2_0_0")
    def HUGGINGFACE_ZSTC_RECOGNAI_BERT_BASE_SPANISH_WWM_CASED_XNLI_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_RECOGNAI_BERT_BASE_SPANISH_WWM_CASED_XNLI_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_RECOGNAI_ZEROSHOT_SELECTRA_MEDIUM_1_0_0")
    def HUGGINGFACE_ZSTC_RECOGNAI_ZEROSHOT_SELECTRA_MEDIUM_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_RECOGNAI_ZEROSHOT_SELECTRA_MEDIUM_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_RECOGNAI_ZEROSHOT_SELECTRA_MEDIUM_2_0_0")
    def HUGGINGFACE_ZSTC_RECOGNAI_ZEROSHOT_SELECTRA_MEDIUM_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_RECOGNAI_ZEROSHOT_SELECTRA_MEDIUM_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_RECOGNAI_ZEROSHOT_SELECTRA_SMALL_1_0_0")
    def HUGGINGFACE_ZSTC_RECOGNAI_ZEROSHOT_SELECTRA_SMALL_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_RECOGNAI_ZEROSHOT_SELECTRA_SMALL_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HUGGINGFACE_ZSTC_RECOGNAI_ZEROSHOT_SELECTRA_SMALL_2_0_0")
    def HUGGINGFACE_ZSTC_RECOGNAI_ZEROSHOT_SELECTRA_SMALL_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "HUGGINGFACE_ZSTC_RECOGNAI_ZEROSHOT_SELECTRA_SMALL_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_2_0_0")
    def META_TEXTGENERATION_LLAMA_2_13_B_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_2_1_0")
    def META_TEXTGENERATION_LLAMA_2_13_B_2_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_2_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_2_1_1")
    def META_TEXTGENERATION_LLAMA_2_13_B_2_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_2_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_2_1_2")
    def META_TEXTGENERATION_LLAMA_2_13_B_2_1_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_2_1_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_2_1_3")
    def META_TEXTGENERATION_LLAMA_2_13_B_2_1_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_2_1_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_2_1_4")
    def META_TEXTGENERATION_LLAMA_2_13_B_2_1_4(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_2_1_4"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_2_1_5")
    def META_TEXTGENERATION_LLAMA_2_13_B_2_1_5(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_2_1_5"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_2_1_6")
    def META_TEXTGENERATION_LLAMA_2_13_B_2_1_6(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_2_1_6"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_2_1_7")
    def META_TEXTGENERATION_LLAMA_2_13_B_2_1_7(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_2_1_7"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_2_1_8")
    def META_TEXTGENERATION_LLAMA_2_13_B_2_1_8(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_2_1_8"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_3_0_0")
    def META_TEXTGENERATION_LLAMA_2_13_B_3_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_3_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_3_0_1")
    def META_TEXTGENERATION_LLAMA_2_13_B_3_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_3_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_3_0_2")
    def META_TEXTGENERATION_LLAMA_2_13_B_3_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_3_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_F_1_1_0")
    def META_TEXTGENERATION_LLAMA_2_13_B_F_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_F_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_F_1_2_0")
    def META_TEXTGENERATION_LLAMA_2_13_B_F_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_F_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_F_1_2_1")
    def META_TEXTGENERATION_LLAMA_2_13_B_F_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_F_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_F_2_0_0")
    def META_TEXTGENERATION_LLAMA_2_13_B_F_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_F_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_F_2_0_1")
    def META_TEXTGENERATION_LLAMA_2_13_B_F_2_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_F_2_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_F_2_0_2")
    def META_TEXTGENERATION_LLAMA_2_13_B_F_2_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_F_2_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_F_2_0_3")
    def META_TEXTGENERATION_LLAMA_2_13_B_F_2_0_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_F_2_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_F_2_0_4")
    def META_TEXTGENERATION_LLAMA_2_13_B_F_2_0_4(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_F_2_0_4"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_F_3_0_0")
    def META_TEXTGENERATION_LLAMA_2_13_B_F_3_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_F_3_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_F_3_0_1")
    def META_TEXTGENERATION_LLAMA_2_13_B_F_3_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_F_3_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_13B_F_3_0_2")
    def META_TEXTGENERATION_LLAMA_2_13_B_F_3_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_13B_F_3_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_1_1_0")
    def META_TEXTGENERATION_LLAMA_2_70_B_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_1_2_0")
    def META_TEXTGENERATION_LLAMA_2_70_B_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_2_0_0")
    def META_TEXTGENERATION_LLAMA_2_70_B_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_2_0_1")
    def META_TEXTGENERATION_LLAMA_2_70_B_2_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_2_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_2_0_2")
    def META_TEXTGENERATION_LLAMA_2_70_B_2_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_2_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_2_0_3")
    def META_TEXTGENERATION_LLAMA_2_70_B_2_0_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_2_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_2_0_4")
    def META_TEXTGENERATION_LLAMA_2_70_B_2_0_4(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_2_0_4"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_2_0_5")
    def META_TEXTGENERATION_LLAMA_2_70_B_2_0_5(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_2_0_5"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_2_0_6")
    def META_TEXTGENERATION_LLAMA_2_70_B_2_0_6(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_2_0_6"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_2_0_7")
    def META_TEXTGENERATION_LLAMA_2_70_B_2_0_7(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_2_0_7"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_3_0_0")
    def META_TEXTGENERATION_LLAMA_2_70_B_3_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_3_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_3_0_1")
    def META_TEXTGENERATION_LLAMA_2_70_B_3_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_3_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_3_0_2")
    def META_TEXTGENERATION_LLAMA_2_70_B_3_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_3_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_F_1_1_0")
    def META_TEXTGENERATION_LLAMA_2_70_B_F_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_F_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_F_1_2_0")
    def META_TEXTGENERATION_LLAMA_2_70_B_F_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_F_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_F_1_2_1")
    def META_TEXTGENERATION_LLAMA_2_70_B_F_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_F_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_F_2_0_0")
    def META_TEXTGENERATION_LLAMA_2_70_B_F_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_F_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_F_2_0_1")
    def META_TEXTGENERATION_LLAMA_2_70_B_F_2_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_F_2_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_F_2_0_2")
    def META_TEXTGENERATION_LLAMA_2_70_B_F_2_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_F_2_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_F_2_0_3")
    def META_TEXTGENERATION_LLAMA_2_70_B_F_2_0_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_F_2_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_F_2_0_4")
    def META_TEXTGENERATION_LLAMA_2_70_B_F_2_0_4(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_F_2_0_4"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_F_3_0_0")
    def META_TEXTGENERATION_LLAMA_2_70_B_F_3_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_F_3_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_F_3_0_1")
    def META_TEXTGENERATION_LLAMA_2_70_B_F_3_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_F_3_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_70B_F_3_0_2")
    def META_TEXTGENERATION_LLAMA_2_70_B_F_3_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_70B_F_3_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_2_0_0")
    def META_TEXTGENERATION_LLAMA_2_7_B_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_2_1_0")
    def META_TEXTGENERATION_LLAMA_2_7_B_2_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_2_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_2_1_1")
    def META_TEXTGENERATION_LLAMA_2_7_B_2_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_2_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_2_1_2")
    def META_TEXTGENERATION_LLAMA_2_7_B_2_1_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_2_1_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_2_1_3")
    def META_TEXTGENERATION_LLAMA_2_7_B_2_1_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_2_1_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_2_1_4")
    def META_TEXTGENERATION_LLAMA_2_7_B_2_1_4(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_2_1_4"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_2_1_5")
    def META_TEXTGENERATION_LLAMA_2_7_B_2_1_5(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_2_1_5"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_2_1_6")
    def META_TEXTGENERATION_LLAMA_2_7_B_2_1_6(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_2_1_6"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_2_1_7")
    def META_TEXTGENERATION_LLAMA_2_7_B_2_1_7(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_2_1_7"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_2_1_8")
    def META_TEXTGENERATION_LLAMA_2_7_B_2_1_8(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_2_1_8"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_3_0_0")
    def META_TEXTGENERATION_LLAMA_2_7_B_3_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_3_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_3_0_1")
    def META_TEXTGENERATION_LLAMA_2_7_B_3_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_3_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_3_0_2")
    def META_TEXTGENERATION_LLAMA_2_7_B_3_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_3_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_F_1_1_0")
    def META_TEXTGENERATION_LLAMA_2_7_B_F_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_F_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_F_1_2_0")
    def META_TEXTGENERATION_LLAMA_2_7_B_F_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_F_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_F_1_2_1")
    def META_TEXTGENERATION_LLAMA_2_7_B_F_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_F_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_F_2_0_0")
    def META_TEXTGENERATION_LLAMA_2_7_B_F_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_F_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_F_2_0_1")
    def META_TEXTGENERATION_LLAMA_2_7_B_F_2_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_F_2_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_F_2_0_2")
    def META_TEXTGENERATION_LLAMA_2_7_B_F_2_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_F_2_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_F_2_0_3")
    def META_TEXTGENERATION_LLAMA_2_7_B_F_2_0_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_F_2_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_F_2_0_4")
    def META_TEXTGENERATION_LLAMA_2_7_B_F_2_0_4(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_F_2_0_4"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_F_3_0_0")
    def META_TEXTGENERATION_LLAMA_2_7_B_F_3_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_F_3_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_F_3_0_1")
    def META_TEXTGENERATION_LLAMA_2_7_B_F_3_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_F_3_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_2_7B_F_3_0_2")
    def META_TEXTGENERATION_LLAMA_2_7_B_F_3_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_2_7B_F_3_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_13B_1_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_13_B_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_13B_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_13B_1_0_1")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_13_B_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_13B_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_13B_1_0_2")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_13_B_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_13B_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_13B_2_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_13_B_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_13B_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_13B_INSTRUCT_1_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_13_B_INSTRUCT_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_13B_INSTRUCT_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_13B_INSTRUCT_1_0_1")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_13_B_INSTRUCT_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_13B_INSTRUCT_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_13B_INSTRUCT_1_0_2")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_13_B_INSTRUCT_1_0_2(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_13B_INSTRUCT_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_13B_INSTRUCT_2_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_13_B_INSTRUCT_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_13B_INSTRUCT_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_13B_PYTHON_1_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_13_B_PYTHON_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_13B_PYTHON_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_13B_PYTHON_1_0_1")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_13_B_PYTHON_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_13B_PYTHON_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_13B_PYTHON_1_0_2")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_13_B_PYTHON_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_13B_PYTHON_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_13B_PYTHON_2_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_13_B_PYTHON_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_13B_PYTHON_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_34B_1_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_34_B_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_34B_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_34B_1_0_1")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_34_B_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_34B_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_34B_1_0_2")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_34_B_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_34B_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_34B_2_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_34_B_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_34B_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_34B_INSTRUCT_1_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_34_B_INSTRUCT_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_34B_INSTRUCT_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_34B_INSTRUCT_1_0_1")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_34_B_INSTRUCT_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_34B_INSTRUCT_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_34B_INSTRUCT_1_0_2")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_34_B_INSTRUCT_1_0_2(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_34B_INSTRUCT_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_34B_INSTRUCT_2_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_34_B_INSTRUCT_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_34B_INSTRUCT_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_34B_PYTHON_1_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_34_B_PYTHON_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_34B_PYTHON_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_34B_PYTHON_1_0_1")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_34_B_PYTHON_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_34B_PYTHON_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_34B_PYTHON_1_0_2")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_34_B_PYTHON_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_34B_PYTHON_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_34B_PYTHON_2_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_34_B_PYTHON_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_34B_PYTHON_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_7B_1_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_7_B_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_7B_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_7B_1_0_1")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_7_B_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_7B_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_7B_1_0_2")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_7_B_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_7B_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_7B_2_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_7_B_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_7B_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_7B_INSTRUCT_1_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_7_B_INSTRUCT_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_7B_INSTRUCT_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_7B_INSTRUCT_1_0_1")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_7_B_INSTRUCT_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_7B_INSTRUCT_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_7B_INSTRUCT_1_0_2")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_7_B_INSTRUCT_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_7B_INSTRUCT_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_7B_INSTRUCT_2_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_7_B_INSTRUCT_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_7B_INSTRUCT_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_7B_PYTHON_1_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_7_B_PYTHON_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_7B_PYTHON_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_7B_PYTHON_1_0_1")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_7_B_PYTHON_1_0_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_7B_PYTHON_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_7B_PYTHON_1_0_2")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_7_B_PYTHON_1_0_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_7B_PYTHON_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_CODELLAMA_7B_PYTHON_2_0_0")
    def META_TEXTGENERATION_LLAMA_CODELLAMA_7_B_PYTHON_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_CODELLAMA_7B_PYTHON_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_TEXTGENERATION_LLAMA_GUARD_7B_1_0_0")
    def META_TEXTGENERATION_LLAMA_GUARD_7_B_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "META_TEXTGENERATION_LLAMA_GUARD_7B_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_DEPTH2IMG_STABLE_DIFFUSION_2_DEPTH_FP16_1_0_0")
    def MODEL_DEPTH2_IMG_STABLE_DIFFUSION_2_DEPTH_FP16_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_DEPTH2IMG_STABLE_DIFFUSION_2_DEPTH_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_DEPTH2IMG_STABLE_DIFFUSION_2_DEPTH_FP16_2_0_0")
    def MODEL_DEPTH2_IMG_STABLE_DIFFUSION_2_DEPTH_FP16_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_DEPTH2IMG_STABLE_DIFFUSION_2_DEPTH_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_DEPTH2IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_1_0_0")
    def MODEL_DEPTH2_IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_DEPTH2IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_DEPTH2IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_2_0_0")
    def MODEL_DEPTH2_IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_DEPTH2IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_DEPTH2IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_FP16_1_0_0")
    def MODEL_DEPTH2_IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_FP16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_DEPTH2IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_DEPTH2IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_FP16_2_0_0")
    def MODEL_DEPTH2_IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_FP16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_DEPTH2IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_DEPTH2IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_V1_1_1_0_0")
    def MODEL_DEPTH2_IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_V1_1_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_DEPTH2IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_V1_1_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_DEPTH2IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_V1_1_2_0_0")
    def MODEL_DEPTH2_IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_V1_1_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_DEPTH2IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_V1_1_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_DEPTH2IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_V1_1_FP16_1_0_0")
    def MODEL_DEPTH2_IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_V1_1_FP16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_DEPTH2IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_V1_1_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_DEPTH2IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_V1_1_FP16_2_0_0")
    def MODEL_DEPTH2_IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_V1_1_FP16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_DEPTH2IMG_STABLE_DIFFUSION_V1_5_CONTROLNET_V1_1_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_DEPTH2IMG_STABLE_DIFFUSION_V2_1_CONTROLNET_1_0_0")
    def MODEL_DEPTH2_IMG_STABLE_DIFFUSION_V2_1_CONTROLNET_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_DEPTH2IMG_STABLE_DIFFUSION_V2_1_CONTROLNET_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_DEPTH2IMG_STABLE_DIFFUSION_V2_1_CONTROLNET_2_0_0")
    def MODEL_DEPTH2_IMG_STABLE_DIFFUSION_V2_1_CONTROLNET_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_DEPTH2IMG_STABLE_DIFFUSION_V2_1_CONTROLNET_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_DEPTH2IMG_STABLE_DIFFUSION_V2_1_CONTROLNET_FP16_1_0_0")
    def MODEL_DEPTH2_IMG_STABLE_DIFFUSION_V2_1_CONTROLNET_FP16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_DEPTH2IMG_STABLE_DIFFUSION_V2_1_CONTROLNET_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_DEPTH2IMG_STABLE_DIFFUSION_V2_1_CONTROLNET_FP16_2_0_0")
    def MODEL_DEPTH2_IMG_STABLE_DIFFUSION_V2_1_CONTROLNET_FP16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_DEPTH2IMG_STABLE_DIFFUSION_V2_1_CONTROLNET_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_IMAGEGENERATION_STABILITYAI_STABLE_DIFFUSION_V2_1_1_0_0")
    def MODEL_IMAGEGENERATION_STABILITYAI_STABLE_DIFFUSION_V2_1_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_IMAGEGENERATION_STABILITYAI_STABLE_DIFFUSION_V2_1_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_IMAGEGENERATION_STABILITYAI_STABLE_DIFFUSION_XL_BASE_1_0_1_0_0")
    def MODEL_IMAGEGENERATION_STABILITYAI_STABLE_DIFFUSION_XL_BASE_1_0_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_IMAGEGENERATION_STABILITYAI_STABLE_DIFFUSION_XL_BASE_1_0_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_IMAGEGENERATION_STABILITYAI_STABLE_DIFFUSION_XL_BASE_1_0_1_0_1")
    def MODEL_IMAGEGENERATION_STABILITYAI_STABLE_DIFFUSION_XL_BASE_1_0_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_IMAGEGENERATION_STABILITYAI_STABLE_DIFFUSION_XL_BASE_1_0_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_1_0_0")
    def MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_1_1_0")
    def MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_2_0_0")
    def MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_FP16_1_0_0")
    def MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_FP16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_FP16_1_1_0")
    def MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_FP16_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_FP16_2_0_0")
    def MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_FP16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_INPAINTING_RUNWAYML_STABLE_DIFFUSION_INPAINTING_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_1_0_0")
    def MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_1_1_0")
    def MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_2_0_0")
    def MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_FP16_1_0_0")
    def MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_FP16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_FP16_1_1_0")
    def MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_FP16_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_FP16_2_0_0")
    def MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_FP16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_INPAINTING_STABILITYAI_STABLE_DIFFUSION_2_INPAINTING_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TEXTGENERATIONJP_JAPANESE_STABLELM_INSTRUCT_ALPHA_7B_V2_1_0_0")
    def MODEL_TEXTGENERATIONJP_JAPANESE_STABLELM_INSTRUCT_ALPHA_7_B_V2_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TEXTGENERATIONJP_JAPANESE_STABLELM_INSTRUCT_ALPHA_7B_V2_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_0_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_1_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_2_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_2_1")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_2_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_2_2")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_2_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_2_3")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_2_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_3_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_3_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_1_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_2_0_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_1_0_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_1_0_1")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_1_0_2")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_1_0_2(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_1_0_3")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_1_0_3(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_1_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_1_1_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_2_0_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V1_4_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_0_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_1_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_1_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_1_1")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_1_1(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_1_2")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_1_2(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_1_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_1_3")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_1_3(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_1_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_2_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_2_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_0_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_0_1")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_0_2")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_0_2(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_0_3")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_0_3(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_0_4")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_0_4(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_0_4"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_1_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_1_1")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_1_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_1_2")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_1_2(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_1_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_1_3")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_1_3(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_1_1_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_2_0_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_1_BASE_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_2_0_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_2_0_0(cls) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_1_0_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_1_0_1")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_1_0_1(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_1_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_1_0_2")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_1_0_2(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_1_0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_1_0_3")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_1_0_3(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_1_0_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_1_1_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_2_0_0")
    def MODEL_TXT2_IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_TXT2IMG_STABILITYAI_STABLE_DIFFUSION_V2_FP16_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_UPSCALING_STABILITYAI_STABLE_DIFFUSION_X4_UPSCALER_FP16_1_0_0")
    def MODEL_UPSCALING_STABILITYAI_STABLE_DIFFUSION_X4_UPSCALER_FP16_1_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_UPSCALING_STABILITYAI_STABLE_DIFFUSION_X4_UPSCALER_FP16_1_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_UPSCALING_STABILITYAI_STABLE_DIFFUSION_X4_UPSCALER_FP16_1_1_0")
    def MODEL_UPSCALING_STABILITYAI_STABLE_DIFFUSION_X4_UPSCALER_FP16_1_1_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_UPSCALING_STABILITYAI_STABLE_DIFFUSION_X4_UPSCALER_FP16_1_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MODEL_UPSCALING_STABILITYAI_STABLE_DIFFUSION_X4_UPSCALER_FP16_2_0_0")
    def MODEL_UPSCALING_STABILITYAI_STABLE_DIFFUSION_X4_UPSCALER_FP16_2_0_0(
        cls,
    ) -> "JumpStartModel":
        '''
        :stability: experimental
        '''
        return typing.cast("JumpStartModel", jsii.sget(cls, "MODEL_UPSCALING_STABILITYAI_STABLE_DIFFUSION_X4_UPSCALER_FP16_2_0_0"))


@jsii.data_type(
    jsii_type="@cdklabs/generative-ai-cdk-constructs.JumpStartSageMakerEndpointProps",
    jsii_struct_bases=[],
    name_mapping={
        "model": "model",
        "endpoint_name": "endpointName",
        "environment": "environment",
        "instance_count": "instanceCount",
        "instance_type": "instanceType",
        "role": "role",
        "startup_health_check_timeout_in_seconds": "startupHealthCheckTimeoutInSeconds",
        "vpc_config": "vpcConfig",
    },
)
class JumpStartSageMakerEndpointProps:
    def __init__(
        self,
        *,
        model: JumpStartModel,
        endpoint_name: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        instance_count: typing.Optional[jsii.Number] = None,
        instance_type: typing.Optional["SageMakerInstanceType"] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
        startup_health_check_timeout_in_seconds: typing.Optional[jsii.Number] = None,
        vpc_config: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param model: 
        :param endpoint_name: 
        :param environment: 
        :param instance_count: 
        :param instance_type: 
        :param role: 
        :param startup_health_check_timeout_in_seconds: 
        :param vpc_config: 

        :stability: experimental
        '''
        if isinstance(vpc_config, dict):
            vpc_config = _aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty(**vpc_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a21e4787a48ba458913fa109830cd5d13f8be4ce00374d6d25306a7755c73997)
            check_type(argname="argument model", value=model, expected_type=type_hints["model"])
            check_type(argname="argument endpoint_name", value=endpoint_name, expected_type=type_hints["endpoint_name"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument instance_count", value=instance_count, expected_type=type_hints["instance_count"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument startup_health_check_timeout_in_seconds", value=startup_health_check_timeout_in_seconds, expected_type=type_hints["startup_health_check_timeout_in_seconds"])
            check_type(argname="argument vpc_config", value=vpc_config, expected_type=type_hints["vpc_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "model": model,
        }
        if endpoint_name is not None:
            self._values["endpoint_name"] = endpoint_name
        if environment is not None:
            self._values["environment"] = environment
        if instance_count is not None:
            self._values["instance_count"] = instance_count
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if role is not None:
            self._values["role"] = role
        if startup_health_check_timeout_in_seconds is not None:
            self._values["startup_health_check_timeout_in_seconds"] = startup_health_check_timeout_in_seconds
        if vpc_config is not None:
            self._values["vpc_config"] = vpc_config

    @builtins.property
    def model(self) -> JumpStartModel:
        '''
        :stability: experimental
        '''
        result = self._values.get("model")
        assert result is not None, "Required property 'model' is missing"
        return typing.cast(JumpStartModel, result)

    @builtins.property
    def endpoint_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("endpoint_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def instance_count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def instance_type(self) -> typing.Optional["SageMakerInstanceType"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional["SageMakerInstanceType"], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        '''
        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], result)

    @builtins.property
    def startup_health_check_timeout_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("startup_health_check_timeout_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc_config(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty]:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc_config")
        return typing.cast(typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JumpStartSageMakerEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LangchainCommonDepsLayer(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/generative-ai-cdk-constructs.LangchainCommonDepsLayer",
):
    '''
    :stability: experimental
    :summary: The LangchainCommonDepsLayer class.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        architecture: _aws_cdk_aws_lambda_ceddda9d.Architecture,
        runtime: _aws_cdk_aws_lambda_ceddda9d.Runtime,
        additional_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        auto_upgrade: typing.Optional[builtins.bool] = None,
        local: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        layer_version_name: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param architecture: (experimental) Required. Lambda function architecture compatible with this Layer.
        :param runtime: (experimental) Required. Lambda function runtime compatible with this Layer.
        :param additional_packages: (experimental) A prop allowing additional python pip libraries to be installed with this langchain layer. Default: - none
        :param auto_upgrade: (experimental) Optional: Add '--upgrade' to pip install requirements.txt In case of a LangchainCommonLayer, this parameter is not used. Default: - false
        :param local: (experimental) Optional: Local compute will be used when installing requirements.txt. By default, a docker container will be spun up to install requirements. To override this behavior, use the python alias string of ``python`` or ``python3`` The string value will be the python alias used to install requirements. Default: - none
        :param description: The description the this Lambda Layer. Default: - No description.
        :param layer_version_name: The name of the layer. Default: - A name will be generated.
        :param license: The SPDX licence identifier or URL to the license file for this layer. Default: - No license information will be recorded.
        :param removal_policy: Whether to retain this version of the layer when a new version is added or when the stack is deleted. Default: RemovalPolicy.DESTROY

        :stability: experimental
        :access: public
        :since: 0.0.0
        :summary: This construct creates a lambda layer loaded with relevant libraries to run genai applications. Libraries include boto3, botocore, requests, requests-aws4auth, langchain, opensearch-py and openai.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5887bf17d5f030e30d4d81e59cc58f7736b547350a7fc34d4824591bab542b31)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = LangchainLayerProps(
            architecture=architecture,
            runtime=runtime,
            additional_packages=additional_packages,
            auto_upgrade=auto_upgrade,
            local=local,
            description=description,
            layer_version_name=layer_version_name,
            license=license,
            removal_policy=removal_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="layer")
    def layer(self) -> _aws_cdk_aws_lambda_ceddda9d.LayerVersion:
        '''(experimental) Returns the instance of lambda.LayerVersion created by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.LayerVersion, jsii.get(self, "layer"))


class LangchainCommonLayer(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/generative-ai-cdk-constructs.LangchainCommonLayer",
):
    '''
    :stability: experimental
    :summary: LangchainCommonLayer allows developers to instantiate a llm client adapter on bedrock, sagemaker or openai following best practise.

    Example::

        import boto3
        from genai_core.adapters.registry import registry
        
        adapter = registry.get_adapter(f"{provider}.{model_id}")
        bedrock_client = boto3.client('bedrock-runtime')
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        compatible_architectures: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.Architecture]] = None,
        compatible_runtimes: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.Runtime]] = None,
        description: typing.Optional[builtins.str] = None,
        layer_version_name: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param compatible_architectures: The system architectures compatible with this layer. Default: [Architecture.X86_64]
        :param compatible_runtimes: The runtimes compatible with this Layer. Default: - All runtimes are supported.
        :param description: The description the this Lambda Layer. Default: - No description.
        :param layer_version_name: The name of the layer. Default: - A name will be generated.
        :param license: The SPDX licence identifier or URL to the license file for this layer. Default: - No license information will be recorded.
        :param removal_policy: Whether to retain this version of the layer when a new version is added or when the stack is deleted. Default: RemovalPolicy.DESTROY

        :stability: experimental
        :access: public
        :since: 0.0.0
        :summary: This construct allows developers to instantiate a llm client adapter on bedrock, sagemaker or openai following best practise.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9da98e3b66ac7e9145afc01d0bcd18f45c1684ff1bc89ccc645b65e2edc8f13a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AdapterProps(
            compatible_architectures=compatible_architectures,
            compatible_runtimes=compatible_runtimes,
            description=description,
            layer_version_name=layer_version_name,
            license=license,
            removal_policy=removal_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="layer")
    def layer(self) -> _aws_cdk_aws_lambda_ceddda9d.LayerVersion:
        '''(experimental) Returns the instance of lambda.LayerVersion created by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.LayerVersion, jsii.get(self, "layer"))


@jsii.data_type(
    jsii_type="@cdklabs/generative-ai-cdk-constructs.LangchainProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "layer_version_name": "layerVersionName",
        "license": "license",
        "removal_policy": "removalPolicy",
    },
)
class LangchainProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        layer_version_name: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''(experimental) LangchainProps.

        :param description: The description the this Lambda Layer. Default: - No description.
        :param layer_version_name: The name of the layer. Default: - A name will be generated.
        :param license: The SPDX licence identifier or URL to the license file for this layer. Default: - No license information will be recorded.
        :param removal_policy: Whether to retain this version of the layer when a new version is added or when the stack is deleted. Default: RemovalPolicy.DESTROY

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52d31c4ca4bd0cf5b3967d59cb772ea252af908e216abb9db44bcadbdcb0c948)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument layer_version_name", value=layer_version_name, expected_type=type_hints["layer_version_name"])
            check_type(argname="argument license", value=license, expected_type=type_hints["license"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if layer_version_name is not None:
            self._values["layer_version_name"] = layer_version_name
        if license is not None:
            self._values["license"] = license
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description the this Lambda Layer.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def layer_version_name(self) -> typing.Optional[builtins.str]:
        '''The name of the layer.

        :default: - A name will be generated.
        '''
        result = self._values.get("layer_version_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''The SPDX licence identifier or URL to the license file for this layer.

        :default: - No license information will be recorded.
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Whether to retain this version of the layer when a new version is added or when the stack is deleted.

        :default: RemovalPolicy.DESTROY
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LangchainProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QaAppsyncOpensearch(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/generative-ai-cdk-constructs.QaAppsyncOpensearch",
):
    '''
    :stability: experimental
    :summary: The QaAppsyncOpensearch class.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cognito_user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
        open_search_index_name: builtins.str,
        bucket_inputs_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_operational_metric: typing.Optional[builtins.bool] = None,
        existing_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        existing_input_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        existing_merged_api: typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi] = None,
        existing_opensearch_domain: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IDomain] = None,
        existing_opensearch_serverless_collection: typing.Optional[_aws_cdk_aws_opensearchserverless_ceddda9d.CfnCollection] = None,
        existing_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        lambda_provisioned_concurrency: typing.Optional[jsii.Number] = None,
        observability: typing.Optional[builtins.bool] = None,
        open_search_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        stage: typing.Optional[builtins.str] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param cognito_user_pool: (experimental) Cognito user pool used for authentication. Default: - None
        :param open_search_index_name: (experimental) Data Index name for the OpenSearch Service. Default: - None
        :param bucket_inputs_assets_props: (experimental) Optional user provided props to override the default props for the S3 Bucket. Providing both this and ``existingInputAssetsBucketObj`` will cause an error. Default: - Default props are used
        :param enable_operational_metric: (experimental) Optional.CDK constructs provided collects anonymous operational metrics to help AWS improve the quality and features of the constructs. Data collection is subject to the AWS Privacy Policy (https://aws.amazon.com/privacy/). To opt out of this feature, simply disable it by setting the construct property "enableOperationalMetric" to false for each construct used. Default: - true
        :param existing_bus_interface: (experimental) Optional Existing instance of an EventBridge bus. If not provided, the construct will create one. Default: - None
        :param existing_input_assets_bucket_obj: (experimental) Existing instance of S3 Bucket object, providing both this and ``bucketInputsAssetsProps`` will cause an error. Default: - None
        :param existing_merged_api: (experimental) Existing merged Appsync GraphQL api. Default: - None
        :param existing_opensearch_domain: (experimental) Existing Amazon OpenSearch Service domain. Default: - None
        :param existing_opensearch_serverless_collection: (experimental) Existing Amazon Amazon OpenSearch Serverless collection. Default: - None
        :param existing_security_group: (experimental) Optional existing security group allowing access to opensearch. Used by the lambda functions built by this construct. If not provided, the construct will create one. Default: - none
        :param existing_vpc: (experimental) Optional An existing VPC in which to deploy the construct. Providing both this and vpcProps is an error. Default: - none
        :param lambda_provisioned_concurrency: (experimental) Optional. Allows a user to configure Lambda provisioned concurrency for consistent performance
        :param observability: (experimental) Enable observability. Warning: associated cost with the services used. Best practive to enable by default. Default: - true
        :param open_search_secret: (experimental) Optional. SecretsManager secret to authenticate against the OpenSearch Service domain if domain is configured with Username/Password. Default: - None
        :param stage: (experimental) Value will be appended to resources name. Default: - _dev
        :param vpc_props: (experimental) Optional custom properties for a VPC the construct will create. This VPC will be used by the Lambda functions the construct creates. Providing both this and existingVpc is an error. Default: - none

        :stability: experimental
        :access: public
        :since: 0.0.0
        :summary: Constructs a new instance of the RagAppsyncStepfnOpensearch class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87235dce222bf37474e367e0b5284fe8ad89c007d7c7d06682de5ff0d56df01b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = QaAppsyncOpensearchProps(
            cognito_user_pool=cognito_user_pool,
            open_search_index_name=open_search_index_name,
            bucket_inputs_assets_props=bucket_inputs_assets_props,
            enable_operational_metric=enable_operational_metric,
            existing_bus_interface=existing_bus_interface,
            existing_input_assets_bucket_obj=existing_input_assets_bucket_obj,
            existing_merged_api=existing_merged_api,
            existing_opensearch_domain=existing_opensearch_domain,
            existing_opensearch_serverless_collection=existing_opensearch_serverless_collection,
            existing_security_group=existing_security_group,
            existing_vpc=existing_vpc,
            lambda_provisioned_concurrency=lambda_provisioned_concurrency,
            observability=observability,
            open_search_secret=open_search_secret,
            stage=stage,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="graphqlApi")
    def graphql_api(self) -> _aws_cdk_aws_appsync_ceddda9d.IGraphqlApi:
        '''(experimental) Returns an instance of appsync.IGraphqlApi created by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_appsync_ceddda9d.IGraphqlApi, jsii.get(self, "graphqlApi"))

    @builtins.property
    @jsii.member(jsii_name="qaBus")
    def qa_bus(self) -> _aws_cdk_aws_events_ceddda9d.IEventBus:
        '''(experimental) Returns the instance of events.IEventBus used by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_events_ceddda9d.IEventBus, jsii.get(self, "qaBus"))

    @builtins.property
    @jsii.member(jsii_name="s3InputAssetsBucketInterface")
    def s3_input_assets_bucket_interface(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''(experimental) Returns an instance of s3.IBucket created by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "s3InputAssetsBucketInterface"))

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        '''(experimental) Returns the instance of ec2.ISecurityGroup used by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup, jsii.get(self, "securityGroup"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) Returns the instance of ec2.IVpc used by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="s3InputAssetsBucket")
    def s3_input_assets_bucket(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        '''(experimental) Returns an instance of s3.Bucket created by the construct. IMPORTANT: If existingInputAssetsBucketObj was provided in Pattern Construct Props, this property will be undefined.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], jsii.get(self, "s3InputAssetsBucket"))


@jsii.data_type(
    jsii_type="@cdklabs/generative-ai-cdk-constructs.QaAppsyncOpensearchProps",
    jsii_struct_bases=[],
    name_mapping={
        "cognito_user_pool": "cognitoUserPool",
        "open_search_index_name": "openSearchIndexName",
        "bucket_inputs_assets_props": "bucketInputsAssetsProps",
        "enable_operational_metric": "enableOperationalMetric",
        "existing_bus_interface": "existingBusInterface",
        "existing_input_assets_bucket_obj": "existingInputAssetsBucketObj",
        "existing_merged_api": "existingMergedApi",
        "existing_opensearch_domain": "existingOpensearchDomain",
        "existing_opensearch_serverless_collection": "existingOpensearchServerlessCollection",
        "existing_security_group": "existingSecurityGroup",
        "existing_vpc": "existingVpc",
        "lambda_provisioned_concurrency": "lambdaProvisionedConcurrency",
        "observability": "observability",
        "open_search_secret": "openSearchSecret",
        "stage": "stage",
        "vpc_props": "vpcProps",
    },
)
class QaAppsyncOpensearchProps:
    def __init__(
        self,
        *,
        cognito_user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
        open_search_index_name: builtins.str,
        bucket_inputs_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_operational_metric: typing.Optional[builtins.bool] = None,
        existing_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        existing_input_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        existing_merged_api: typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi] = None,
        existing_opensearch_domain: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IDomain] = None,
        existing_opensearch_serverless_collection: typing.Optional[_aws_cdk_aws_opensearchserverless_ceddda9d.CfnCollection] = None,
        existing_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        lambda_provisioned_concurrency: typing.Optional[jsii.Number] = None,
        observability: typing.Optional[builtins.bool] = None,
        open_search_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        stage: typing.Optional[builtins.str] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) The properties for the QaAppsyncOpensearchProps class.

        :param cognito_user_pool: (experimental) Cognito user pool used for authentication. Default: - None
        :param open_search_index_name: (experimental) Data Index name for the OpenSearch Service. Default: - None
        :param bucket_inputs_assets_props: (experimental) Optional user provided props to override the default props for the S3 Bucket. Providing both this and ``existingInputAssetsBucketObj`` will cause an error. Default: - Default props are used
        :param enable_operational_metric: (experimental) Optional.CDK constructs provided collects anonymous operational metrics to help AWS improve the quality and features of the constructs. Data collection is subject to the AWS Privacy Policy (https://aws.amazon.com/privacy/). To opt out of this feature, simply disable it by setting the construct property "enableOperationalMetric" to false for each construct used. Default: - true
        :param existing_bus_interface: (experimental) Optional Existing instance of an EventBridge bus. If not provided, the construct will create one. Default: - None
        :param existing_input_assets_bucket_obj: (experimental) Existing instance of S3 Bucket object, providing both this and ``bucketInputsAssetsProps`` will cause an error. Default: - None
        :param existing_merged_api: (experimental) Existing merged Appsync GraphQL api. Default: - None
        :param existing_opensearch_domain: (experimental) Existing Amazon OpenSearch Service domain. Default: - None
        :param existing_opensearch_serverless_collection: (experimental) Existing Amazon Amazon OpenSearch Serverless collection. Default: - None
        :param existing_security_group: (experimental) Optional existing security group allowing access to opensearch. Used by the lambda functions built by this construct. If not provided, the construct will create one. Default: - none
        :param existing_vpc: (experimental) Optional An existing VPC in which to deploy the construct. Providing both this and vpcProps is an error. Default: - none
        :param lambda_provisioned_concurrency: (experimental) Optional. Allows a user to configure Lambda provisioned concurrency for consistent performance
        :param observability: (experimental) Enable observability. Warning: associated cost with the services used. Best practive to enable by default. Default: - true
        :param open_search_secret: (experimental) Optional. SecretsManager secret to authenticate against the OpenSearch Service domain if domain is configured with Username/Password. Default: - None
        :param stage: (experimental) Value will be appended to resources name. Default: - _dev
        :param vpc_props: (experimental) Optional custom properties for a VPC the construct will create. This VPC will be used by the Lambda functions the construct creates. Providing both this and existingVpc is an error. Default: - none

        :stability: experimental
        '''
        if isinstance(bucket_inputs_assets_props, dict):
            bucket_inputs_assets_props = _aws_cdk_aws_s3_ceddda9d.BucketProps(**bucket_inputs_assets_props)
        if isinstance(vpc_props, dict):
            vpc_props = _aws_cdk_aws_ec2_ceddda9d.VpcProps(**vpc_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff2c8f0d402dcb481b313b3fe2800ddb797d454c33c358eadd45c7a626be6592)
            check_type(argname="argument cognito_user_pool", value=cognito_user_pool, expected_type=type_hints["cognito_user_pool"])
            check_type(argname="argument open_search_index_name", value=open_search_index_name, expected_type=type_hints["open_search_index_name"])
            check_type(argname="argument bucket_inputs_assets_props", value=bucket_inputs_assets_props, expected_type=type_hints["bucket_inputs_assets_props"])
            check_type(argname="argument enable_operational_metric", value=enable_operational_metric, expected_type=type_hints["enable_operational_metric"])
            check_type(argname="argument existing_bus_interface", value=existing_bus_interface, expected_type=type_hints["existing_bus_interface"])
            check_type(argname="argument existing_input_assets_bucket_obj", value=existing_input_assets_bucket_obj, expected_type=type_hints["existing_input_assets_bucket_obj"])
            check_type(argname="argument existing_merged_api", value=existing_merged_api, expected_type=type_hints["existing_merged_api"])
            check_type(argname="argument existing_opensearch_domain", value=existing_opensearch_domain, expected_type=type_hints["existing_opensearch_domain"])
            check_type(argname="argument existing_opensearch_serverless_collection", value=existing_opensearch_serverless_collection, expected_type=type_hints["existing_opensearch_serverless_collection"])
            check_type(argname="argument existing_security_group", value=existing_security_group, expected_type=type_hints["existing_security_group"])
            check_type(argname="argument existing_vpc", value=existing_vpc, expected_type=type_hints["existing_vpc"])
            check_type(argname="argument lambda_provisioned_concurrency", value=lambda_provisioned_concurrency, expected_type=type_hints["lambda_provisioned_concurrency"])
            check_type(argname="argument observability", value=observability, expected_type=type_hints["observability"])
            check_type(argname="argument open_search_secret", value=open_search_secret, expected_type=type_hints["open_search_secret"])
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
            check_type(argname="argument vpc_props", value=vpc_props, expected_type=type_hints["vpc_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cognito_user_pool": cognito_user_pool,
            "open_search_index_name": open_search_index_name,
        }
        if bucket_inputs_assets_props is not None:
            self._values["bucket_inputs_assets_props"] = bucket_inputs_assets_props
        if enable_operational_metric is not None:
            self._values["enable_operational_metric"] = enable_operational_metric
        if existing_bus_interface is not None:
            self._values["existing_bus_interface"] = existing_bus_interface
        if existing_input_assets_bucket_obj is not None:
            self._values["existing_input_assets_bucket_obj"] = existing_input_assets_bucket_obj
        if existing_merged_api is not None:
            self._values["existing_merged_api"] = existing_merged_api
        if existing_opensearch_domain is not None:
            self._values["existing_opensearch_domain"] = existing_opensearch_domain
        if existing_opensearch_serverless_collection is not None:
            self._values["existing_opensearch_serverless_collection"] = existing_opensearch_serverless_collection
        if existing_security_group is not None:
            self._values["existing_security_group"] = existing_security_group
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if lambda_provisioned_concurrency is not None:
            self._values["lambda_provisioned_concurrency"] = lambda_provisioned_concurrency
        if observability is not None:
            self._values["observability"] = observability
        if open_search_secret is not None:
            self._values["open_search_secret"] = open_search_secret
        if stage is not None:
            self._values["stage"] = stage
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def cognito_user_pool(self) -> _aws_cdk_aws_cognito_ceddda9d.IUserPool:
        '''(experimental) Cognito user pool used for authentication.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("cognito_user_pool")
        assert result is not None, "Required property 'cognito_user_pool' is missing"
        return typing.cast(_aws_cdk_aws_cognito_ceddda9d.IUserPool, result)

    @builtins.property
    def open_search_index_name(self) -> builtins.str:
        '''(experimental) Data Index name for the OpenSearch Service.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("open_search_index_name")
        assert result is not None, "Required property 'open_search_index_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bucket_inputs_assets_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps]:
        '''(experimental) Optional user provided props to override the default props for the S3 Bucket.

        Providing both this and ``existingInputAssetsBucketObj`` will cause an error.

        :default: - Default props are used

        :stability: experimental
        '''
        result = self._values.get("bucket_inputs_assets_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps], result)

    @builtins.property
    def enable_operational_metric(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Optional.CDK constructs provided collects anonymous operational metrics to help AWS improve the quality and features of the constructs. Data collection is subject to the AWS Privacy Policy (https://aws.amazon.com/privacy/). To opt out of this feature, simply disable it by setting the construct property "enableOperationalMetric" to false for each construct used.

        :default: - true

        :stability: experimental
        '''
        result = self._values.get("enable_operational_metric")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def existing_bus_interface(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus]:
        '''(experimental) Optional Existing instance of an EventBridge bus.

        If not provided, the construct will create one.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("existing_bus_interface")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus], result)

    @builtins.property
    def existing_input_assets_bucket_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''(experimental) Existing instance of S3 Bucket object, providing both this and ``bucketInputsAssetsProps`` will cause an error.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("existing_input_assets_bucket_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def existing_merged_api(
        self,
    ) -> typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi]:
        '''(experimental) Existing merged Appsync GraphQL api.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("existing_merged_api")
        return typing.cast(typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi], result)

    @builtins.property
    def existing_opensearch_domain(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IDomain]:
        '''(experimental) Existing Amazon OpenSearch Service domain.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("existing_opensearch_domain")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IDomain], result)

    @builtins.property
    def existing_opensearch_serverless_collection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchserverless_ceddda9d.CfnCollection]:
        '''(experimental) Existing Amazon Amazon OpenSearch Serverless collection.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("existing_opensearch_serverless_collection")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchserverless_ceddda9d.CfnCollection], result)

    @builtins.property
    def existing_security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''(experimental) Optional existing security group allowing access to opensearch.

        Used by the lambda functions
        built by this construct. If not provided, the construct will create one.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("existing_security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) Optional An existing VPC in which to deploy the construct.

        Providing both this and
        vpcProps is an error.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def lambda_provisioned_concurrency(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Optional.

        Allows a user to configure
        Lambda provisioned concurrency for consistent performance

        :stability: experimental
        '''
        result = self._values.get("lambda_provisioned_concurrency")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def observability(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable observability.

        Warning: associated cost with the services
        used. Best practive to enable by default.

        :default: - true

        :stability: experimental
        '''
        result = self._values.get("observability")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def open_search_secret(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        '''(experimental) Optional.

        SecretsManager secret to authenticate against the OpenSearch Service domain if
        domain is configured with Username/Password.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("open_search_secret")
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], result)

    @builtins.property
    def stage(self) -> typing.Optional[builtins.str]:
        '''(experimental) Value will be appended to resources name.

        :default: - _dev

        :stability: experimental
        '''
        result = self._values.get("stage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_props(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps]:
        '''(experimental) Optional custom properties for a VPC the construct will create.

        This VPC will
        be used by the Lambda functions the construct creates. Providing
        both this and existingVpc is an error.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QaAppsyncOpensearchProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RagAppsyncStepfnOpensearch(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/generative-ai-cdk-constructs.RagAppsyncStepfnOpensearch",
):
    '''
    :stability: experimental
    :summary: The RagAppsyncStepfnOpensearch class.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cognito_user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
        open_search_index_name: builtins.str,
        bucket_inputs_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        bucket_processed_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_operational_metric: typing.Optional[builtins.bool] = None,
        existing_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        existing_input_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        existing_merged_api: typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi] = None,
        existing_opensearch_domain: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IDomain] = None,
        existing_opensearch_serverless_collection: typing.Optional[_aws_cdk_aws_opensearchserverless_ceddda9d.CfnCollection] = None,
        existing_processed_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        existing_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        observability: typing.Optional[builtins.bool] = None,
        open_search_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        stage: typing.Optional[builtins.str] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param cognito_user_pool: (experimental) Cognito user pool used for authentication. Default: - None
        :param open_search_index_name: (experimental) Index name for the OpenSearch Service. Default: - None
        :param bucket_inputs_assets_props: (experimental) Optional user provided props to override the default props for the S3 Bucket. Providing both this and ``existingInputAssetsBucketObj`` will cause an error. Default: - Default props are used
        :param bucket_processed_assets_props: (experimental) Optional user provided props to override the default props for the S3 Bucket. Providing both this and ``existingProcessedAssetsBucketObj`` will cause an error. Default: - Default props are used
        :param enable_operational_metric: (experimental) Optional.CDK constructs provided collects anonymous operational metrics to help AWS improve the quality and features of the constructs. Data collection is subject to the AWS Privacy Policy (https://aws.amazon.com/privacy/). To opt out of this feature, simply disable it by setting the construct property "enableOperationalMetric" to false for each construct used. Default: - true
        :param existing_bus_interface: (experimental) Optional Existing instance of an EventBridge bus. If not provided, the construct will create one. Default: - None
        :param existing_input_assets_bucket_obj: (experimental) Existing instance of S3 Bucket object, providing both this and ``bucketInputsAssetsProps`` will cause an error. Default: - None
        :param existing_merged_api: (experimental) Existing merged Appsync GraphQL api. Default: - None
        :param existing_opensearch_domain: (experimental) Optional existing Amazon OpenSearch Service domain. Default: - None
        :param existing_opensearch_serverless_collection: (experimental) Optional existing Amazon Amazon OpenSearch Serverless collection. Default: - None
        :param existing_processed_assets_bucket_obj: (experimental) Existing instance of S3 Bucket object, providing both this and ``bucketProcessedAssetsProps`` will cause an error. Default: - None
        :param existing_security_group: (experimental) Optional existing security group allowing access to opensearch. Used by the lambda functions built by this construct. If not provided, the construct will create one. Default: - none
        :param existing_vpc: (experimental) Optional An existing VPC in which to deploy the construct. Providing both this and vpcProps is an error. Default: - none
        :param observability: (experimental) Enable observability. Warning: associated cost with the services used. Best practice to enable by default. Default: - true
        :param open_search_secret: (experimental) Optional. SecretsManager secret to authenticate against the OpenSearch Service domain if domain is configured with Username/Password. Default: - None
        :param stage: (experimental) Value will be appended to resources name. Default: - _dev
        :param vpc_props: (experimental) Optional custom properties for a VPC the construct will create. This VPC will be used by the Lambda functions the construct creates. Providing both this and existingVpc is an error. Default: - none

        :stability: experimental
        :access: public
        :since: 0.0.0
        :summary: Constructs a new instance of the RagAppsyncStepfnOpensearch class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b47682f30dcd4f711daa26c544bfc9e0888d2931d0711782d9e99f42de2ba10)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RagAppsyncStepfnOpensearchProps(
            cognito_user_pool=cognito_user_pool,
            open_search_index_name=open_search_index_name,
            bucket_inputs_assets_props=bucket_inputs_assets_props,
            bucket_processed_assets_props=bucket_processed_assets_props,
            enable_operational_metric=enable_operational_metric,
            existing_bus_interface=existing_bus_interface,
            existing_input_assets_bucket_obj=existing_input_assets_bucket_obj,
            existing_merged_api=existing_merged_api,
            existing_opensearch_domain=existing_opensearch_domain,
            existing_opensearch_serverless_collection=existing_opensearch_serverless_collection,
            existing_processed_assets_bucket_obj=existing_processed_assets_bucket_obj,
            existing_security_group=existing_security_group,
            existing_vpc=existing_vpc,
            observability=observability,
            open_search_secret=open_search_secret,
            stage=stage,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="graphqlApi")
    def graphql_api(self) -> _aws_cdk_aws_appsync_ceddda9d.IGraphqlApi:
        '''(experimental) Returns an instance of appsync.IGraphqlApi created by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_appsync_ceddda9d.IGraphqlApi, jsii.get(self, "graphqlApi"))

    @builtins.property
    @jsii.member(jsii_name="ingestionBus")
    def ingestion_bus(self) -> _aws_cdk_aws_events_ceddda9d.IEventBus:
        '''(experimental) Returns the instance of events.IEventBus used by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_events_ceddda9d.IEventBus, jsii.get(self, "ingestionBus"))

    @builtins.property
    @jsii.member(jsii_name="s3InputAssetsBucketInterface")
    def s3_input_assets_bucket_interface(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''(experimental) Returns an instance of s3.IBucket created by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "s3InputAssetsBucketInterface"))

    @builtins.property
    @jsii.member(jsii_name="s3ProcessedAssetsBucketInterface")
    def s3_processed_assets_bucket_interface(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''(experimental) Returns an instance of s3.IBucket created by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "s3ProcessedAssetsBucketInterface"))

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        '''(experimental) Returns the instance of ec2.ISecurityGroup used by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup, jsii.get(self, "securityGroup"))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''(experimental) Returns an instance of stepfn.StateMachine created by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.get(self, "stateMachine"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) Returns the instance of ec2.IVpc used by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="s3InputAssetsBucket")
    def s3_input_assets_bucket(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        '''(experimental) Returns an instance of s3.Bucket created by the construct. IMPORTANT: If existingInputAssetsBucketObj was provided in Pattern Construct Props, this property will be undefined.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], jsii.get(self, "s3InputAssetsBucket"))

    @builtins.property
    @jsii.member(jsii_name="s3ProcessedAssetsBucket")
    def s3_processed_assets_bucket(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        '''(experimental) Returns an instance of s3.Bucket created by the construct. IMPORTANT: If existingProcessedAssetsBucketObj was provided in Pattern Construct Props, this property will be undefined.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], jsii.get(self, "s3ProcessedAssetsBucket"))


@jsii.data_type(
    jsii_type="@cdklabs/generative-ai-cdk-constructs.RagAppsyncStepfnOpensearchProps",
    jsii_struct_bases=[],
    name_mapping={
        "cognito_user_pool": "cognitoUserPool",
        "open_search_index_name": "openSearchIndexName",
        "bucket_inputs_assets_props": "bucketInputsAssetsProps",
        "bucket_processed_assets_props": "bucketProcessedAssetsProps",
        "enable_operational_metric": "enableOperationalMetric",
        "existing_bus_interface": "existingBusInterface",
        "existing_input_assets_bucket_obj": "existingInputAssetsBucketObj",
        "existing_merged_api": "existingMergedApi",
        "existing_opensearch_domain": "existingOpensearchDomain",
        "existing_opensearch_serverless_collection": "existingOpensearchServerlessCollection",
        "existing_processed_assets_bucket_obj": "existingProcessedAssetsBucketObj",
        "existing_security_group": "existingSecurityGroup",
        "existing_vpc": "existingVpc",
        "observability": "observability",
        "open_search_secret": "openSearchSecret",
        "stage": "stage",
        "vpc_props": "vpcProps",
    },
)
class RagAppsyncStepfnOpensearchProps:
    def __init__(
        self,
        *,
        cognito_user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
        open_search_index_name: builtins.str,
        bucket_inputs_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        bucket_processed_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_operational_metric: typing.Optional[builtins.bool] = None,
        existing_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        existing_input_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        existing_merged_api: typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi] = None,
        existing_opensearch_domain: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IDomain] = None,
        existing_opensearch_serverless_collection: typing.Optional[_aws_cdk_aws_opensearchserverless_ceddda9d.CfnCollection] = None,
        existing_processed_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        existing_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        observability: typing.Optional[builtins.bool] = None,
        open_search_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        stage: typing.Optional[builtins.str] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) The properties for the RagAppsyncStepfnOpensearchProps class.

        :param cognito_user_pool: (experimental) Cognito user pool used for authentication. Default: - None
        :param open_search_index_name: (experimental) Index name for the OpenSearch Service. Default: - None
        :param bucket_inputs_assets_props: (experimental) Optional user provided props to override the default props for the S3 Bucket. Providing both this and ``existingInputAssetsBucketObj`` will cause an error. Default: - Default props are used
        :param bucket_processed_assets_props: (experimental) Optional user provided props to override the default props for the S3 Bucket. Providing both this and ``existingProcessedAssetsBucketObj`` will cause an error. Default: - Default props are used
        :param enable_operational_metric: (experimental) Optional.CDK constructs provided collects anonymous operational metrics to help AWS improve the quality and features of the constructs. Data collection is subject to the AWS Privacy Policy (https://aws.amazon.com/privacy/). To opt out of this feature, simply disable it by setting the construct property "enableOperationalMetric" to false for each construct used. Default: - true
        :param existing_bus_interface: (experimental) Optional Existing instance of an EventBridge bus. If not provided, the construct will create one. Default: - None
        :param existing_input_assets_bucket_obj: (experimental) Existing instance of S3 Bucket object, providing both this and ``bucketInputsAssetsProps`` will cause an error. Default: - None
        :param existing_merged_api: (experimental) Existing merged Appsync GraphQL api. Default: - None
        :param existing_opensearch_domain: (experimental) Optional existing Amazon OpenSearch Service domain. Default: - None
        :param existing_opensearch_serverless_collection: (experimental) Optional existing Amazon Amazon OpenSearch Serverless collection. Default: - None
        :param existing_processed_assets_bucket_obj: (experimental) Existing instance of S3 Bucket object, providing both this and ``bucketProcessedAssetsProps`` will cause an error. Default: - None
        :param existing_security_group: (experimental) Optional existing security group allowing access to opensearch. Used by the lambda functions built by this construct. If not provided, the construct will create one. Default: - none
        :param existing_vpc: (experimental) Optional An existing VPC in which to deploy the construct. Providing both this and vpcProps is an error. Default: - none
        :param observability: (experimental) Enable observability. Warning: associated cost with the services used. Best practice to enable by default. Default: - true
        :param open_search_secret: (experimental) Optional. SecretsManager secret to authenticate against the OpenSearch Service domain if domain is configured with Username/Password. Default: - None
        :param stage: (experimental) Value will be appended to resources name. Default: - _dev
        :param vpc_props: (experimental) Optional custom properties for a VPC the construct will create. This VPC will be used by the Lambda functions the construct creates. Providing both this and existingVpc is an error. Default: - none

        :stability: experimental
        '''
        if isinstance(bucket_inputs_assets_props, dict):
            bucket_inputs_assets_props = _aws_cdk_aws_s3_ceddda9d.BucketProps(**bucket_inputs_assets_props)
        if isinstance(bucket_processed_assets_props, dict):
            bucket_processed_assets_props = _aws_cdk_aws_s3_ceddda9d.BucketProps(**bucket_processed_assets_props)
        if isinstance(vpc_props, dict):
            vpc_props = _aws_cdk_aws_ec2_ceddda9d.VpcProps(**vpc_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84410e9ddf3c6c72a9fafb245544fa73e4c8020dfb3e51d2f31e3b9c8bfa846f)
            check_type(argname="argument cognito_user_pool", value=cognito_user_pool, expected_type=type_hints["cognito_user_pool"])
            check_type(argname="argument open_search_index_name", value=open_search_index_name, expected_type=type_hints["open_search_index_name"])
            check_type(argname="argument bucket_inputs_assets_props", value=bucket_inputs_assets_props, expected_type=type_hints["bucket_inputs_assets_props"])
            check_type(argname="argument bucket_processed_assets_props", value=bucket_processed_assets_props, expected_type=type_hints["bucket_processed_assets_props"])
            check_type(argname="argument enable_operational_metric", value=enable_operational_metric, expected_type=type_hints["enable_operational_metric"])
            check_type(argname="argument existing_bus_interface", value=existing_bus_interface, expected_type=type_hints["existing_bus_interface"])
            check_type(argname="argument existing_input_assets_bucket_obj", value=existing_input_assets_bucket_obj, expected_type=type_hints["existing_input_assets_bucket_obj"])
            check_type(argname="argument existing_merged_api", value=existing_merged_api, expected_type=type_hints["existing_merged_api"])
            check_type(argname="argument existing_opensearch_domain", value=existing_opensearch_domain, expected_type=type_hints["existing_opensearch_domain"])
            check_type(argname="argument existing_opensearch_serverless_collection", value=existing_opensearch_serverless_collection, expected_type=type_hints["existing_opensearch_serverless_collection"])
            check_type(argname="argument existing_processed_assets_bucket_obj", value=existing_processed_assets_bucket_obj, expected_type=type_hints["existing_processed_assets_bucket_obj"])
            check_type(argname="argument existing_security_group", value=existing_security_group, expected_type=type_hints["existing_security_group"])
            check_type(argname="argument existing_vpc", value=existing_vpc, expected_type=type_hints["existing_vpc"])
            check_type(argname="argument observability", value=observability, expected_type=type_hints["observability"])
            check_type(argname="argument open_search_secret", value=open_search_secret, expected_type=type_hints["open_search_secret"])
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
            check_type(argname="argument vpc_props", value=vpc_props, expected_type=type_hints["vpc_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cognito_user_pool": cognito_user_pool,
            "open_search_index_name": open_search_index_name,
        }
        if bucket_inputs_assets_props is not None:
            self._values["bucket_inputs_assets_props"] = bucket_inputs_assets_props
        if bucket_processed_assets_props is not None:
            self._values["bucket_processed_assets_props"] = bucket_processed_assets_props
        if enable_operational_metric is not None:
            self._values["enable_operational_metric"] = enable_operational_metric
        if existing_bus_interface is not None:
            self._values["existing_bus_interface"] = existing_bus_interface
        if existing_input_assets_bucket_obj is not None:
            self._values["existing_input_assets_bucket_obj"] = existing_input_assets_bucket_obj
        if existing_merged_api is not None:
            self._values["existing_merged_api"] = existing_merged_api
        if existing_opensearch_domain is not None:
            self._values["existing_opensearch_domain"] = existing_opensearch_domain
        if existing_opensearch_serverless_collection is not None:
            self._values["existing_opensearch_serverless_collection"] = existing_opensearch_serverless_collection
        if existing_processed_assets_bucket_obj is not None:
            self._values["existing_processed_assets_bucket_obj"] = existing_processed_assets_bucket_obj
        if existing_security_group is not None:
            self._values["existing_security_group"] = existing_security_group
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if observability is not None:
            self._values["observability"] = observability
        if open_search_secret is not None:
            self._values["open_search_secret"] = open_search_secret
        if stage is not None:
            self._values["stage"] = stage
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def cognito_user_pool(self) -> _aws_cdk_aws_cognito_ceddda9d.IUserPool:
        '''(experimental) Cognito user pool used for authentication.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("cognito_user_pool")
        assert result is not None, "Required property 'cognito_user_pool' is missing"
        return typing.cast(_aws_cdk_aws_cognito_ceddda9d.IUserPool, result)

    @builtins.property
    def open_search_index_name(self) -> builtins.str:
        '''(experimental) Index name for the OpenSearch Service.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("open_search_index_name")
        assert result is not None, "Required property 'open_search_index_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bucket_inputs_assets_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps]:
        '''(experimental) Optional user provided props to override the default props for the S3 Bucket.

        Providing both this and ``existingInputAssetsBucketObj`` will cause an error.

        :default: - Default props are used

        :stability: experimental
        '''
        result = self._values.get("bucket_inputs_assets_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps], result)

    @builtins.property
    def bucket_processed_assets_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps]:
        '''(experimental) Optional user provided props to override the default props for the S3 Bucket.

        Providing both this and ``existingProcessedAssetsBucketObj`` will cause an error.

        :default: - Default props are used

        :stability: experimental
        '''
        result = self._values.get("bucket_processed_assets_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps], result)

    @builtins.property
    def enable_operational_metric(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Optional.CDK constructs provided collects anonymous operational metrics to help AWS improve the quality and features of the constructs. Data collection is subject to the AWS Privacy Policy (https://aws.amazon.com/privacy/). To opt out of this feature, simply disable it by setting the construct property "enableOperationalMetric" to false for each construct used.

        :default: - true

        :stability: experimental
        '''
        result = self._values.get("enable_operational_metric")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def existing_bus_interface(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus]:
        '''(experimental) Optional Existing instance of an EventBridge bus.

        If not provided, the construct will create one.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("existing_bus_interface")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus], result)

    @builtins.property
    def existing_input_assets_bucket_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''(experimental) Existing instance of S3 Bucket object, providing both this and ``bucketInputsAssetsProps`` will cause an error.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("existing_input_assets_bucket_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def existing_merged_api(
        self,
    ) -> typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi]:
        '''(experimental) Existing merged Appsync GraphQL api.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("existing_merged_api")
        return typing.cast(typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi], result)

    @builtins.property
    def existing_opensearch_domain(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IDomain]:
        '''(experimental) Optional existing Amazon OpenSearch Service domain.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("existing_opensearch_domain")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IDomain], result)

    @builtins.property
    def existing_opensearch_serverless_collection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchserverless_ceddda9d.CfnCollection]:
        '''(experimental) Optional existing Amazon Amazon OpenSearch Serverless collection.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("existing_opensearch_serverless_collection")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchserverless_ceddda9d.CfnCollection], result)

    @builtins.property
    def existing_processed_assets_bucket_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''(experimental) Existing instance of S3 Bucket object, providing both this and ``bucketProcessedAssetsProps`` will cause an error.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("existing_processed_assets_bucket_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def existing_security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''(experimental) Optional existing security group allowing access to opensearch.

        Used by the lambda functions
        built by this construct. If not provided, the construct will create one.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("existing_security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) Optional An existing VPC in which to deploy the construct.

        Providing both this and
        vpcProps is an error.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def observability(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable observability.

        Warning: associated cost with the services
        used. Best practice to enable by default.

        :default: - true

        :stability: experimental
        '''
        result = self._values.get("observability")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def open_search_secret(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        '''(experimental) Optional.

        SecretsManager secret to authenticate against the OpenSearch Service domain if
        domain is configured with Username/Password.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("open_search_secret")
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], result)

    @builtins.property
    def stage(self) -> typing.Optional[builtins.str]:
        '''(experimental) Value will be appended to resources name.

        :default: - _dev

        :stability: experimental
        '''
        result = self._values.get("stage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_props(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps]:
        '''(experimental) Optional custom properties for a VPC the construct will create.

        This VPC will
        be used by the Lambda functions the construct creates. Providing
        both this and existingVpc is an error.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RagAppsyncStepfnOpensearchProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SageMakerEndpointBase(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdklabs/generative-ai-cdk-constructs.SageMakerEndpointBase",
):
    '''
    :stability: experimental
    '''

    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''Creates a new construct node.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c37da07d50996bf3815df5522cdacee052c06fde9388dfbbfe2234481a961908)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @jsii.member(jsii_name="createSageMakerRole")
    def _create_sage_maker_role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.invoke(self, "createSageMakerRole", []))


class _SageMakerEndpointBaseProxy(SageMakerEndpointBase):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, SageMakerEndpointBase).__jsii_proxy_class__ = lambda : _SageMakerEndpointBaseProxy


class SageMakerInstanceType(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/generative-ai-cdk-constructs.SageMakerInstanceType",
):
    '''(experimental) Supported instance types for SageMaker instance-based production variants.

    :stability: experimental
    '''

    def __init__(self, instance_type: builtins.str) -> None:
        '''
        :param instance_type: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f06ce0cc4b08453b7ab410c78b48041f013a51e2dfa884a02fd5c6e2128fe4e0)
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
        jsii.create(self.__class__, self, [instance_type])

    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(cls, instance_type: builtins.str) -> "SageMakerInstanceType":
        '''(experimental) Builds an InstanceType from a given string or token (such as a CfnParameter).

        :param instance_type: An instance type as string.

        :return: A strongly typed InstanceType

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f58c993f4fbd1d7d4666ae23b06ee672f893b6774b448ab48869abff7e44114)
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
        return typing.cast("SageMakerInstanceType", jsii.sinvoke(cls, "of", [instance_type]))

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''(experimental) Return the instance type as a string.

        :return: The instance type as a string

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "toString", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C4_2XLARGE")
    def ML_C4_2_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c4.2xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C4_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C4_4XLARGE")
    def ML_C4_4_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c4.4xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C4_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C4_8XLARGE")
    def ML_C4_8_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c4.8xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C4_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C4_LARGE")
    def ML_C4_LARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c4.large.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C4_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C4_XLARGE")
    def ML_C4_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c4.xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C4_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5_18XLARGE")
    def ML_C5_18_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c5.18xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C5_18XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5_2XLARGE")
    def ML_C5_2_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c5.2xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C5_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5_4XLARGE")
    def ML_C5_4_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c5.4xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C5_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5_9XLARGE")
    def ML_C5_9_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c5.9xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C5_9XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5_LARGE")
    def ML_C5_LARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c5.large.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C5_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5_XLARGE")
    def ML_C5_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c5.xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C5_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5D_18XLARGE")
    def ML_C5_D_18_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c5d.18xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C5D_18XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5D_2XLARGE")
    def ML_C5_D_2_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c5d.2xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C5D_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5D_4XLARGE")
    def ML_C5_D_4_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c5d.4xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C5D_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5D_9XLARGE")
    def ML_C5_D_9_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c5d.9xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C5D_9XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5D_LARGE")
    def ML_C5_D_LARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c5d.large.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C5D_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5D_XLARGE")
    def ML_C5_D_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c5d.xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C5D_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_12XLARGE")
    def ML_C6_I_12_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c6i.12xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C6I_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_16XLARGE")
    def ML_C6_I_16_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c6i.16xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C6I_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_24XLARGE")
    def ML_C6_I_24_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c6i.24xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C6I_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_2XLARGE")
    def ML_C6_I_2_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c6i.2xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C6I_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_32XLARGE")
    def ML_C6_I_32_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c6i.32xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C6I_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_4XLARGE")
    def ML_C6_I_4_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c6i.4xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C6I_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_8XLARGE")
    def ML_C6_I_8_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c6i.8xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C6I_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_LARGE")
    def ML_C6_I_LARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c6i.large.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C6I_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_XLARGE")
    def ML_C6_I_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.c6i.xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_C6I_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G4DN_12XLARGE")
    def ML_G4_DN_12_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.g4dn.12xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_G4DN_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G4DN_16XLARGE")
    def ML_G4_DN_16_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.g4dn.16xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_G4DN_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G4DN_2XLARGE")
    def ML_G4_DN_2_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.g4dn.2xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_G4DN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G4DN_4XLARGE")
    def ML_G4_DN_4_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.g4dn.4xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_G4DN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G4DN_8XLARGE")
    def ML_G4_DN_8_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.g4dn.8xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_G4DN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G4DN_XLARGE")
    def ML_G4_DN_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.g4dn.xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_G4DN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G5_12XLARGE")
    def ML_G5_12_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.g5.12xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_G5_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G5_16XLARGE")
    def ML_G5_16_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.g5.16xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_G5_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G5_24XLARGE")
    def ML_G5_24_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.g5.24xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_G5_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G5_2XLARGE")
    def ML_G5_2_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.g5.2xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_G5_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G5_48XLARGE")
    def ML_G5_48_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.g5.48xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_G5_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G5_4XLARGE")
    def ML_G5_4_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.g5.4xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_G5_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G5_8XLARGE")
    def ML_G5_8_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.g5.8xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_G5_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G5_XLARGE")
    def ML_G5_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.g5.xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_G5_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_INF1_24XLARGE")
    def ML_INF1_24_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.inf1.24xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_INF1_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_INF1_2XLARGE")
    def ML_INF1_2_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.inf1.2xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_INF1_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_INF1_6XLARGE")
    def ML_INF1_6_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.inf1.6xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_INF1_6XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_INF1_XLARGE")
    def ML_INF1_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.inf1.xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_INF1_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_INF2_24XLARGE")
    def ML_INF2_24_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.inf2.24xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_INF2_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_INF2_48XLARGE")
    def ML_INF2_48_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.inf2.48xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_INF2_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_INF2_8XLARGE")
    def ML_INF2_8_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.inf2.8xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_INF2_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_INF2_XLARGE")
    def ML_INF2_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.inf2.xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_INF2_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M4_10XLARGE")
    def ML_M4_10_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.m4.10xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_M4_10XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M4_16XLARGE")
    def ML_M4_16_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.m4.16xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_M4_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M4_2XLARGE")
    def ML_M4_2_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.m4.2xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_M4_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M4_4XLARGE")
    def ML_M4_4_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.m4.4xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_M4_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M4_XLARGE")
    def ML_M4_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.m4.xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_M4_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5_12XLARGE")
    def ML_M5_12_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.m5.12xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_M5_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5_24XLARGE")
    def ML_M5_24_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.m5.24xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_M5_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5_2XLARGE")
    def ML_M5_2_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.m5.2xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_M5_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5_4XLARGE")
    def ML_M5_4_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.m5.4xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_M5_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5_LARGE")
    def ML_M5_LARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.m5.large.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_M5_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5_XLARGE")
    def ML_M5_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.m5.xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_M5_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5D_12XLARGE")
    def ML_M5_D_12_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.m5d.12xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_M5D_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5D_24XLARGE")
    def ML_M5_D_24_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.m5d.24xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_M5D_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5D_2XLARGE")
    def ML_M5_D_2_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.m5d.2xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_M5D_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5D_4XLARGE")
    def ML_M5_D_4_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.m5d.4xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_M5D_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5D_LARGE")
    def ML_M5_D_LARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.m5d.large.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_M5D_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5D_XLARGE")
    def ML_M5_D_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.m5d.xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_M5D_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_P2_16XLARGE")
    def ML_P2_16_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.p2.16xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_P2_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_P2_8XLARGE")
    def ML_P2_8_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.p2.8xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_P2_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_P2_XLARGE")
    def ML_P2_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.p2.xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_P2_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_P3_16XLARGE")
    def ML_P3_16_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.p3.16xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_P3_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_P3_2XLARGE")
    def ML_P3_2_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.p3.2xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_P3_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_P3_8XLARGE")
    def ML_P3_8_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.p3.8xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_P3_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_P4D_24XLARGE")
    def ML_P4_D_24_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.p4d.24xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_P4D_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5_12XLARGE")
    def ML_R5_12_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.r5.12xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_R5_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5_24XLARGE")
    def ML_R5_24_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.r5.24xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_R5_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5_2XLARGE")
    def ML_R5_2_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.r5.2xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_R5_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5_4XLARGE")
    def ML_R5_4_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.r5.4xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_R5_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5_LARGE")
    def ML_R5_LARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.r5.large.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_R5_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5_XLARGE")
    def ML_R5_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.r5.xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_R5_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5D_12XLARGE")
    def ML_R5_D_12_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.r5d.12xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_R5D_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5D_24XLARGE")
    def ML_R5_D_24_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.r5d.24xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_R5D_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5D_2XLARGE")
    def ML_R5_D_2_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.r5d.2xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_R5D_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5D_4XLARGE")
    def ML_R5_D_4_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.r5d.4xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_R5D_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5D_LARGE")
    def ML_R5_D_LARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.r5d.large.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_R5D_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5D_XLARGE")
    def ML_R5_D_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.r5d.xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_R5D_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_T2_2XLARGE")
    def ML_T2_2_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.t2.2xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_T2_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_T2_LARGE")
    def ML_T2_LARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.t2.large.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_T2_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_T2_MEDIUM")
    def ML_T2_MEDIUM(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.t2.medium.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_T2_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_T2_XLARGE")
    def ML_T2_XLARGE(cls) -> "SageMakerInstanceType":
        '''(experimental) ml.t2.xlarge.

        :stability: experimental
        '''
        return typing.cast("SageMakerInstanceType", jsii.sget(cls, "ML_T2_XLARGE"))


class SummarizationAppsyncStepfn(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/generative-ai-cdk-constructs.SummarizationAppsyncStepfn",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cognito_user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
        bucket_inputs_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        bucket_processed_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        cfn_cache_cluster_props: typing.Optional[typing.Union[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheClusterProps, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_operational_metric: typing.Optional[builtins.bool] = None,
        event_bus_props: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventBusProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        existing_input_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        existing_merged_api: typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi] = None,
        existing_processed_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        existing_redis_culster: typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster] = None,
        existing_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        is_file_transformation_required: typing.Optional[builtins.str] = None,
        observability: typing.Optional[builtins.bool] = None,
        stage: typing.Optional[builtins.str] = None,
        summary_api_name: typing.Optional[builtins.str] = None,
        summary_chain_type: typing.Optional[builtins.str] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param cognito_user_pool: (experimental) Required. Cognito user pool used for authentication. Default: - None
        :param bucket_inputs_assets_props: (experimental) Optional. User provided props to override the default props for the S3 Bucket. Providing both this and ``existingInputAssetsBucketObj`` will cause an error. Default: - Default props are used
        :param bucket_processed_assets_props: (experimental) Optional. User provided props to override the default props for the S3 Bucket. Providing both this and ``existingProcessedAssetsBucketObj`` will cause an error. Default: - Default props are used
        :param cfn_cache_cluster_props: (experimental) Optional. Custom cfnCacheClusterProps for Redis. Providing existingRedisCulster and cfnCacheClusterProps together will result in error. Default: numCacheNodes- 1
        :param enable_operational_metric: (experimental) Optional.CDK constructs provided collects anonymous operational metrics to help AWS improve the quality and features of the constructs. Data collection is subject to the AWS Privacy Policy (https://aws.amazon.com/privacy/). To opt out of this feature, simply disable it by setting the construct property "enableOperationalMetric" to false for each construct used. Default: - true
        :param event_bus_props: (experimental) Optional. A new custom EventBus is created with provided props. Providing existingEventBusInterface and eventBusProps both will result in validation error. Default: - None
        :param existing_bus_interface: (experimental) Optional. Existing instance of EventBus. The summary construct integrate appsync with event bridge' to route the request to step functions. Default: - None
        :param existing_input_assets_bucket_obj: (experimental) Optional. Existing s3 Bucket to store the input document which needs to be summarized. pdf is the supported input document format. If transformed (txt format) file is available then this bucket is optional. Default: - None
        :param existing_merged_api: (experimental) Optional - Existing merged Appsync GraphQL api. Default: - None
        :param existing_processed_assets_bucket_obj: (experimental) Optional. This bucket stores the transformed (txt) assets for generating summary. If None is provided then this contruct will create one. Default: - None
        :param existing_redis_culster: (experimental) Optional. Existing Redis cluster to cache the generated summary for subsequent request of same document. Default: - none
        :param existing_security_group: (experimental) Optional. Security group for the lambda function which this construct will use. If no exisiting security group is provided it will create one from the vpc. Default: - none
        :param existing_vpc: (experimental) Optional. An existing VPC can be used to deploy the construct. Providing both this and vpcProps is an error. Default: - none
        :param is_file_transformation_required: (experimental) Optional. The summary construct transform the input document into txt format. If the transformation is not required then this flag can be set to false. If set to true then a transformed asset bucket is created which transform the input document from input asset bucket to txt format. Default: - False
        :param observability: (experimental) Enable observability. Warning: associated cost with the services used. Best practice to enable by default. Default: - true
        :param stage: (experimental) Value will be appended to resources name. Default: - _dev
        :param summary_api_name: (experimental) Optional. User provided Name for summary api on appsync. A graphql api will be created by this construct with this name. Default: 'summaryApi'
        :param summary_chain_type: (experimental) Optional. Chain type defines how to pass the document to LLM. there are three types of chain types. Stuff: Simply "stuff" all your documents into a single prompt. Map-reduce: Summarize each document on it's own in a "map" step and then "reduce" the summaries into a final summary Refine : This constructs a response by looping over the input documents and iteratively updating its answer Default: - Stuff
        :param vpc_props: (experimental) Optional. The construct creates a custom VPC based on vpcProps. Providing both this and existingVpc is an error. Default: - none

        :stability: experimental
        :access: public
        :since: 0.0.0
        :summary: Constructs a new instance of the SummarizationAppsyncStepfn class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e3d8b9e643131ffd22e254e28d1be23095a03faa91dc469f13c16edf293c7af)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SummarizationAppsyncStepfnProps(
            cognito_user_pool=cognito_user_pool,
            bucket_inputs_assets_props=bucket_inputs_assets_props,
            bucket_processed_assets_props=bucket_processed_assets_props,
            cfn_cache_cluster_props=cfn_cache_cluster_props,
            enable_operational_metric=enable_operational_metric,
            event_bus_props=event_bus_props,
            existing_bus_interface=existing_bus_interface,
            existing_input_assets_bucket_obj=existing_input_assets_bucket_obj,
            existing_merged_api=existing_merged_api,
            existing_processed_assets_bucket_obj=existing_processed_assets_bucket_obj,
            existing_redis_culster=existing_redis_culster,
            existing_security_group=existing_security_group,
            existing_vpc=existing_vpc,
            is_file_transformation_required=is_file_transformation_required,
            observability=observability,
            stage=stage,
            summary_api_name=summary_api_name,
            summary_chain_type=summary_chain_type,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="eventBridgeBus")
    def event_bridge_bus(self) -> _aws_cdk_aws_events_ceddda9d.IEventBus:
        '''(experimental) Returns an instance of events.IEventBus created by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_events_ceddda9d.IEventBus, jsii.get(self, "eventBridgeBus"))

    @builtins.property
    @jsii.member(jsii_name="graphqlApi")
    def graphql_api(self) -> _aws_cdk_aws_appsync_ceddda9d.IGraphqlApi:
        '''(experimental) Returns an instance of appsync.CfnGraphQLApi for summary created by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_appsync_ceddda9d.IGraphqlApi, jsii.get(self, "graphqlApi"))

    @builtins.property
    @jsii.member(jsii_name="inputAssetBucket")
    def input_asset_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''(experimental) Returns the instance of s3.IBucket used by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "inputAssetBucket"))

    @builtins.property
    @jsii.member(jsii_name="processedAssetBucket")
    def processed_asset_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''(experimental) Returns the instance of s3.IBucket used by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "processedAssetBucket"))

    @builtins.property
    @jsii.member(jsii_name="redisCluster")
    def redis_cluster(self) -> _aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster:
        '''(experimental) Returns an instance of redis cluster created by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster, jsii.get(self, "redisCluster"))

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        '''(experimental) Returns the instance of ec2.ISecurityGroup used by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup, jsii.get(self, "securityGroup"))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''(experimental) Step function.

        :default: - fieldLogLevel - None

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.get(self, "stateMachine"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) Returns the instance of ec2.IVpc used by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@cdklabs/generative-ai-cdk-constructs.SummarizationAppsyncStepfnProps",
    jsii_struct_bases=[],
    name_mapping={
        "cognito_user_pool": "cognitoUserPool",
        "bucket_inputs_assets_props": "bucketInputsAssetsProps",
        "bucket_processed_assets_props": "bucketProcessedAssetsProps",
        "cfn_cache_cluster_props": "cfnCacheClusterProps",
        "enable_operational_metric": "enableOperationalMetric",
        "event_bus_props": "eventBusProps",
        "existing_bus_interface": "existingBusInterface",
        "existing_input_assets_bucket_obj": "existingInputAssetsBucketObj",
        "existing_merged_api": "existingMergedApi",
        "existing_processed_assets_bucket_obj": "existingProcessedAssetsBucketObj",
        "existing_redis_culster": "existingRedisCulster",
        "existing_security_group": "existingSecurityGroup",
        "existing_vpc": "existingVpc",
        "is_file_transformation_required": "isFileTransformationRequired",
        "observability": "observability",
        "stage": "stage",
        "summary_api_name": "summaryApiName",
        "summary_chain_type": "summaryChainType",
        "vpc_props": "vpcProps",
    },
)
class SummarizationAppsyncStepfnProps:
    def __init__(
        self,
        *,
        cognito_user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
        bucket_inputs_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        bucket_processed_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        cfn_cache_cluster_props: typing.Optional[typing.Union[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheClusterProps, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_operational_metric: typing.Optional[builtins.bool] = None,
        event_bus_props: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventBusProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        existing_input_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        existing_merged_api: typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi] = None,
        existing_processed_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        existing_redis_culster: typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster] = None,
        existing_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        is_file_transformation_required: typing.Optional[builtins.str] = None,
        observability: typing.Optional[builtins.bool] = None,
        stage: typing.Optional[builtins.str] = None,
        summary_api_name: typing.Optional[builtins.str] = None,
        summary_chain_type: typing.Optional[builtins.str] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param cognito_user_pool: (experimental) Required. Cognito user pool used for authentication. Default: - None
        :param bucket_inputs_assets_props: (experimental) Optional. User provided props to override the default props for the S3 Bucket. Providing both this and ``existingInputAssetsBucketObj`` will cause an error. Default: - Default props are used
        :param bucket_processed_assets_props: (experimental) Optional. User provided props to override the default props for the S3 Bucket. Providing both this and ``existingProcessedAssetsBucketObj`` will cause an error. Default: - Default props are used
        :param cfn_cache_cluster_props: (experimental) Optional. Custom cfnCacheClusterProps for Redis. Providing existingRedisCulster and cfnCacheClusterProps together will result in error. Default: numCacheNodes- 1
        :param enable_operational_metric: (experimental) Optional.CDK constructs provided collects anonymous operational metrics to help AWS improve the quality and features of the constructs. Data collection is subject to the AWS Privacy Policy (https://aws.amazon.com/privacy/). To opt out of this feature, simply disable it by setting the construct property "enableOperationalMetric" to false for each construct used. Default: - true
        :param event_bus_props: (experimental) Optional. A new custom EventBus is created with provided props. Providing existingEventBusInterface and eventBusProps both will result in validation error. Default: - None
        :param existing_bus_interface: (experimental) Optional. Existing instance of EventBus. The summary construct integrate appsync with event bridge' to route the request to step functions. Default: - None
        :param existing_input_assets_bucket_obj: (experimental) Optional. Existing s3 Bucket to store the input document which needs to be summarized. pdf is the supported input document format. If transformed (txt format) file is available then this bucket is optional. Default: - None
        :param existing_merged_api: (experimental) Optional - Existing merged Appsync GraphQL api. Default: - None
        :param existing_processed_assets_bucket_obj: (experimental) Optional. This bucket stores the transformed (txt) assets for generating summary. If None is provided then this contruct will create one. Default: - None
        :param existing_redis_culster: (experimental) Optional. Existing Redis cluster to cache the generated summary for subsequent request of same document. Default: - none
        :param existing_security_group: (experimental) Optional. Security group for the lambda function which this construct will use. If no exisiting security group is provided it will create one from the vpc. Default: - none
        :param existing_vpc: (experimental) Optional. An existing VPC can be used to deploy the construct. Providing both this and vpcProps is an error. Default: - none
        :param is_file_transformation_required: (experimental) Optional. The summary construct transform the input document into txt format. If the transformation is not required then this flag can be set to false. If set to true then a transformed asset bucket is created which transform the input document from input asset bucket to txt format. Default: - False
        :param observability: (experimental) Enable observability. Warning: associated cost with the services used. Best practice to enable by default. Default: - true
        :param stage: (experimental) Value will be appended to resources name. Default: - _dev
        :param summary_api_name: (experimental) Optional. User provided Name for summary api on appsync. A graphql api will be created by this construct with this name. Default: 'summaryApi'
        :param summary_chain_type: (experimental) Optional. Chain type defines how to pass the document to LLM. there are three types of chain types. Stuff: Simply "stuff" all your documents into a single prompt. Map-reduce: Summarize each document on it's own in a "map" step and then "reduce" the summaries into a final summary Refine : This constructs a response by looping over the input documents and iteratively updating its answer Default: - Stuff
        :param vpc_props: (experimental) Optional. The construct creates a custom VPC based on vpcProps. Providing both this and existingVpc is an error. Default: - none

        :stability: experimental
        '''
        if isinstance(bucket_inputs_assets_props, dict):
            bucket_inputs_assets_props = _aws_cdk_aws_s3_ceddda9d.BucketProps(**bucket_inputs_assets_props)
        if isinstance(bucket_processed_assets_props, dict):
            bucket_processed_assets_props = _aws_cdk_aws_s3_ceddda9d.BucketProps(**bucket_processed_assets_props)
        if isinstance(cfn_cache_cluster_props, dict):
            cfn_cache_cluster_props = _aws_cdk_aws_elasticache_ceddda9d.CfnCacheClusterProps(**cfn_cache_cluster_props)
        if isinstance(event_bus_props, dict):
            event_bus_props = _aws_cdk_aws_events_ceddda9d.EventBusProps(**event_bus_props)
        if isinstance(vpc_props, dict):
            vpc_props = _aws_cdk_aws_ec2_ceddda9d.VpcProps(**vpc_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c70798ec1d57933ac8ff9b3e4952de2c9f173958f717d396052ee110b0045bc)
            check_type(argname="argument cognito_user_pool", value=cognito_user_pool, expected_type=type_hints["cognito_user_pool"])
            check_type(argname="argument bucket_inputs_assets_props", value=bucket_inputs_assets_props, expected_type=type_hints["bucket_inputs_assets_props"])
            check_type(argname="argument bucket_processed_assets_props", value=bucket_processed_assets_props, expected_type=type_hints["bucket_processed_assets_props"])
            check_type(argname="argument cfn_cache_cluster_props", value=cfn_cache_cluster_props, expected_type=type_hints["cfn_cache_cluster_props"])
            check_type(argname="argument enable_operational_metric", value=enable_operational_metric, expected_type=type_hints["enable_operational_metric"])
            check_type(argname="argument event_bus_props", value=event_bus_props, expected_type=type_hints["event_bus_props"])
            check_type(argname="argument existing_bus_interface", value=existing_bus_interface, expected_type=type_hints["existing_bus_interface"])
            check_type(argname="argument existing_input_assets_bucket_obj", value=existing_input_assets_bucket_obj, expected_type=type_hints["existing_input_assets_bucket_obj"])
            check_type(argname="argument existing_merged_api", value=existing_merged_api, expected_type=type_hints["existing_merged_api"])
            check_type(argname="argument existing_processed_assets_bucket_obj", value=existing_processed_assets_bucket_obj, expected_type=type_hints["existing_processed_assets_bucket_obj"])
            check_type(argname="argument existing_redis_culster", value=existing_redis_culster, expected_type=type_hints["existing_redis_culster"])
            check_type(argname="argument existing_security_group", value=existing_security_group, expected_type=type_hints["existing_security_group"])
            check_type(argname="argument existing_vpc", value=existing_vpc, expected_type=type_hints["existing_vpc"])
            check_type(argname="argument is_file_transformation_required", value=is_file_transformation_required, expected_type=type_hints["is_file_transformation_required"])
            check_type(argname="argument observability", value=observability, expected_type=type_hints["observability"])
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
            check_type(argname="argument summary_api_name", value=summary_api_name, expected_type=type_hints["summary_api_name"])
            check_type(argname="argument summary_chain_type", value=summary_chain_type, expected_type=type_hints["summary_chain_type"])
            check_type(argname="argument vpc_props", value=vpc_props, expected_type=type_hints["vpc_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cognito_user_pool": cognito_user_pool,
        }
        if bucket_inputs_assets_props is not None:
            self._values["bucket_inputs_assets_props"] = bucket_inputs_assets_props
        if bucket_processed_assets_props is not None:
            self._values["bucket_processed_assets_props"] = bucket_processed_assets_props
        if cfn_cache_cluster_props is not None:
            self._values["cfn_cache_cluster_props"] = cfn_cache_cluster_props
        if enable_operational_metric is not None:
            self._values["enable_operational_metric"] = enable_operational_metric
        if event_bus_props is not None:
            self._values["event_bus_props"] = event_bus_props
        if existing_bus_interface is not None:
            self._values["existing_bus_interface"] = existing_bus_interface
        if existing_input_assets_bucket_obj is not None:
            self._values["existing_input_assets_bucket_obj"] = existing_input_assets_bucket_obj
        if existing_merged_api is not None:
            self._values["existing_merged_api"] = existing_merged_api
        if existing_processed_assets_bucket_obj is not None:
            self._values["existing_processed_assets_bucket_obj"] = existing_processed_assets_bucket_obj
        if existing_redis_culster is not None:
            self._values["existing_redis_culster"] = existing_redis_culster
        if existing_security_group is not None:
            self._values["existing_security_group"] = existing_security_group
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if is_file_transformation_required is not None:
            self._values["is_file_transformation_required"] = is_file_transformation_required
        if observability is not None:
            self._values["observability"] = observability
        if stage is not None:
            self._values["stage"] = stage
        if summary_api_name is not None:
            self._values["summary_api_name"] = summary_api_name
        if summary_chain_type is not None:
            self._values["summary_chain_type"] = summary_chain_type
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def cognito_user_pool(self) -> _aws_cdk_aws_cognito_ceddda9d.IUserPool:
        '''(experimental) Required.

        Cognito user pool used for authentication.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("cognito_user_pool")
        assert result is not None, "Required property 'cognito_user_pool' is missing"
        return typing.cast(_aws_cdk_aws_cognito_ceddda9d.IUserPool, result)

    @builtins.property
    def bucket_inputs_assets_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps]:
        '''(experimental) Optional.

        User provided props to override the default props for the S3 Bucket.
        Providing both this and ``existingInputAssetsBucketObj`` will cause an error.

        :default: - Default props are used

        :stability: experimental
        '''
        result = self._values.get("bucket_inputs_assets_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps], result)

    @builtins.property
    def bucket_processed_assets_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps]:
        '''(experimental) Optional.

        User provided props to override the default props for the S3 Bucket.
        Providing both this and ``existingProcessedAssetsBucketObj`` will cause an error.

        :default: - Default props are used

        :stability: experimental
        '''
        result = self._values.get("bucket_processed_assets_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps], result)

    @builtins.property
    def cfn_cache_cluster_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheClusterProps]:
        '''(experimental) Optional.

        Custom cfnCacheClusterProps for Redis.
        Providing existingRedisCulster and cfnCacheClusterProps together will result in error.

        :default: numCacheNodes- 1

        :stability: experimental
        '''
        result = self._values.get("cfn_cache_cluster_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheClusterProps], result)

    @builtins.property
    def enable_operational_metric(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Optional.CDK constructs provided collects anonymous operational metrics to help AWS improve the quality and features of the constructs. Data collection is subject to the AWS Privacy Policy (https://aws.amazon.com/privacy/). To opt out of this feature, simply disable it by setting the construct property "enableOperationalMetric" to false for each construct used.

        :default: - true

        :stability: experimental
        '''
        result = self._values.get("enable_operational_metric")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def event_bus_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventBusProps]:
        '''(experimental) Optional.

        A new custom EventBus is created with provided props.
        Providing existingEventBusInterface and eventBusProps both will result in validation error.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("event_bus_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.EventBusProps], result)

    @builtins.property
    def existing_bus_interface(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus]:
        '''(experimental) Optional.

        Existing instance of EventBus. The summary construct integrate appsync with event bridge'
        to route the request to step functions.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("existing_bus_interface")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus], result)

    @builtins.property
    def existing_input_assets_bucket_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''(experimental) Optional.

        Existing s3 Bucket to store the input document which needs to be summarized.
        pdf is the supported input document format. If transformed (txt format) file is
        available then this bucket is optional.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("existing_input_assets_bucket_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def existing_merged_api(
        self,
    ) -> typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi]:
        '''(experimental) Optional - Existing merged Appsync GraphQL api.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("existing_merged_api")
        return typing.cast(typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi], result)

    @builtins.property
    def existing_processed_assets_bucket_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''(experimental) Optional.

        This bucket stores the transformed (txt) assets for generating summary.
        If None is provided then this contruct will create one.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("existing_processed_assets_bucket_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def existing_redis_culster(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster]:
        '''(experimental) Optional.

        Existing Redis cluster to cache the generated summary
        for subsequent request of same document.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("existing_redis_culster")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster], result)

    @builtins.property
    def existing_security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''(experimental) Optional.

        Security group for the lambda function which this construct will use.
        If no exisiting security group is provided it will create one from the vpc.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("existing_security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) Optional.

        An existing VPC can be used to deploy the construct.
        Providing both this and vpcProps is an error.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def is_file_transformation_required(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional.

        The summary construct transform the input document into txt format. If the
        transformation is not required then this flag can be set to false. If set to true
        then a transformed asset bucket is created which transform the input document from
        input asset bucket to txt format.

        :default: - False

        :stability: experimental
        '''
        result = self._values.get("is_file_transformation_required")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def observability(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable observability.

        Warning: associated cost with the services
        used. Best practice to enable by default.

        :default: - true

        :stability: experimental
        '''
        result = self._values.get("observability")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stage(self) -> typing.Optional[builtins.str]:
        '''(experimental) Value will be appended to resources name.

        :default: - _dev

        :stability: experimental
        '''
        result = self._values.get("stage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def summary_api_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional.

        User provided Name for summary api on appsync.
        A graphql api will be created by this construct with this name.

        :default: 'summaryApi'

        :stability: experimental
        '''
        result = self._values.get("summary_api_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def summary_chain_type(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional.

        Chain type defines how to pass the document to LLM.
        there are three types of chain types.
        Stuff: Simply "stuff" all your documents into a single prompt.
        Map-reduce: Summarize each document on it's own in a "map" step and then "reduce" the summaries into a final summary
        Refine :  This constructs a response by looping over the input documents and iteratively updating its answer

        :default: - Stuff

        :stability: experimental
        '''
        result = self._values.get("summary_chain_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_props(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps]:
        '''(experimental) Optional.

        The construct creates a custom VPC based on vpcProps.
        Providing both this and existingVpc is an error.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SummarizationAppsyncStepfnProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_aws_iam_ceddda9d.IGrantable)
class CustomSageMakerEndpoint(
    SageMakerEndpointBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/generative-ai-cdk-constructs.CustomSageMakerEndpoint",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        container: ContainerImage,
        endpoint_name: builtins.str,
        instance_type: SageMakerInstanceType,
        model_data_url: builtins.str,
        model_id: builtins.str,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        instance_count: typing.Optional[jsii.Number] = None,
        model_data_download_timeout_in_seconds: typing.Optional[jsii.Number] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
        startup_health_check_timeout_in_seconds: typing.Optional[jsii.Number] = None,
        volume_size_in_gb: typing.Optional[jsii.Number] = None,
        vpc_config: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param container: 
        :param endpoint_name: 
        :param instance_type: 
        :param model_data_url: 
        :param model_id: 
        :param environment: 
        :param instance_count: 
        :param model_data_download_timeout_in_seconds: 
        :param role: 
        :param startup_health_check_timeout_in_seconds: 
        :param volume_size_in_gb: 
        :param vpc_config: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__989752ca25fc9932b1bdd01340b7988a6d08041c857f9f2b8919b0eda68523b3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CustomSageMakerEndpointProps(
            container=container,
            endpoint_name=endpoint_name,
            instance_type=instance_type,
            model_data_url=model_data_url,
            model_id=model_id,
            environment=environment,
            instance_count=instance_count,
            model_data_download_timeout_in_seconds=model_data_download_timeout_in_seconds,
            role=role,
            startup_health_check_timeout_in_seconds=startup_health_check_timeout_in_seconds,
            volume_size_in_gb=volume_size_in_gb,
            vpc_config=vpc_config,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> None:
        '''
        :param statement: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd1caa527c73cfa2f0cb7fc16dbd9f3c0bd1763ef673bb797faf1f432635f1be)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(None, jsii.invoke(self, "addToRolePolicy", [statement]))

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3440cb6fc8022809464d5c8edf0a71c987b3b0c52761c58076f71a7e8f20a5da)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantInvoke", [grantee]))

    @builtins.property
    @jsii.member(jsii_name="cfnEndpoint")
    def cfn_endpoint(self) -> _aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint, jsii.get(self, "cfnEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="cfnEndpointConfig")
    def cfn_endpoint_config(self) -> _aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfig:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfig, jsii.get(self, "cfnEndpointConfig"))

    @builtins.property
    @jsii.member(jsii_name="cfnModel")
    def cfn_model(self) -> _aws_cdk_aws_sagemaker_ceddda9d.CfnModel:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sagemaker_ceddda9d.CfnModel, jsii.get(self, "cfnModel"))

    @builtins.property
    @jsii.member(jsii_name="endpointArn")
    def endpoint_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "endpointArn"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="instanceCount")
    def instance_count(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "instanceCount"))

    @builtins.property
    @jsii.member(jsii_name="modelDataDownloadTimeoutInSeconds")
    def model_data_download_timeout_in_seconds(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "modelDataDownloadTimeoutInSeconds"))

    @builtins.property
    @jsii.member(jsii_name="modelDataUrl")
    def model_data_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "modelDataUrl"))

    @builtins.property
    @jsii.member(jsii_name="modelId")
    def model_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "modelId"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> typing.Optional[SageMakerInstanceType]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[SageMakerInstanceType], jsii.get(self, "instanceType"))

    @builtins.property
    @jsii.member(jsii_name="volumeSizeInGb")
    def volume_size_in_gb(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "volumeSizeInGb"))


@jsii.implements(_aws_cdk_aws_iam_ceddda9d.IGrantable)
class HuggingFaceSageMakerEndpoint(
    SageMakerEndpointBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/generative-ai-cdk-constructs.HuggingFaceSageMakerEndpoint",
):
    '''
    :stability: experimental
    :summary: The HuggingFaceSageMakerEndpoint class.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        container: ContainerImage,
        instance_type: SageMakerInstanceType,
        model_id: builtins.str,
        endpoint_name: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        instance_count: typing.Optional[jsii.Number] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
        startup_health_check_timeout_in_seconds: typing.Optional[jsii.Number] = None,
        vpc_config: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param container: 
        :param instance_type: 
        :param model_id: 
        :param endpoint_name: 
        :param environment: 
        :param instance_count: 
        :param role: 
        :param startup_health_check_timeout_in_seconds: 
        :param vpc_config: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38086469e018e34a8d8b00c156063e690e17f2bf4c037abc9cac1be2b89ea99b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = HuggingFaceSageMakerEndpointProps(
            container=container,
            instance_type=instance_type,
            model_id=model_id,
            endpoint_name=endpoint_name,
            environment=environment,
            instance_count=instance_count,
            role=role,
            startup_health_check_timeout_in_seconds=startup_health_check_timeout_in_seconds,
            vpc_config=vpc_config,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> None:
        '''
        :param statement: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f884fddb56b07302085c01964f7da04278b8808e0f8978b47ee3fa780e1a00a9)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(None, jsii.invoke(self, "addToRolePolicy", [statement]))

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b75f76f86752e358a0164022cc8101b42b03ff1b6cc0fcbea0553348d99ff27)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantInvoke", [grantee]))

    @builtins.property
    @jsii.member(jsii_name="cfnEndpoint")
    def cfn_endpoint(self) -> _aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint, jsii.get(self, "cfnEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="cfnEndpointConfig")
    def cfn_endpoint_config(self) -> _aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfig:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfig, jsii.get(self, "cfnEndpointConfig"))

    @builtins.property
    @jsii.member(jsii_name="cfnModel")
    def cfn_model(self) -> _aws_cdk_aws_sagemaker_ceddda9d.CfnModel:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sagemaker_ceddda9d.CfnModel, jsii.get(self, "cfnModel"))

    @builtins.property
    @jsii.member(jsii_name="endpointArn")
    def endpoint_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "endpointArn"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="instanceCount")
    def instance_count(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "instanceCount"))

    @builtins.property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> SageMakerInstanceType:
        '''
        :stability: experimental
        '''
        return typing.cast(SageMakerInstanceType, jsii.get(self, "instanceType"))

    @builtins.property
    @jsii.member(jsii_name="modelId")
    def model_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "modelId"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "role"))


class JumpStartSageMakerEndpoint(
    SageMakerEndpointBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/generative-ai-cdk-constructs.JumpStartSageMakerEndpoint",
):
    '''
    :stability: experimental
    :summary: The JumpStartSageMakerEndpoint class.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        model: JumpStartModel,
        endpoint_name: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        instance_count: typing.Optional[jsii.Number] = None,
        instance_type: typing.Optional[SageMakerInstanceType] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
        startup_health_check_timeout_in_seconds: typing.Optional[jsii.Number] = None,
        vpc_config: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param model: 
        :param endpoint_name: 
        :param environment: 
        :param instance_count: 
        :param instance_type: 
        :param role: 
        :param startup_health_check_timeout_in_seconds: 
        :param vpc_config: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__014e5d72b7decc2a5275975908d20bc2e6428f93ab52b954050e305acb50ccf5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = JumpStartSageMakerEndpointProps(
            model=model,
            endpoint_name=endpoint_name,
            environment=environment,
            instance_count=instance_count,
            instance_type=instance_type,
            role=role,
            startup_health_check_timeout_in_seconds=startup_health_check_timeout_in_seconds,
            vpc_config=vpc_config,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> None:
        '''
        :param statement: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba9c5b6fe6b83af0ad5f9138e4c4257b8c37463d898276834c309ec9d22b3eb2)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(None, jsii.invoke(self, "addToRolePolicy", [statement]))

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a86bb20d33d314b3762c600becde03bdc2caa6db40a8f0e9f3057e11a53a9bac)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantInvoke", [grantee]))

    @builtins.property
    @jsii.member(jsii_name="cfnEndpoint")
    def cfn_endpoint(self) -> _aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint, jsii.get(self, "cfnEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="cfnEndpointConfig")
    def cfn_endpoint_config(self) -> _aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfig:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfig, jsii.get(self, "cfnEndpointConfig"))

    @builtins.property
    @jsii.member(jsii_name="cfnModel")
    def cfn_model(self) -> _aws_cdk_aws_sagemaker_ceddda9d.CfnModel:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sagemaker_ceddda9d.CfnModel, jsii.get(self, "cfnModel"))

    @builtins.property
    @jsii.member(jsii_name="endpointArn")
    def endpoint_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "endpointArn"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="instanceCount")
    def instance_count(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "instanceCount"))

    @builtins.property
    @jsii.member(jsii_name="model")
    def model(self) -> JumpStartModel:
        '''
        :stability: experimental
        '''
        return typing.cast(JumpStartModel, jsii.get(self, "model"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> typing.Optional[SageMakerInstanceType]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[SageMakerInstanceType], jsii.get(self, "instanceType"))


@jsii.data_type(
    jsii_type="@cdklabs/generative-ai-cdk-constructs.LangchainLayerProps",
    jsii_struct_bases=[LangchainProps],
    name_mapping={
        "description": "description",
        "layer_version_name": "layerVersionName",
        "license": "license",
        "removal_policy": "removalPolicy",
        "architecture": "architecture",
        "runtime": "runtime",
        "additional_packages": "additionalPackages",
        "auto_upgrade": "autoUpgrade",
        "local": "local",
    },
)
class LangchainLayerProps(LangchainProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        layer_version_name: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        architecture: _aws_cdk_aws_lambda_ceddda9d.Architecture,
        runtime: _aws_cdk_aws_lambda_ceddda9d.Runtime,
        additional_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        auto_upgrade: typing.Optional[builtins.bool] = None,
        local: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) The properties for the LangchainLayerProps class.

        :param description: The description the this Lambda Layer. Default: - No description.
        :param layer_version_name: The name of the layer. Default: - A name will be generated.
        :param license: The SPDX licence identifier or URL to the license file for this layer. Default: - No license information will be recorded.
        :param removal_policy: Whether to retain this version of the layer when a new version is added or when the stack is deleted. Default: RemovalPolicy.DESTROY
        :param architecture: (experimental) Required. Lambda function architecture compatible with this Layer.
        :param runtime: (experimental) Required. Lambda function runtime compatible with this Layer.
        :param additional_packages: (experimental) A prop allowing additional python pip libraries to be installed with this langchain layer. Default: - none
        :param auto_upgrade: (experimental) Optional: Add '--upgrade' to pip install requirements.txt In case of a LangchainCommonLayer, this parameter is not used. Default: - false
        :param local: (experimental) Optional: Local compute will be used when installing requirements.txt. By default, a docker container will be spun up to install requirements. To override this behavior, use the python alias string of ``python`` or ``python3`` The string value will be the python alias used to install requirements. Default: - none

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3537d2f8bfb6093f936a7883eb70fc78008cb2c2a19e21a76265ec13de0f315)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument layer_version_name", value=layer_version_name, expected_type=type_hints["layer_version_name"])
            check_type(argname="argument license", value=license, expected_type=type_hints["license"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument architecture", value=architecture, expected_type=type_hints["architecture"])
            check_type(argname="argument runtime", value=runtime, expected_type=type_hints["runtime"])
            check_type(argname="argument additional_packages", value=additional_packages, expected_type=type_hints["additional_packages"])
            check_type(argname="argument auto_upgrade", value=auto_upgrade, expected_type=type_hints["auto_upgrade"])
            check_type(argname="argument local", value=local, expected_type=type_hints["local"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "architecture": architecture,
            "runtime": runtime,
        }
        if description is not None:
            self._values["description"] = description
        if layer_version_name is not None:
            self._values["layer_version_name"] = layer_version_name
        if license is not None:
            self._values["license"] = license
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if additional_packages is not None:
            self._values["additional_packages"] = additional_packages
        if auto_upgrade is not None:
            self._values["auto_upgrade"] = auto_upgrade
        if local is not None:
            self._values["local"] = local

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description the this Lambda Layer.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def layer_version_name(self) -> typing.Optional[builtins.str]:
        '''The name of the layer.

        :default: - A name will be generated.
        '''
        result = self._values.get("layer_version_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''The SPDX licence identifier or URL to the license file for this layer.

        :default: - No license information will be recorded.
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Whether to retain this version of the layer when a new version is added or when the stack is deleted.

        :default: RemovalPolicy.DESTROY
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def architecture(self) -> _aws_cdk_aws_lambda_ceddda9d.Architecture:
        '''(experimental) Required.

        Lambda function architecture compatible with this Layer.

        :stability: experimental
        '''
        result = self._values.get("architecture")
        assert result is not None, "Required property 'architecture' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Architecture, result)

    @builtins.property
    def runtime(self) -> _aws_cdk_aws_lambda_ceddda9d.Runtime:
        '''(experimental) Required.

        Lambda function runtime compatible with this Layer.

        :stability: experimental
        '''
        result = self._values.get("runtime")
        assert result is not None, "Required property 'runtime' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Runtime, result)

    @builtins.property
    def additional_packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A prop allowing additional python pip libraries to be installed with this langchain layer.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("additional_packages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def auto_upgrade(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Optional: Add '--upgrade' to pip install requirements.txt In case of a LangchainCommonLayer, this parameter is not used.

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("auto_upgrade")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def local(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional: Local compute will be used when installing requirements.txt. By default, a docker container will be spun up to install requirements. To override this behavior, use the python alias string of ``python`` or ``python3`` The string value will be the python alias used to install requirements.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("local")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LangchainLayerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AdapterProps",
    "ContainerImage",
    "ContainerImageConfig",
    "CustomSageMakerEndpoint",
    "CustomSageMakerEndpointProps",
    "DeepLearningContainerImage",
    "HuggingFaceSageMakerEndpoint",
    "HuggingFaceSageMakerEndpointProps",
    "IInstanceAliase",
    "IInstanceValiant",
    "IJumpStartModelSpec",
    "JumpStartModel",
    "JumpStartSageMakerEndpoint",
    "JumpStartSageMakerEndpointProps",
    "LangchainCommonDepsLayer",
    "LangchainCommonLayer",
    "LangchainLayerProps",
    "LangchainProps",
    "QaAppsyncOpensearch",
    "QaAppsyncOpensearchProps",
    "RagAppsyncStepfnOpensearch",
    "RagAppsyncStepfnOpensearchProps",
    "SageMakerEndpointBase",
    "SageMakerInstanceType",
    "SummarizationAppsyncStepfn",
    "SummarizationAppsyncStepfnProps",
    "bedrock",
    "opensearch_vectorindex",
    "opensearchserverless",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import bedrock
from . import opensearch_vectorindex
from . import opensearchserverless

def _typecheckingstub__14940da981f24c52deaeac165bd230136ed11f0570a4f7e7b9cb9ce527771c1e(
    *,
    compatible_architectures: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.Architecture]] = None,
    compatible_runtimes: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.Runtime]] = None,
    description: typing.Optional[builtins.str] = None,
    layer_version_name: typing.Optional[builtins.str] = None,
    license: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25f8364678c63568f662d1c08defb90957a4a2e7d3066311040cba2e3735b2fd(
    directory: builtins.str,
    *,
    asset_name: typing.Optional[builtins.str] = None,
    build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    build_secrets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    build_ssh: typing.Optional[builtins.str] = None,
    cache_from: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecr_assets_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]]] = None,
    cache_to: typing.Optional[typing.Union[_aws_cdk_aws_ecr_assets_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]] = None,
    file: typing.Optional[builtins.str] = None,
    invalidation: typing.Optional[typing.Union[_aws_cdk_aws_ecr_assets_ceddda9d.DockerImageAssetInvalidationOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    network_mode: typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.NetworkMode] = None,
    outputs: typing.Optional[typing.Sequence[builtins.str]] = None,
    platform: typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.Platform] = None,
    target: typing.Optional[builtins.str] = None,
    extra_hash: typing.Optional[builtins.str] = None,
    exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
    follow_symlinks: typing.Optional[_aws_cdk_ceddda9d.SymlinkFollowMode] = None,
    ignore_mode: typing.Optional[_aws_cdk_ceddda9d.IgnoreMode] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d56d3018c15bc3c527de6fcfbab1fce78287d4b4a491912aa644b5edbd8864e(
    repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
    tag: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98ebe648e608c12c055bbce76a5856ab8c5494b3267f8d897e31136265e41508(
    scope: _constructs_77d1e7e8.Construct,
    grantable: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93de8836b2699c5ff29ea91bd61ddf2d833937fcf645c73a50bfb8c03c3b01e4(
    *,
    image_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64c88e4b8c433fb64fc5ff7b8ba1dfe89b0e7d556fee70434f79fe2f29d94734(
    *,
    container: ContainerImage,
    endpoint_name: builtins.str,
    instance_type: SageMakerInstanceType,
    model_data_url: builtins.str,
    model_id: builtins.str,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    instance_count: typing.Optional[jsii.Number] = None,
    model_data_download_timeout_in_seconds: typing.Optional[jsii.Number] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    startup_health_check_timeout_in_seconds: typing.Optional[jsii.Number] = None,
    volume_size_in_gb: typing.Optional[jsii.Number] = None,
    vpc_config: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d3668d1403c78d9ca09200041cb872341727345f79173e3de3ec628c79a40d2(
    repository_name: builtins.str,
    tag: builtins.str,
    account_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ee4748a769dcb340a4537378546c2adacf2d41a2735729450c9cc171a8ae1af(
    repository_name: builtins.str,
    tag: builtins.str,
    account_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61d694cb21f225b8854128d356326406cf367ffbc30d0b508a85ebb3ea487f8f(
    scope: _constructs_77d1e7e8.Construct,
    grantable: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9abbb731cf44967a6628e353d6c56d0035755b62bf45acdaa8261b4c5048d1f9(
    *,
    container: ContainerImage,
    instance_type: SageMakerInstanceType,
    model_id: builtins.str,
    endpoint_name: typing.Optional[builtins.str] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    instance_count: typing.Optional[jsii.Number] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    startup_health_check_timeout_in_seconds: typing.Optional[jsii.Number] = None,
    vpc_config: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5f72a06047d6784d819d9905a60d528d3adf1757fd113a494d1e278ff756cc0(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09be534ff54d13743d68fbae01a7a6206246397b640b98663316222b3582760e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__784c92c851a2dedf6e80ea471cde9f9490de2aa6021222c9354e77dce1375a9c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bd10265f2863a8642df6187149bcdb3e5b8d4d4a701e3c0f81e180f79133355(
    value: typing.Optional[typing.Mapping[builtins.str, builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5208b4cb02ff50a0ebbf048c64aae565c2966812ac05c66bd93c7b3c84aa63ca(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a5a0c622f349e4bb3c898657c97ff2fd43f2f1ae081b59b80a923854e9a513f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2073cfea003f3e88c802dd137c85fd6e32f9da1475fd6187a6f87ace6a655672(
    value: typing.Mapping[builtins.str, typing.Union[builtins.str, jsii.Number, builtins.bool]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aef2d73f0172f5d063f633b101b7066b0fbe43a8824831786cf98be28ecd7f30(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0aa0d5de10cb8693f8f2a7f933f95ad652052122b9c5fbb256a6a6eb62687607(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__230bf6b942aecadf2cddb2400e4b8fa93d7b5324764d21f3c3745c62d2c05093(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e18f266234ad99daa9e9e8bc62ef14e306dceb86e8896985bbb9c334a1a680d4(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab8b9681e067fc772bfa8ae21e9b889922f76498043ac3dc59607d18b1c99b6d(
    value: typing.Optional[typing.List[IInstanceAliase]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a37af151d413380fdbb03c303f6e418d5e5ca5225e04d5264a9a4ea57136b320(
    value: typing.Optional[typing.List[IInstanceValiant]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b5a37e8a274c0f3fc20705440c0c3341b45281869a1e4e347af5d91621fcaa1(
    value: typing.Optional[typing.Mapping[builtins.str, builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03c90f1f4cdb0e78188cc1b2b4752b6e641e3139cd9ddbcd4cf9be7e0e0a09dc(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__951253bb0ca138e826c6fe2a480e29d1949fa737e804147291d2ca257fc68fbc(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5af7b97de0c920bbdd298f2015ccefdbeb43ecd7756bcf540abe8209e26d7adb(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a21e4787a48ba458913fa109830cd5d13f8be4ce00374d6d25306a7755c73997(
    *,
    model: JumpStartModel,
    endpoint_name: typing.Optional[builtins.str] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    instance_count: typing.Optional[jsii.Number] = None,
    instance_type: typing.Optional[SageMakerInstanceType] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    startup_health_check_timeout_in_seconds: typing.Optional[jsii.Number] = None,
    vpc_config: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5887bf17d5f030e30d4d81e59cc58f7736b547350a7fc34d4824591bab542b31(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    architecture: _aws_cdk_aws_lambda_ceddda9d.Architecture,
    runtime: _aws_cdk_aws_lambda_ceddda9d.Runtime,
    additional_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
    auto_upgrade: typing.Optional[builtins.bool] = None,
    local: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    layer_version_name: typing.Optional[builtins.str] = None,
    license: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9da98e3b66ac7e9145afc01d0bcd18f45c1684ff1bc89ccc645b65e2edc8f13a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    compatible_architectures: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.Architecture]] = None,
    compatible_runtimes: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.Runtime]] = None,
    description: typing.Optional[builtins.str] = None,
    layer_version_name: typing.Optional[builtins.str] = None,
    license: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52d31c4ca4bd0cf5b3967d59cb772ea252af908e216abb9db44bcadbdcb0c948(
    *,
    description: typing.Optional[builtins.str] = None,
    layer_version_name: typing.Optional[builtins.str] = None,
    license: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87235dce222bf37474e367e0b5284fe8ad89c007d7c7d06682de5ff0d56df01b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cognito_user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
    open_search_index_name: builtins.str,
    bucket_inputs_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_operational_metric: typing.Optional[builtins.bool] = None,
    existing_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    existing_input_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    existing_merged_api: typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi] = None,
    existing_opensearch_domain: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IDomain] = None,
    existing_opensearch_serverless_collection: typing.Optional[_aws_cdk_aws_opensearchserverless_ceddda9d.CfnCollection] = None,
    existing_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    lambda_provisioned_concurrency: typing.Optional[jsii.Number] = None,
    observability: typing.Optional[builtins.bool] = None,
    open_search_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    stage: typing.Optional[builtins.str] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff2c8f0d402dcb481b313b3fe2800ddb797d454c33c358eadd45c7a626be6592(
    *,
    cognito_user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
    open_search_index_name: builtins.str,
    bucket_inputs_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_operational_metric: typing.Optional[builtins.bool] = None,
    existing_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    existing_input_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    existing_merged_api: typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi] = None,
    existing_opensearch_domain: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IDomain] = None,
    existing_opensearch_serverless_collection: typing.Optional[_aws_cdk_aws_opensearchserverless_ceddda9d.CfnCollection] = None,
    existing_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    lambda_provisioned_concurrency: typing.Optional[jsii.Number] = None,
    observability: typing.Optional[builtins.bool] = None,
    open_search_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    stage: typing.Optional[builtins.str] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b47682f30dcd4f711daa26c544bfc9e0888d2931d0711782d9e99f42de2ba10(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cognito_user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
    open_search_index_name: builtins.str,
    bucket_inputs_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    bucket_processed_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_operational_metric: typing.Optional[builtins.bool] = None,
    existing_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    existing_input_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    existing_merged_api: typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi] = None,
    existing_opensearch_domain: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IDomain] = None,
    existing_opensearch_serverless_collection: typing.Optional[_aws_cdk_aws_opensearchserverless_ceddda9d.CfnCollection] = None,
    existing_processed_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    existing_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    observability: typing.Optional[builtins.bool] = None,
    open_search_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    stage: typing.Optional[builtins.str] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84410e9ddf3c6c72a9fafb245544fa73e4c8020dfb3e51d2f31e3b9c8bfa846f(
    *,
    cognito_user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
    open_search_index_name: builtins.str,
    bucket_inputs_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    bucket_processed_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_operational_metric: typing.Optional[builtins.bool] = None,
    existing_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    existing_input_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    existing_merged_api: typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi] = None,
    existing_opensearch_domain: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IDomain] = None,
    existing_opensearch_serverless_collection: typing.Optional[_aws_cdk_aws_opensearchserverless_ceddda9d.CfnCollection] = None,
    existing_processed_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    existing_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    observability: typing.Optional[builtins.bool] = None,
    open_search_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    stage: typing.Optional[builtins.str] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c37da07d50996bf3815df5522cdacee052c06fde9388dfbbfe2234481a961908(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f06ce0cc4b08453b7ab410c78b48041f013a51e2dfa884a02fd5c6e2128fe4e0(
    instance_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f58c993f4fbd1d7d4666ae23b06ee672f893b6774b448ab48869abff7e44114(
    instance_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e3d8b9e643131ffd22e254e28d1be23095a03faa91dc469f13c16edf293c7af(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cognito_user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
    bucket_inputs_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    bucket_processed_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    cfn_cache_cluster_props: typing.Optional[typing.Union[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheClusterProps, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_operational_metric: typing.Optional[builtins.bool] = None,
    event_bus_props: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventBusProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    existing_input_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    existing_merged_api: typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi] = None,
    existing_processed_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    existing_redis_culster: typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster] = None,
    existing_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    is_file_transformation_required: typing.Optional[builtins.str] = None,
    observability: typing.Optional[builtins.bool] = None,
    stage: typing.Optional[builtins.str] = None,
    summary_api_name: typing.Optional[builtins.str] = None,
    summary_chain_type: typing.Optional[builtins.str] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c70798ec1d57933ac8ff9b3e4952de2c9f173958f717d396052ee110b0045bc(
    *,
    cognito_user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
    bucket_inputs_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    bucket_processed_assets_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    cfn_cache_cluster_props: typing.Optional[typing.Union[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheClusterProps, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_operational_metric: typing.Optional[builtins.bool] = None,
    event_bus_props: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventBusProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    existing_input_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    existing_merged_api: typing.Optional[_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi] = None,
    existing_processed_assets_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    existing_redis_culster: typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster] = None,
    existing_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    is_file_transformation_required: typing.Optional[builtins.str] = None,
    observability: typing.Optional[builtins.bool] = None,
    stage: typing.Optional[builtins.str] = None,
    summary_api_name: typing.Optional[builtins.str] = None,
    summary_chain_type: typing.Optional[builtins.str] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__989752ca25fc9932b1bdd01340b7988a6d08041c857f9f2b8919b0eda68523b3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    container: ContainerImage,
    endpoint_name: builtins.str,
    instance_type: SageMakerInstanceType,
    model_data_url: builtins.str,
    model_id: builtins.str,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    instance_count: typing.Optional[jsii.Number] = None,
    model_data_download_timeout_in_seconds: typing.Optional[jsii.Number] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    startup_health_check_timeout_in_seconds: typing.Optional[jsii.Number] = None,
    volume_size_in_gb: typing.Optional[jsii.Number] = None,
    vpc_config: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd1caa527c73cfa2f0cb7fc16dbd9f3c0bd1763ef673bb797faf1f432635f1be(
    statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3440cb6fc8022809464d5c8edf0a71c987b3b0c52761c58076f71a7e8f20a5da(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38086469e018e34a8d8b00c156063e690e17f2bf4c037abc9cac1be2b89ea99b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    container: ContainerImage,
    instance_type: SageMakerInstanceType,
    model_id: builtins.str,
    endpoint_name: typing.Optional[builtins.str] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    instance_count: typing.Optional[jsii.Number] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    startup_health_check_timeout_in_seconds: typing.Optional[jsii.Number] = None,
    vpc_config: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f884fddb56b07302085c01964f7da04278b8808e0f8978b47ee3fa780e1a00a9(
    statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b75f76f86752e358a0164022cc8101b42b03ff1b6cc0fcbea0553348d99ff27(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__014e5d72b7decc2a5275975908d20bc2e6428f93ab52b954050e305acb50ccf5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    model: JumpStartModel,
    endpoint_name: typing.Optional[builtins.str] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    instance_count: typing.Optional[jsii.Number] = None,
    instance_type: typing.Optional[SageMakerInstanceType] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    startup_health_check_timeout_in_seconds: typing.Optional[jsii.Number] = None,
    vpc_config: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel.VpcConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba9c5b6fe6b83af0ad5f9138e4c4257b8c37463d898276834c309ec9d22b3eb2(
    statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a86bb20d33d314b3762c600becde03bdc2caa6db40a8f0e9f3057e11a53a9bac(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3537d2f8bfb6093f936a7883eb70fc78008cb2c2a19e21a76265ec13de0f315(
    *,
    description: typing.Optional[builtins.str] = None,
    layer_version_name: typing.Optional[builtins.str] = None,
    license: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    architecture: _aws_cdk_aws_lambda_ceddda9d.Architecture,
    runtime: _aws_cdk_aws_lambda_ceddda9d.Runtime,
    additional_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
    auto_upgrade: typing.Optional[builtins.bool] = None,
    local: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
