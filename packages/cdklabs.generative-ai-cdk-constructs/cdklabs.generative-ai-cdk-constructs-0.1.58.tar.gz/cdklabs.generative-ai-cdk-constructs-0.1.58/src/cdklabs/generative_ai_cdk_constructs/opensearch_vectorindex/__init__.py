'''
# Amazon OpenSearch Vector Index Construct Library

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

This construct library provides a resource that creates a vector index on an Amazon OpenSearch Domain. It currently only supports Amazon OpenSearch Serverless.

## Table of contents

* [API](#api)
* [Vector Index](#vector-index)

## API

See the [API documentation](../../../apidocs/modules/opensearchserverless.md).

## Vector Index

The `VectorIndex` resource connects to OpenSearch and creates an index suitable for use with Amazon Bedrock Knowledge Bases.

```python
import { opensearchserverless, opensearch_vectorindex } from '@cdklabs/generative-ai-cdk-constructs';

const vectorStore = new opensearchserverless.VectorCollection(this, 'VectorCollection');

new opensearch_vectorindex.VectorIndex(this, 'VectorIndex', {
collection: vectorStore,
indexName,
vectorField,
vectorDimensions: 1536,
mappings: [
  {
    mappingField: 'AMAZON_BEDROCK_TEXT_CHUNK',
    dataType: 'text',
    filterable: true,
  },
  {
    mappingField: 'AMAZON_BEDROCK_METADATA',
    dataType: 'text',
    filterable: false,
  },
],
});
```
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

import aws_cdk as _aws_cdk_ceddda9d
import constructs as _constructs_77d1e7e8
from ..opensearchserverless import VectorCollection as _VectorCollection_91bfdaa9


@jsii.data_type(
    jsii_type="@cdklabs/generative-ai-cdk-constructs.opensearch_vectorindex.MetadataManagementFieldProps",
    jsii_struct_bases=[],
    name_mapping={
        "data_type": "dataType",
        "filterable": "filterable",
        "mapping_field": "mappingField",
    },
)
class MetadataManagementFieldProps:
    def __init__(
        self,
        *,
        data_type: builtins.str,
        filterable: builtins.bool,
        mapping_field: builtins.str,
    ) -> None:
        '''(experimental) Metadata field definitions.

        :param data_type: (experimental) The data type of the field.
        :param filterable: (experimental) Whether the field is filterable.
        :param mapping_field: (experimental) The name of the field.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc232715f2e7167be4478ee7ff835dccae7b1ffcbc414d5da6a4de31bf5a23ef)
            check_type(argname="argument data_type", value=data_type, expected_type=type_hints["data_type"])
            check_type(argname="argument filterable", value=filterable, expected_type=type_hints["filterable"])
            check_type(argname="argument mapping_field", value=mapping_field, expected_type=type_hints["mapping_field"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "data_type": data_type,
            "filterable": filterable,
            "mapping_field": mapping_field,
        }

    @builtins.property
    def data_type(self) -> builtins.str:
        '''(experimental) The data type of the field.

        :stability: experimental
        '''
        result = self._values.get("data_type")
        assert result is not None, "Required property 'data_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filterable(self) -> builtins.bool:
        '''(experimental) Whether the field is filterable.

        :stability: experimental
        '''
        result = self._values.get("filterable")
        assert result is not None, "Required property 'filterable' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def mapping_field(self) -> builtins.str:
        '''(experimental) The name of the field.

        :stability: experimental
        '''
        result = self._values.get("mapping_field")
        assert result is not None, "Required property 'mapping_field' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetadataManagementFieldProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VectorIndex(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/generative-ai-cdk-constructs.opensearch_vectorindex.VectorIndex",
):
    '''(experimental) Deploy a vector index on the collection.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        collection: _VectorCollection_91bfdaa9,
        index_name: builtins.str,
        mappings: typing.Sequence[typing.Union[MetadataManagementFieldProps, typing.Dict[builtins.str, typing.Any]]],
        vector_dimensions: jsii.Number,
        vector_field: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param collection: (experimental) The OpenSearch Vector Collection.
        :param index_name: (experimental) The name of the index.
        :param mappings: (experimental) The metadata management fields.
        :param vector_dimensions: (experimental) The number of dimensions in the vector.
        :param vector_field: (experimental) The name of the vector field.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5003f7f8d99d7c28d9747284aec10690f601ccd6b2cfbd8d4576c55545a72e0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = VectorIndexProps(
            collection=collection,
            index_name=index_name,
            mappings=mappings,
            vector_dimensions=vector_dimensions,
            vector_field=vector_field,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cdklabs/generative-ai-cdk-constructs.opensearch_vectorindex.VectorIndexProps",
    jsii_struct_bases=[],
    name_mapping={
        "collection": "collection",
        "index_name": "indexName",
        "mappings": "mappings",
        "vector_dimensions": "vectorDimensions",
        "vector_field": "vectorField",
    },
)
class VectorIndexProps:
    def __init__(
        self,
        *,
        collection: _VectorCollection_91bfdaa9,
        index_name: builtins.str,
        mappings: typing.Sequence[typing.Union[MetadataManagementFieldProps, typing.Dict[builtins.str, typing.Any]]],
        vector_dimensions: jsii.Number,
        vector_field: builtins.str,
    ) -> None:
        '''(experimental) Properties for the VectorIndex.

        :param collection: (experimental) The OpenSearch Vector Collection.
        :param index_name: (experimental) The name of the index.
        :param mappings: (experimental) The metadata management fields.
        :param vector_dimensions: (experimental) The number of dimensions in the vector.
        :param vector_field: (experimental) The name of the vector field.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d660fe6c930253fed67011cc25bd50dfb6c4c58bfc412a7d480a8ef1787f5dd)
            check_type(argname="argument collection", value=collection, expected_type=type_hints["collection"])
            check_type(argname="argument index_name", value=index_name, expected_type=type_hints["index_name"])
            check_type(argname="argument mappings", value=mappings, expected_type=type_hints["mappings"])
            check_type(argname="argument vector_dimensions", value=vector_dimensions, expected_type=type_hints["vector_dimensions"])
            check_type(argname="argument vector_field", value=vector_field, expected_type=type_hints["vector_field"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "collection": collection,
            "index_name": index_name,
            "mappings": mappings,
            "vector_dimensions": vector_dimensions,
            "vector_field": vector_field,
        }

    @builtins.property
    def collection(self) -> _VectorCollection_91bfdaa9:
        '''(experimental) The OpenSearch Vector Collection.

        :stability: experimental
        '''
        result = self._values.get("collection")
        assert result is not None, "Required property 'collection' is missing"
        return typing.cast(_VectorCollection_91bfdaa9, result)

    @builtins.property
    def index_name(self) -> builtins.str:
        '''(experimental) The name of the index.

        :stability: experimental
        '''
        result = self._values.get("index_name")
        assert result is not None, "Required property 'index_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mappings(self) -> typing.List[MetadataManagementFieldProps]:
        '''(experimental) The metadata management fields.

        :stability: experimental
        '''
        result = self._values.get("mappings")
        assert result is not None, "Required property 'mappings' is missing"
        return typing.cast(typing.List[MetadataManagementFieldProps], result)

    @builtins.property
    def vector_dimensions(self) -> jsii.Number:
        '''(experimental) The number of dimensions in the vector.

        :stability: experimental
        '''
        result = self._values.get("vector_dimensions")
        assert result is not None, "Required property 'vector_dimensions' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def vector_field(self) -> builtins.str:
        '''(experimental) The name of the vector field.

        :stability: experimental
        '''
        result = self._values.get("vector_field")
        assert result is not None, "Required property 'vector_field' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VectorIndexProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "MetadataManagementFieldProps",
    "VectorIndex",
    "VectorIndexProps",
]

publication.publish()

def _typecheckingstub__bc232715f2e7167be4478ee7ff835dccae7b1ffcbc414d5da6a4de31bf5a23ef(
    *,
    data_type: builtins.str,
    filterable: builtins.bool,
    mapping_field: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5003f7f8d99d7c28d9747284aec10690f601ccd6b2cfbd8d4576c55545a72e0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    collection: _VectorCollection_91bfdaa9,
    index_name: builtins.str,
    mappings: typing.Sequence[typing.Union[MetadataManagementFieldProps, typing.Dict[builtins.str, typing.Any]]],
    vector_dimensions: jsii.Number,
    vector_field: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d660fe6c930253fed67011cc25bd50dfb6c4c58bfc412a7d480a8ef1787f5dd(
    *,
    collection: _VectorCollection_91bfdaa9,
    index_name: builtins.str,
    mappings: typing.Sequence[typing.Union[MetadataManagementFieldProps, typing.Dict[builtins.str, typing.Any]]],
    vector_dimensions: jsii.Number,
    vector_field: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
