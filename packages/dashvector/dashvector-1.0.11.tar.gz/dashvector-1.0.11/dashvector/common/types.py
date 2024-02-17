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

import json
import struct
from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import numpy as np

from dashvector.common.error import DashVectorCode, DashVectorException
from dashvector.common.handler import RPCResponse
from dashvector.common.status import Status
from dashvector.util.convertor import to_json_without_ascii

VectorDataType = Union[
    Type[int],
    Type[float],
    Type[bool],
    Type[np.int8],
    Type[np.int16],
    Type[np.float16],
    Type[np.bool_],
    Type[np.float32],
    Type[np.float64],
]
VectorValueType = Union[List[int], List[float], np.ndarray]
FieldDataType = Dict[str, Union[Type[str], Type[int], Type[float], Type[bool]]]
FieldValueType = Dict[str, Union[str, int, float, bool]]
IdsType = Union[str, List[str]]
ValueDataType = Union[str, int, float, bool]


class DashVectorProtocol(IntEnum):
    GRPC = 0
    HTTP = 1


class MetricStrType(str, Enum):
    EUCLIDEAN = "euclidean"
    DOTPRODUCT = "dotproduct"
    COSINE = "cosine"


class MetricType(IntEnum):
    EUCLIDEAN = 0
    DOTPRODUCT = 1
    COSINE = 2

    @staticmethod
    def get(mtype: Union[str, MetricStrType]) -> IntEnum:
        if mtype == MetricStrType.EUCLIDEAN:
            return MetricType.EUCLIDEAN
        elif mtype == MetricStrType.DOTPRODUCT:
            return MetricType.DOTPRODUCT
        elif mtype == MetricStrType.COSINE:
            return MetricType.COSINE
        else:
            raise DashVectorException(
                code=DashVectorCode.InvalidArgument,
                reason=f"DashVectorSDK get invalid metrictype {mtype} and must be in [cosine, dotproduct, euclidean]",
            )

    @staticmethod
    def str(mtype: Union[int, IntEnum]) -> str:
        if mtype == MetricType.EUCLIDEAN:
            return MetricStrType.EUCLIDEAN.value
        elif mtype == MetricType.DOTPRODUCT:
            return MetricStrType.DOTPRODUCT.value
        elif mtype == MetricType.COSINE:
            return MetricStrType.COSINE.value
        raise DashVectorException(
            code=DashVectorCode.InvalidArgument,
            reason=f"DashVectorSDK get invalid metrictype {mtype} and must be in [cosine, dotproduct, euclidean]",
        )


class VectorStrType(str, Enum):
    FLOAT = "FLOAT"
    INT = "INT"


class VectorType(IntEnum):
    FLOAT = 0
    INT = 1

    @staticmethod
    def get(vtype: Union[str, VectorStrType]) -> IntEnum:
        if vtype == VectorStrType.FLOAT:
            return VectorType.FLOAT
        elif vtype == VectorStrType.INT:
            return VectorType.INT
        else:
            raise DashVectorException(
                code=DashVectorCode.InvalidVectorType,
                reason=f"DashVectorSDK get invalid vectortype {vtype} and must be in [int, float]",
            )

    @staticmethod
    def str(vtype: Union[int, IntEnum]) -> str:
        if vtype == VectorType.FLOAT:
            return VectorStrType.FLOAT.value
        elif vtype == VectorType.INT:
            return VectorStrType.INT.value
        raise DashVectorException(
            code=DashVectorCode.InvalidVectorType,
            reason=f"DashVectorSDK get invalid vectortype {vtype} and must be in [int, float]]",
        )

    @staticmethod
    def get_vector_data_type(vtype: Type):
        if not isinstance(vtype, type):
            raise DashVectorException(
                code=DashVectorCode.InvalidVectorType,
                reason=f"DashVectorSDK does not support vector data type {vtype} and must be in [int, float]",
            )
        if vtype not in _vector_dtype_map:
            raise DashVectorException(
                code=DashVectorCode.InvalidVectorType,
                reason=f"DashVectorSDK does not support vector data type {vtype} and must be in [int, float]",
            )
        return _vector_dtype_map[vtype]

    @staticmethod
    def get_vector_data_format(data_type):
        if data_type not in (VectorType.INT, VectorType.FLOAT):
            raise DashVectorException(
                code=DashVectorCode.InvalidVectorType,
                reason=f"DashVectorSDK does not support vector({data_type}) to convert bytes",
            )
        return _vector_type_to_format[data_type]

    @staticmethod
    def convert_to_bytes(feature, data_type, dimension):
        if data_type not in (VectorType.INT, VectorType.FLOAT):
            raise DashVectorException(
                code=DashVectorCode.InvalidVectorType,
                reason=f"DashVectorSDK does not support auto pack feature type({data_type})",
            )
        return struct.pack(f"<{dimension}{_vector_type_to_format[data_type]}", *feature)

    @staticmethod
    def convert_to_dtype(feature, data_type, dimension):
        if data_type not in (VectorType.INT, VectorType.FLOAT):
            raise DashVectorException(
                code=DashVectorCode.InvalidVectorType,
                reason=f"DashVectorSDK does not support auto unpack feature type({data_type})",
            )
        return struct.unpack(f"<{dimension}{_vector_type_to_format[data_type]}", feature)

    @property
    def indices(self):
        return self._indices

    @property
    def values(self):
        return self._values

    def __dict__(self):
        return {"indices": self.indices, "values": self.values}


