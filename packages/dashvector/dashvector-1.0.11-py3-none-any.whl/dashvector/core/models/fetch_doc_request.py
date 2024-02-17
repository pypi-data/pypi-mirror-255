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


class FetchDocRequest(RPCRequest):
    def __init__(self, *, collection_meta: CollectionMeta, ids: IdsType, partition: Optional[str] = None):
        """
        collection_meta: CollectionMeta
        """
        self._collection_meta = collection_meta
        self._collection_name = collection_meta.name

        """
        ids: IdsType
        """
        self._ids = []
        self._ids_is_single = False
        if isinstance(ids, list):
            if len(ids) < 1 or len(ids) > 1024:
                raise DashVectorException(
                    code=DashVectorCode.ExceedIdsLimit,
                    reason=f"DashVectorSDK GetDocRequest ids list length({len(ids)}) is invalid and must be in [1, 1024]",
                )
            for id in ids:
                if isinstance(id, str):
                    if re.search(DOC_ID_PATTERN, id) is None:
                        raise DashVectorException(
                            code=DashVectorCode.InvalidPrimaryKey,
                            reason=f"DashVectorSDK GetDocRequest id in ids list characters({id}) is invalid and "
                            + DOC_ID_PATTERN_MSG,
                        )
                    self._ids.append(id)
                else:
                    raise DashVectorException(
                        code=DashVectorCode.InvalidArgument,
                        reason=f"DashVectorSDK GetDocRequest id in ids list type({type(id)}) is invalid and must be str",
                    )

        elif isinstance(ids, str):
            if re.search(DOC_ID_PATTERN, ids) is None:
                raise DashVectorException(
                    code=DashVectorCode.InvalidPrimaryKey,
                    reason=f"DashVectorSDK GetDocRequest ids str characters({ids}) is invalid and "
                    + DOC_ID_PATTERN_MSG,
                )

            self._ids.append(ids)
            self._ids_is_single = True
        else:
            raise DashVectorException(
                code=DashVectorCode.InvalidArgument,
                reason=f"DashVectorSDK GetDocRequest ids type({type(ids)}) is invalid and must be [str, List[str]]",
            )

        """
        partition: Optional[str]
        """
        self._partition = None
        if partition is not None:
            if not isinstance(partition, str):
                raise DashVectorException(
                    code=DashVectorCode.InvalidArgument,
                    reason=f"DashVectorSDK GetDocRequest partition type({type(partition)}) is invalid and must be str",
                )

            if re.search(COLLECTION_AND_PARTITION_NAME_PATTERN, partition) is None:
                raise DashVectorException(
                    code=DashVectorCode.InvalidPartitionName,
                    reason=f"DashVectorSDK GetDocRequest partition characters({partition}) is invalid and "
                    + COLLECTION_AND_PARTITION_NAME_PATTERN_MSG,
                )

            self._partition = partition

        """
        FetchDocRequest: google.protobuf.Message
        """
        fetch_request = dashvector_pb2.FetchDocRequest()
        fetch_request.ids.extend(self._ids)
        if self._partition is not None:
            fetch_request.partition = self._partition

        super().__init__(request=fetch_request)

    @property
    def collection_name(self):
        return self._collection_name

    @property
    def partition_name(self):
        return "default" if self._partition is None else self._partition

    @property
    def collection_meta(self):
        return self._collection_meta

    @property
    def ids(self):
        ids_str = ",".join(self._ids)
        return ids_str

    @property
    def ids_is_single(self):
        return self._ids_is_single
