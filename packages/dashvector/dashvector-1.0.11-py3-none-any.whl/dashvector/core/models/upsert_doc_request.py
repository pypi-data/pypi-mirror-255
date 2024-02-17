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
from dashvector.core.doc import Doc, DocBuilder
from dashvector.core.models.collection_meta_status import CollectionMeta
from dashvector.core.proto import dashvector_pb2
from dashvector.util.convertor import to_sorted_sparse_vector


class UpsertDocRequest(RPCRequest):
    def __init__(
        self,
        *,
        collection_meta: CollectionMeta,
        docs: Union[Doc, Tuple, List[Doc], List[Tuple]],
        partition: Optional[str] = None,
        action: str = "upsert",
    ):
        """
        collection_meta: CollectionMeta
        """
        self._collection_meta = collection_meta
        self._collection_name = collection_meta.name
        self._field = collection_meta.fields_schema
        self._dtype = VectorType.get(collection_meta.dtype)
        self._dimension = collection_meta.dimension
        self._metric = collection_meta.metric

        """
        partition: Optional[str]
        """
        self._partition = None
        if partition is not None:
            if not isinstance(partition, str):
                raise DashVectorException(
                    code=DashVectorCode.InvalidArgument,
                    reason=f"DashVectorSDK UpsertDocRequest partition type({type(partition)}) is invalid and must be str",
                )

            if re.search(COLLECTION_AND_PARTITION_NAME_PATTERN, partition) is None:
                raise DashVectorException(
                    code=DashVectorCode.InvalidPartitionName,
                    reason=f"DashVectorSDK UpsertDocRequest partition characters({partition}) is invalid and "
                    + COLLECTION_AND_PARTITION_NAME_PATTERN_MSG,
                )

            self._partition = partition

        """
        action: str
        """
        self._action = ""
        if not isinstance(action, str):
            raise DashVectorException(
                code=DashVectorCode.InvalidArgument,
                reason=f"DashVectorSDK UpsertDocRequest action type({type(action)}) is invalid and must be str",
            )
        if action not in ("upsert", "insert", "update"):
            raise DashVectorException(
                code=DashVectorCode.InvalidArgument,
                reason=f"DashVectorSDK UpsertDocRequest action value({action}) is invalid and must be in ['insert', 'update', 'upsert']",
            )
        self._action = action

        """
        InsertDocRequest: google.protobuf.Message
        UpdateDocRequest: google.protobuf.Message
        UpsertDocRequest: google.protobuf.Message
        """
        if self._action == "upsert":
            upsert_request = dashvector_pb2.UpsertDocRequest()
        elif self._action == "insert":
            upsert_request = dashvector_pb2.InsertDocRequest()
        else:
            upsert_request = dashvector_pb2.UpdateDocRequest()

        if self._partition is not None:
            upsert_request.partition = self._partition

        """
        docs: Union[Doc, Tuple, List[Doc], List[Tuple]]
        """
        id_list = []
        vector_list = []
        fields_list = []
        sparse_vector_list = []

        if isinstance(docs, Doc):
            id, vector, fields, sparse_vector = self._format_input(doc=docs)
            id_list.append(id)
            vector_list.append(vector)
            fields_list.append(fields)
            sparse_vector_list.append(sparse_vector)
        elif isinstance(docs, tuple):
            id, vector, fields, sparse_vector = self._format_input(tup=docs)
            id_list.append(id)
            vector_list.append(vector)
            fields_list.append(fields)
            sparse_vector_list.append(sparse_vector)
        elif isinstance(docs, list):
            if len(docs) <= 0 or len(docs) > 1024:
                raise DashVectorException(
                    code=DashVectorCode.InvalidBatchSize,
                    reason=f"DashVectorSDK UpsertDocRequest input docs length({len(docs)}) is invalid and must be in [1, 1024]",
                )

            for doc in docs:
                if isinstance(doc, Doc):
                    id, vector, fields, sparse_vector = self._format_input(doc=doc)
                elif isinstance(doc, tuple):
                    id, vector, fields, sparse_vector = self._format_input(tup=doc)
                else:
                    raise DashVectorException(
                        code=DashVectorCode.InvalidArgument,
                        reason=f"DashVectorSDK UpsertDocRequest doc type({type(doc)}) in docs is invalid and must be in [Doc, Tuple]",
                    )
                id_list.append(id)
                vector_list.append(vector)
                fields_list.append(fields)
                sparse_vector_list.append(sparse_vector)
        else:
            raise DashVectorException(
                code=DashVectorCode.InvalidArgument,
                reason=f"DashVectorSDK UpsertDocRequest input type({type(docs)}) is Invalid and must be in [Doc, Tuple]",
            )

        id_list, vector_list, fields_list, sparse_vector_list = self._format_params(
            id_list, vector_list, fields_list, sparse_vector_list
        )

        self._docs = []
        for _list_id in range(len(id_list)):
            id = id_list[_list_id]
            vector = vector_list[_list_id]
            field_map = fields_list[_list_id]
            sparse_vector = sparse_vector_list[_list_id]

            new_doc = upsert_request.docs.add()

            # doc id
            if not isinstance(id, str):
                raise DashVectorException(
                    code=DashVectorCode.InvalidArgument,
                    reason=f"DashVectorSDK UpsertDocRequest doc id({type(id)}) is invalid and must be str",
                )
            new_doc.id = id

            # doc vector
            if isinstance(vector, bytes):
                new_doc.vector.byte_vector = vector
            elif isinstance(vector, list):
                new_doc.vector.float_vector.values.extend(vector)
            elif isinstance(vector, np.ndarray):
                new_doc.vector.float_vector.values.extend(vector)
            else:
                raise DashVectorException(
                    code=DashVectorCode.InvalidArgument,
                    reason=f"DashVectorSDK UpsertDocRequest vector type({type(vector)}) in invalid and must be in [bytes, list, numpy.ndarray]",
                )

            # doc fields
            if field_map is not None:
                for field_name, filed_value in field_map.items():
                    if not isinstance(field_name, str):
                        raise DashVectorException(
                            code=DashVectorCode.InvalidArgument,
                            reason=f"DashVectorSDK UpsertDocRequest field name type({type(field_name)}) is invalid and must be str",
                        )

                    if re.search(FIELD_NAME_PATTERN, field_name) is None:
                        raise DashVectorException(
                            code=DashVectorCode.InvalidFieldName,
                            reason=f"DashVectorSDK UpsertDocRequest field name characters({field_name}) is invalid and "
                            + FIELD_NAME_PATTERN_MSG,
                        )

                    fvalue = new_doc.fields[field_name]
                    ftype = FieldType.get_field_data_type(type(filed_value))
                    if ftype == FieldType.BOOL:
                        fvalue.bool_value = filed_value
                    elif ftype == FieldType.FLOAT:
                        fvalue.float_value = filed_value
                    elif ftype == FieldType.INT:
                        fvalue.int_value = filed_value
                    elif ftype == FieldType.STRING:
                        fvalue.string_value = filed_value
            # doc sparse_vector
            if sparse_vector is not None:
                if self._metric != MetricStrType.DOTPRODUCT:
                    raise DashVectorException(
                        code=DashVectorCode.InvalidSparseValues,
                        reason=f"DashVectorSDK supports doc with sparse_vector only collection metric is dotproduct",
                    )
                for key, value in sparse_vector.items():
                    new_doc.sparse_vector[key] = value
            self._docs.append(DocBuilder.from_pb(new_doc, collection_meta=collection_meta).__dict__())

        super().__init__(request=upsert_request)

    def _format_input(self, *, doc: Optional[Doc] = None, tup: Optional[Tuple] = None):
        if doc is not None:
            return doc.id, doc.vector, doc.fields, doc.sparse_vector
        elif tup is not None:
            if len(tup) == 2:
                return tup[0], tup[1], None, None
            elif len(tup) == 3:
                return tup[0], tup[1], tup[2], None
            elif len(tup) == 4:
                return tup[0], tup[1], tup[2], tup[3]
            else:
                raise DashVectorException(
                    code=DashVectorCode.InvalidArgument,
                    reason=f"DashVectorSDK UpsertDocRequest doc tuple length({len(tup)}) is invalid and must be in [2, 4]",
                )
        else:
            raise DashVectorException(
                code=DashVectorCode.InvalidArgument,
                reason="DashVectorSDK UpsertDocRequest doc is invalid and must be in [Doc, Tuple]",
            )

    def _format_params(
        self,
        id_list: List[str],
        vector_list: List[VectorValueType],
        fields_list: Optional[List[FieldValueType]] = None,
        sparse_vector_list: Optional[List[Dict[int, float]]] = None,
    ):
        batch_size = len(id_list)

        # check doc_id
        for id in id_list:
            if isinstance(id, str):
                if re.search(DOC_ID_PATTERN, id) is None:
                    raise DashVectorException(
                        code=DashVectorCode.InvalidPrimaryKey,
                        reason=f"DashVectorSDK UpsertDocRequest id characters({id}) is invalid and "
                        + DOC_ID_PATTERN_MSG,
                    )
            else:
                raise DashVectorException(
                    code=DashVectorCode.InvalidArgument,
                    reason=f"DashVectorSDK UpsertDocRequest id type({type(id)}) invalid and must be str",
                )

        # check vector
        if batch_size != len(vector_list):
            raise DashVectorException(
                code=DashVectorCode.InvalidBatchSize,
                reason=f"DashVectorSDK UpsertDocRequest batch size({batch_size}) is different between id and vector",
            )

        for vector_idx in range(len(vector_list)):
            vector_list[vector_idx] = self._vector_to_pb(vector_list[vector_idx])

        # check fields
        if batch_size != len(fields_list):
            raise DashVectorException(
                code=DashVectorCode.InvalidBatchSize,
                reason=f"DashVectorSDK UpsertDocRequest batch size({batch_size}) is different between id and fields",
            )
        for fields_one in fields_list:
            if fields_one is None:
                continue

            if not isinstance(fields_one, dict):
                raise DashVectorException(
                    code=DashVectorCode.InvalidField,
                    reason=f"DashVectorSDK UpsertDocRequest fields type({type(fields_one)}) is invalid",
                )

            if len(fields_one) > 1024:
                raise DashVectorException(
                    code=DashVectorCode.InvalidField,
                    reason=f"DashVectorSDK UpsertDocRequest fields length({len(fields_one)}) is invalid and must be in [1, 1024]",
                )

        # check sparse_vector
        if batch_size != len(sparse_vector_list):
            raise DashVectorException(
                code=DashVectorCode.InvalidBatchSize,
                reason=f"DashVectorSDK UpsertDocRequest batch size({batch_size}) is different between id and sparse_vector",
            )
        sort_sparse_lists = [to_sorted_sparse_vector(sparse_vector) for sparse_vector in sparse_vector_list]
        return id_list, vector_list, fields_list, sort_sparse_lists

    def _vector_to_pb(self, vector: VectorValueType):
        if isinstance(vector, list):
            if len(vector) != self._dimension:
                raise DashVectorException(
                    code=DashVectorCode.MismatchedDimension,
                    reason=f"DashVectorSDK UpsertDocRequest vector length({len(vector)}) is invalid and must be same with collection dimension({self._dimension})",
                )
            vector_data_type = VectorType.get_vector_data_type(type(vector[0]))
            if vector_data_type != self._dtype:
                raise DashVectorException(
                    code=DashVectorCode.MismatchedDataType,
                    reason=f"DashVectorSDK UpsertDocRequest vector type({type(vector[0])}) is invalid and must be in [int, float]",
                )
            if VectorType.INT == self._dtype:
                try:
                    return VectorType.convert_to_bytes(vector, self._dtype, self._dimension)
                except Exception as e:
                    raise DashVectorException(
                        code=DashVectorCode.InvalidVectorFormat,
                        reason=f"DashVectorSDK UpsertDocRequest vector value({vector}) is invalid and int value must be in [-128,127]",
                    )
        elif isinstance(vector, np.ndarray):
            if vector.ndim != 1:
                raise DashVectorException(
                    code=DashVectorCode.InvalidArgument,
                    reason=f"DashVectorSDK UpsertDocRequest vector numpy dimension({vector.ndim}) is invalid and must be 1",
                )
            if vector.shape[0] != self._dimension:
                raise DashVectorException(
                    code=DashVectorCode.MismatchedDimension,
                    reason=f"DashVectorSDK UpsertDocRequest vector numpy shape[0]({vector.shape[0]}) is invalid and must be same with collection dimension({self._dimension})",
                )
            try:
                if VectorType.INT == self._dtype:
                    data_format_type = VectorType.get_vector_data_format(self._dtype)
                    return np.ascontiguousarray(vector, dtype=f"<{data_format_type}").tobytes()
                else:
                    return vector
            except Exception as e:
                raise DashVectorException(
                    code=DashVectorCode.InvalidVectorFormat,
                    reason=f"DashVectorSDK UpsertDocRequest vector value({vector}) is invalid",
                )
        else:
            raise DashVectorException(
                code=DashVectorCode.InvalidVectorFormat,
                reason=f"DashVectorSDK UpsertDocRequest vector type({type(vector)}) is invalid and must be in [List, numpy.ndarray]",
            )
        return vector

    @property
    def collection_name(self):
        return self._collection_name

    def to_json(self):
        data = {"partition": self._partition, "docs": self._docs}
        return json.dumps(data)