class FieldStrType(str, Enum):
    BOOL = "BOOL"
    STRING = "STRING"
    INT = "INT"
    FLOAT = "FLOAT"


class FieldType(IntEnum):
    BOOL = 0
    STRING = 1
    INT = 2
    FLOAT = 3

    @staticmethod
    def get(ftype: Union[str, FieldStrType]) -> IntEnum:
        if ftype == FieldStrType.BOOL:
            return FieldType.BOOL
        elif ftype == FieldStrType.STRING:
            return FieldType.STRING
        elif ftype == FieldStrType.INT:
            return FieldType.INT
        elif ftype == FieldStrType.FLOAT:
            return FieldType.FLOAT
        else:
            raise DashVectorException(
                code=DashVectorCode.InvalidField,
                reason=f"DashVectorSDK does not support field value type {ftype} and must be in [bool, str, int, float]",
            )

    @staticmethod
    def str(ftype: Union[int, IntEnum]) -> str:
        if ftype == FieldType.BOOL:
            return FieldStrType.BOOL.value
        elif ftype == FieldType.STRING:
            return FieldStrType.STRING.value
        elif ftype == FieldType.INT:
            return FieldStrType.INT.value
        elif ftype == FieldType.FLOAT:
            return FieldStrType.FLOAT.value
        raise DashVectorException(
            code=DashVectorCode.InvalidField,
            reason=f"DashVectorSDK does not support field value type {ftype} and must be in [bool, str, int, float]",
        )

    @staticmethod
    def get_field_data_type(dtype: Type):
        if not isinstance(dtype, type):
            raise DashVectorException(
                code=DashVectorCode.InvalidField,
                reason=f"DashVectorSDK does not support field value type {dtype} and must be in [bool, str, int, float]",
            )
        if dtype not in _attr_dtype_map:
            raise DashVectorException(
                code=DashVectorCode.InvalidField,
                reason=f"DashVectorSDK does not support field value type {dtype} and must be in [bool, str, int, float]",
            )
        return _attr_dtype_map[dtype]


class IndexStrType(str, Enum):
    UNDEFINED = "IT_UNDEFINED"
    HNSW = "IT_HNSW"
    INVERT = "IT_INVERT"


class IndexType(IntEnum):
    UNDEFINED = 0
    HNSW = 1
    INVERT = 10

    @staticmethod
    def get(itype: Union[str, IndexStrType]):
        if itype == IndexStrType.UNDEFINED:
            return IndexType.UNDEFINED
        elif itype == IndexStrType.HNSW:
            return IndexType.HNSW
        elif itype == IndexStrType.INVERT:
            return IndexType.INVERT
        else:
            raise DashVectorException(
                code=DashVectorCode.InvalidIndexType, reason=f"DashVectorSDK does not support indextype {itype}"
            )

    @staticmethod
    def str(itype: Union[int, IntEnum]) -> str:
        if itype == IndexType.UNDEFINED:
            return IndexStrType.UNDEFINED.value
        elif itype == IndexType.HNSW:
            return IndexStrType.HNSW.value
        elif itype == IndexType.INVERT:
            return IndexStrType.INVERT.value
        raise DashVectorException(
            code=DashVectorCode.InvalidIndexType, reason=f"DashVectorSDK does not support indextype {itype}"
        )


