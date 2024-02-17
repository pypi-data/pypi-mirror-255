##
#   Copyright 2021 Alibaba, Inc. and its affiliates. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
##

# -*- coding: utf-8 -*-

import re

from dashvector.common.constants import *
from dashvector.common.handler import RPCRequest
from dashvector.common.types import *
from dashvector.core.models.collection_meta_status import CollectionMeta
from dashvector.core.proto import dashvector_pb2
from dashvector.util.convertor import to_sorted_sparse_vector


class QueryDocRequest(RPCRequest):
    def __init__(
        self,
        *,
        collection_meta: CollectionMeta,
        vector: Optional[VectorValueType] = None,
        id: Optional[str] = None,
        topk: int = 10,
        filter: Optional[str] = None,
        include_vector: bool = False,
        partition: Optional[str] = None,
        output_fields: Optional[List[str]] = None,
        sparse_vector: Optional[Dict[int, float]] = None,
    ):
        self._collection_meta = collection_meta
        self._collection_name = collection_meta.name
        self._dtype = VectorType.get(collection_meta.dtype)
        self._dimension = collection_meta.dimension
        self._field_map = collection_meta.fields_schema
        self._origin_vector = vector
        self._id = id
        self._metric = collection_meta.metric
        """
        QueryRequest
        """
        query_request = dashvector_pb2.QueryDocRequest()

        """
        vector: Optional[VectorValueType] = None
        """
        self._vector = vector
        if id is not None and vector is not None:
            raise DashVectorException(
                code=DashVectorCode.ExistVectorAndId,
                reason="DashVectorSDK QueryDocRequest supports passing in either or neither of the two parameters vector and id, but not both",
            )
        elif id is not None:
            if isinstance(id, str):
                if re.search(DOC_ID_PATTERN, id) is None:
                    raise DashVectorException(
                        code=DashVectorCode.InvalidPrimaryKey,
                        reason=f"DashVectorSDK QueryDocRequest id str characters({id}) is invalid and "
                        + DOC_ID_PATTERN_MSG,
                    )
                query_request.id = id
            else:
                raise DashVectorException(
                    code=DashVectorCode.InvalidArgument,
                    reason=f"DashVectorSDK QueryDocRequest expect id to be <str> but actual type is ({type(id)})",
                )
        elif vector is not None:
            if isinstance(self._vector, list):
                if len(self._vector) != self._dimension:
                    raise DashVectorException(
                        code=DashVectorCode.MismatchedDimension,
                        reason=f"DashVectorSDK QueryDocRequest vector list length({len(self._vector)}) is invalid and must be same with collection dimension({self._dimension})",
                    )
                vector_data_type = VectorType.get_vector_data_type(type(self._vector[0]))
                if vector_data_type != self._dtype:
                    raise DashVectorException(
                        code=DashVectorCode.MismatchedDataType,
                        reason=f"DashVectorSDK QueryDocRequest vector type({type(self._vector[0])}) is invalid and must be {collection_meta.dtype}",
                    )
                if vector_data_type == VectorType.INT:
                    try:
                        self._vector = VectorType.convert_to_bytes(self._vector, self._dtype, self._dimension)
                    except Exception as e:
                        raise DashVectorException(
                            code=DashVectorCode.InvalidVectorFormat,
                            reason=f"DashVectorSDK QueryDocRequest vector value({vector}) is invalid and int value must be [-128, 127]",
                        )
            elif isinstance(self._vector, np.ndarray):
                if self._vector.ndim != 1:
                    raise DashVectorException(
                        code=DashVectorCode.InvalidArgument,
                        reason=f"DashVectorSDK QueryDocRequest vector numpy dimension({self._vector.ndim}) is invalid and must be 1",
                    )
                if self._vector.shape[0] != self._dimension:
                    raise DashVectorException(
                        code=DashVectorCode.MismatchedDimension,
                        reason=f"DashVectorSDK QueryDocRequest vector numpy shape[0]({self._vector.shape[0]}) is invalid and must be same with collection dimension({self._dimension})",
                    )
            else:
                raise DashVectorException(
                    code=DashVectorCode.InvalidArgument,
                    reason=f"DashVectorSDK QueryDocRequest vector type({type(self._vector)}) is invalid and must be [list, numpy.ndarray]",
                )

            if isinstance(self._vector, list):
                query_request.vector.float_vector.values.extend(self._vector)
            elif isinstance(self._vector, bytes):
                query_request.vector.byte_vector = self._vector
            elif isinstance(self._vector, np.ndarray):
                if self._dtype == VectorType.INT:
                    data_format_type = VectorType.get_vector_data_format(self._dtype)
                    self._vector = np.ascontiguousarray(self._vector, dtype=f"<{data_format_type}").tobytes()
                    query_request.vector.byte_vector = self._vector
                else:
                    self._vector = list(self._vector)
                    query_request.vector.float_vector.values.extend(self._vector)
        """
        topk: int = 10
        """
        self._topk = topk
        if not isinstance(topk, int):
            raise DashVectorException(
                code=DashVectorCode.InvalidArgument,
                reason=f"DashVectorSDK QueryDocRequest topk type({type(topk)}) is invalid and must be int",
            )
        if topk < 1 or topk > 1024:
            raise DashVectorException(
                code=DashVectorCode.InvalidTopk,
                reason=f"DashVectorSDK GetDocRequest topk value({topk}) is invalid and must be in [1, 1024]",
            )
        query_request.topk = self._topk

        """
        filter: Optional[str] = None,
        """
        self._filter = None
        if filter is not None:
            if not isinstance(filter, str):
                raise DashVectorException(
                    code=DashVectorCode.InvalidArgument,
                    reason=f"DashVectorSDK QueryDocRequest filter type({type(filter)}) is invalid and must be str",
                )

            if len(filter) > 10240:
                raise DashVectorException(
                    code=DashVectorCode.InvalidFilter,
                    reason=f"DashVectorSDK GetDocRequest filter length({len(filter)}) is invalid and must be in [0, 10240]",
                )

            if len(filter) > 0:
                self._filter = filter
        if self._filter is not None:
            query_request.filter = self._filter

        """
        include_vector: bool = False,
        """
        self._include_vector = include_vector
        if not isinstance(include_vector, bool):
            raise DashVectorException(
                code=DashVectorCode.InvalidArgument,
                reason=f"DashVectorSDK QueryDocRequest include_vector type({type(include_vector)}) is invalid and must be bool",
            )
        query_request.include_vector = self._include_vector

        """
        partition: Optional[str] = None
        """
        self._partition = None
        if partition is not None:
            if not isinstance(partition, str):
                raise DashVectorException(
                    code=DashVectorCode.InvalidArgument,
                    reason=f"DashVectorSDK QueryDocRequest partition type({type(partition)}) is invalid and must be str",
                )

            if re.search(COLLECTION_AND_PARTITION_NAME_PATTERN, partition) is None:
                raise DashVectorException(
                    code=DashVectorCode.InvalidPartitionName,
                    reason=f"DashVectorSDK QueryDocRequest partition characters({partition}) is invalid and "
                    + COLLECTION_AND_PARTITION_NAME_PATTERN_MSG,
                )

            self._partition = partition
        if self._partition is not None:
            query_request.partition = self._partition

        """
        output_fields: Optional[List[str]] = None
        """
        self._output_fields = None
        if output_fields is not None:
            if isinstance(output_fields, list):
                for output_field in output_fields:
                    if not isinstance(output_field, str):
                        raise DashVectorException(
                            code=DashVectorCode.InvalidArgument,
                            reason=f"DashVectorSDK QueryDocRequest output_field in output_fields type({type(output_field)}) is invalid and must be list[str]",
                        )

                    if re.search(FIELD_NAME_PATTERN, output_field) is None:
                        raise DashVectorException(
                            code=DashVectorCode.InvalidField,
                            reason=f"DashVectorSDK QueryDocRequest output_field in output_fields characters({output_field}) is invalid and "
                            + FIELD_NAME_PATTERN_MSG,
                        )

                self._output_fields = output_fields
            else:
                raise DashVectorException(
                    code=DashVectorCode.InvalidArgument,
                    reason=f"DashVectorSDK QueryDocRequest output_fields type({type(output_fields)}) is invalid and must be List[str]",
                )
        if self._output_fields is not None:
            query_request.output_fields.extend(self._output_fields)

        """
        sparse_vector: Optional[Dict[int, float]] = None
        """
        self._sparse_vector = sparse_vector
        if self._sparse_vector is not None:
            if self._metric != MetricStrType.DOTPRODUCT:
                raise DashVectorException(
                    code=DashVectorCode.InvalidSparseValues,
                    reason=f"DashVectorSDK supports query with sparse_vector only collection metric is dotproduct",
                )
            for key, value in to_sorted_sparse_vector(self._sparse_vector).items():
                query_request.sparse_vector[key] = value
        super().__init__(request=query_request)

    @property
    def collection_meta(self):
        return self._collection_meta

    @property
    def collection_name(self):
        return self._collection_name

    @property
    def include_vector(self):
        return self._include_vector

    def to_json(self):
        data = {
            "topk": self._topk,
            "include_vector": self._include_vector,
        }
        if self._origin_vector is not None:
            vector = self._origin_vector
            if isinstance(vector, np.ndarray):
                vector = vector.astype(np.float32).tolist()
            data["vector"] = vector
        else:
            data["id"] = self._id
        if self._filter is not None:
            data["filter"] = self._filter
        if self._partition is not None:
            data["partition"] = self._partition
        if self._sparse_vector is not None:
            data["sparse_vector"] = self._sparse_vector
        if self._output_fields is not None:
            data["output_fields"] = self._output_fields

        return json.dumps(data)
