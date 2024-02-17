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
from dashvector.common.error import DashVectorCode, DashVectorException
from dashvector.common.handler import RPCRequest
from dashvector.core.proto import dashvector_pb2


class DeleteCollectionRequest(RPCRequest):
    def __init__(self, *, name: str):
        """
        name: str
        """
        self._name = ""
        if not isinstance(name, str):
            raise DashVectorException(
                code=DashVectorCode.InvalidArgument,
                reason=f"DashVectorSDK DeleteCollectionRequest name type({name}) is Invalid and must be str",
            )

        if re.search(COLLECTION_AND_PARTITION_NAME_PATTERN, name) is None:
            raise DashVectorException(
                code=DashVectorCode.InvalidCollectionName,
                reason=f"DashVectorSDK DeleteCollectionRequest name characters({name}) is invalid and "
                + COLLECTION_AND_PARTITION_NAME_PATTERN_MSG,
            )
        self._name = name

        """
        DeleteCollectionRequest: google.protobuf.Message
        """
        delete_request = dashvector_pb2.DeleteCollectionRequest(name=self._name)

        super().__init__(request=delete_request)

    @property
    def name(self):
        return self._name