_vector_dtype_map = {
    float: VectorType.FLOAT,
    int: VectorType.INT,
}

_vector_type_to_format = {
    VectorType.FLOAT: "f",
    VectorType.INT: "b",
}

_attr_dtype_map = {str: FieldType.STRING, bool: FieldType.BOOL, int: FieldType.INT, float: FieldType.FLOAT}


class DashVectorResponse(object):
    def __init__(self, response: Optional[RPCResponse] = None, *, exception: Optional[DashVectorException] = None):
        self._code = DashVectorCode.Unknown
        self._message = ""
        self._request_id = ""
        self._output = None

        self.__response = response
        self.__exception = exception

        if self.__response is None:
            self._code = DashVectorCode.Success

        if self.__response is not None and not self.__response.async_req:
            self.get()

        if self.__exception is not None:
            self._code = self.__exception.code
            self._message = self.__exception.message
            self._request_id = self.__exception.request_id

    def get(self):
        if self._code != DashVectorCode.Unknown:
            return self

        if self.__response is None:
            return self

        try:
            result = self.__response.get()
            self._request_id = result.request_id
            self._code = result.code
            self._message = result.message
            self._output = result.output
        except DashVectorException as e:
            self._code = e.code
            self._message = e.message
            self._request_id = e.request_id

        return self

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message

    @property
    def request_id(self):
        return self._request_id

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value: Any):
        self._output = value

    @property
    def response(self):
        return self.__response

    def __dict__(self):
        if self._output is None:
            return {"code": self.code, "message": self.message, "requests_id": self.request_id}
        elif isinstance(self._output, Status):
            return {
                "code": self.code,
                "message": self.message,
                "requests_id": self.request_id,
                "output": Status.str(self._output),
            }
        elif isinstance(self._output, (str, int, float)):
            return {
                "code": self.code,
                "message": self.message,
                "requests_id": self.request_id,
                "output": str(self._output),
            }
        elif isinstance(self._output, list):
            output_list = []
            for output_value in self._output:
                if isinstance(output_value, (str, int, float)):
                    output_list.append(str(output_value))
                elif hasattr(output_value, "__dict__"):
                    output_list.append(output_value.__dict__())
                elif hasattr(output_value, "__str__"):
                    output_list.append(output_value.__str__())
                else:
                    output_list.append(str(type(output_value)))
            return {"code": self.code, "message": self.message, "requests_id": self.request_id, "output": output_list}
        elif isinstance(self._output, dict):
            output_dict = {}
            for output_key, output_value in self._output.items():
                if isinstance(output_value, (str, int, float)):
                    output_dict[output_key] = str(output_value)
                elif hasattr(output_value, "__dict__"):
                    output_dict[output_key] = output_value.__dict__()
                elif hasattr(output_value, "__str__"):
                    output_dict[output_key] = output_value.__str__()
                else:
                    output_dict[output_key] = str(type(output_value))
            return {"code": self.code, "message": self.message, "requests_id": self.request_id, "output": output_dict}
        elif hasattr(self._output, "__dict__"):
            return {
                "code": self.code,
                "message": self.message,
                "requests_id": self.request_id,
                "output": self._output.__dict__(),
            }
        elif hasattr(self._output, "__str__"):
            return {
                "code": self.code,
                "message": self.message,
                "requests_id": self.request_id,
                "output": self._output.__str__(),
            }
        else:
            return {
                "code": self.code,
                "message": self.message,
                "requests_id": self.request_id,
                "output": str(type(self._output)),
            }

    def __str__(self):
        return to_json_without_ascii(self.__dict__())

    def __repr__(self):
        return self.__str__()

    def __bool__(self):
        return self.code == DashVectorCode.Success

    def __len__(self):
        return len(self._output)

    def __iter__(self):
        return self._output.__iter__()

    def __contains__(self, item):
        if hasattr(self._output, "__contains__"):
            return self.output.__contains__(item)
        else:
            raise TypeError(f"DashVectorSDK Get argument of type '{type(self.output)}' is not iterable")

    def __getitem__(self, item):
        if hasattr(self._output, "__getitem__"):
            return self.output.__getitem__(item)
        else:
            raise TypeError(f"DashVectorSDK Get '{type(self.output)}' object is not subscriptable")
