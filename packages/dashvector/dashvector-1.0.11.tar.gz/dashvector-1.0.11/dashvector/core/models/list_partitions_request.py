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
from dashvector.common.types import DashVectorCode, DashVectorException
from dashvector.core.proto import dashvector_pb2


class ListPartitionsRequest(RPCRequest):
    def __init__(self, *, collection_name: str):
        """
        collection_name:str
        """
        self._collection_name = None
        if collection_name is not None:
            if not isinstance(collection_name, str):
                raise DashVectorException(
                    code=DashVectorCode.InvalidArgument,
                    reason=f"DashVectorSDK GetDocRequest partition type({type(collection_name)}) is invalid and must be str",
                )

            if re.search(COLLECTION_AND_PARTITION_NAME_PATTERN, collection_name) is None:
                raise DashVectorException(
                    code=DashVectorCode.InvalidPartitionName,
                    reason=f"DashVectorSDK GetDocRequest partition characters({collection_name}) is invalid and "
                    + COLLECTION_AND_PARTITION_NAME_PATTERN_MSG,
                )
            self._collection_name = collection_name

        """
        ListCollectionsRequest: google.protobuf.Message
        """
        list_request = dashvector_pb2.ListPartitionsRequest()

        super().__init__(request=list_request)

    @property
    def collection_name(self):
        return self._collection_name
