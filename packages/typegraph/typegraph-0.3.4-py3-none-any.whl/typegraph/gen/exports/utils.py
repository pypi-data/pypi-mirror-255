from ..exports import core
from ..intrinsics import _clamp, _decode_utf8, _encode_utf8, _load, _store
from ..types import Err, Ok, Result
import ctypes
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
import wasmtime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from .. import Root

Error = core.Error
TypeId = int
@dataclass
class ReduceValue:
    inherit: bool
    payload: Optional[str]

@dataclass
class ReducePath:
    path: List[str]
    value: ReduceValue

@dataclass
class Reduce:
    paths: List[ReducePath]

@dataclass
class AuthProtocolOauth2:
    pass

@dataclass
class AuthProtocolJwt:
    pass

@dataclass
class AuthProtocolBasic:
    pass

AuthProtocol = Union[AuthProtocolOauth2, AuthProtocolJwt, AuthProtocolBasic]

@dataclass
class Auth:
    name: str
    protocol: AuthProtocol
    auth_data: List[Tuple[str, str]]

@dataclass
class QueryBodyParams:
    tg: str
    cli_version: str
    secrets: Optional[List[Tuple[str, str]]]

class Utils:
    component: 'Root'
    
    def __init__(self, component: 'Root') -> None:
        self.component = component
    def gen_reduceb(self, caller: wasmtime.Store, supertype_id: TypeId, data: Reduce) -> Result[TypeId, Error]:
        record = data
        field = record.paths
        vec15 = field
        len17 = len(vec15)
        result16 = self.component._realloc0(caller, 0, 0, 4, len17 * 24)
        assert(isinstance(result16, int))
        for i18 in range(0, len17):
            e = vec15[i18]
            base0 = result16 + i18 * 24
            record1 = e
            field2 = record1.path
            field3 = record1.value
            vec = field2
            len7 = len(vec)
            result = self.component._realloc0(caller, 0, 0, 4, len7 * 8)
            assert(isinstance(result, int))
            for i8 in range(0, len7):
                e4 = vec[i8]
                base5 = result + i8 * 8
                ptr, len6 = _encode_utf8(e4, self.component._realloc0, self.component._core_memory0, caller)
                _store(ctypes.c_uint32, self.component._core_memory0, caller, base5, 4, len6)
                _store(ctypes.c_uint32, self.component._core_memory0, caller, base5, 0, ptr)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base0, 4, len7)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base0, 0, result)
            record9 = field3
            field10 = record9.inherit
            field11 = record9.payload
            _store(ctypes.c_uint8, self.component._core_memory0, caller, base0, 8, int(field10))
            if field11 is None:
                _store(ctypes.c_uint8, self.component._core_memory0, caller, base0, 12, 0)
            else:
                payload12 = field11
                _store(ctypes.c_uint8, self.component._core_memory0, caller, base0, 12, 1)
                ptr13, len14 = _encode_utf8(payload12, self.component._realloc0, self.component._core_memory0, caller)
                _store(ctypes.c_uint32, self.component._core_memory0, caller, base0, 20, len14)
                _store(ctypes.c_uint32, self.component._core_memory0, caller, base0, 16, ptr13)
        ret = self.component.lift_callee64(caller, _clamp(supertype_id, 0, 4294967295), result16, len17)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[TypeId, Error]
        if load == 0:
            load19 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            expected = Ok(load19 & 0xffffffff)
        elif load == 1:
            load20 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load21 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr27 = load20
            len28 = load21
            result29: List[str] = []
            for i30 in range(0, len28):
                base22 = ptr27 + i30 * 8
                load23 = _load(ctypes.c_int32, self.component._core_memory0, caller, base22, 0)
                load24 = _load(ctypes.c_int32, self.component._core_memory0, caller, base22, 4)
                ptr25 = load23
                len26 = load24
                list = _decode_utf8(self.component._core_memory0, caller, ptr25, len26)
                result29.append(list)
            expected = Err(core.Error(result29))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return0(caller, ret)
        return expected
    def add_graphql_endpoint(self, caller: wasmtime.Store, graphql: str) -> Result[int, Error]:
        ptr, len0 = _encode_utf8(graphql, self.component._realloc0, self.component._core_memory0, caller)
        ret = self.component.lift_callee65(caller, ptr, len0)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[int, Error]
        if load == 0:
            load1 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            expected = Ok(load1 & 0xffffffff)
        elif load == 1:
            load2 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load3 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr9 = load2
            len10 = load3
            result: List[str] = []
            for i11 in range(0, len10):
                base4 = ptr9 + i11 * 8
                load5 = _load(ctypes.c_int32, self.component._core_memory0, caller, base4, 0)
                load6 = _load(ctypes.c_int32, self.component._core_memory0, caller, base4, 4)
                ptr7 = load5
                len8 = load6
                list = _decode_utf8(self.component._core_memory0, caller, ptr7, len8)
                result.append(list)
            expected = Err(core.Error(result))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return0(caller, ret)
        return expected
    def add_auth(self, caller: wasmtime.Store, data: Auth) -> Result[int, Error]:
        record = data
        field = record.name
        field0 = record.protocol
        field1 = record.auth_data
        ptr, len2 = _encode_utf8(field, self.component._realloc0, self.component._core_memory0, caller)
        if isinstance(field0, AuthProtocolOauth2):
            variant = 0
        elif isinstance(field0, AuthProtocolJwt):
            variant = 1
        elif isinstance(field0, AuthProtocolBasic):
            variant = 2
        else:
            raise TypeError("invalid variant specified for AuthProtocol")
        vec = field1
        len11 = len(vec)
        result = self.component._realloc0(caller, 0, 0, 4, len11 * 16)
        assert(isinstance(result, int))
        for i12 in range(0, len11):
            e = vec[i12]
            base5 = result + i12 * 16
            (tuplei,tuplei6,) = e
            ptr7, len8 = _encode_utf8(tuplei, self.component._realloc0, self.component._core_memory0, caller)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base5, 4, len8)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base5, 0, ptr7)
            ptr9, len10 = _encode_utf8(tuplei6, self.component._realloc0, self.component._core_memory0, caller)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base5, 12, len10)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base5, 8, ptr9)
        ret = self.component.lift_callee66(caller, ptr, len2, variant, result, len11)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[int, Error]
        if load == 0:
            load13 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            expected = Ok(load13 & 0xffffffff)
        elif load == 1:
            load14 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load15 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr21 = load14
            len22 = load15
            result23: List[str] = []
            for i24 in range(0, len22):
                base16 = ptr21 + i24 * 8
                load17 = _load(ctypes.c_int32, self.component._core_memory0, caller, base16, 0)
                load18 = _load(ctypes.c_int32, self.component._core_memory0, caller, base16, 4)
                ptr19 = load17
                len20 = load18
                list = _decode_utf8(self.component._core_memory0, caller, ptr19, len20)
                result23.append(list)
            expected = Err(core.Error(result23))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return0(caller, ret)
        return expected
    def add_raw_auth(self, caller: wasmtime.Store, data: str) -> Result[int, Error]:
        ptr, len0 = _encode_utf8(data, self.component._realloc0, self.component._core_memory0, caller)
        ret = self.component.lift_callee67(caller, ptr, len0)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[int, Error]
        if load == 0:
            load1 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            expected = Ok(load1 & 0xffffffff)
        elif load == 1:
            load2 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load3 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr9 = load2
            len10 = load3
            result: List[str] = []
            for i11 in range(0, len10):
                base4 = ptr9 + i11 * 8
                load5 = _load(ctypes.c_int32, self.component._core_memory0, caller, base4, 0)
                load6 = _load(ctypes.c_int32, self.component._core_memory0, caller, base4, 4)
                ptr7 = load5
                len8 = load6
                list = _decode_utf8(self.component._core_memory0, caller, ptr7, len8)
                result.append(list)
            expected = Err(core.Error(result))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return0(caller, ret)
        return expected
    def oauth2(self, caller: wasmtime.Store, service_name: str, scopes: str) -> Result[str, Error]:
        ptr, len0 = _encode_utf8(service_name, self.component._realloc0, self.component._core_memory0, caller)
        ptr1, len2 = _encode_utf8(scopes, self.component._realloc0, self.component._core_memory0, caller)
        ret = self.component.lift_callee68(caller, ptr, len0, ptr1, len2)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[str, Error]
        if load == 0:
            load3 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load4 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr5 = load3
            len6 = load4
            list = _decode_utf8(self.component._core_memory0, caller, ptr5, len6)
            expected = Ok(list)
        elif load == 1:
            load7 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load8 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr15 = load7
            len16 = load8
            result: List[str] = []
            for i17 in range(0, len16):
                base9 = ptr15 + i17 * 8
                load10 = _load(ctypes.c_int32, self.component._core_memory0, caller, base9, 0)
                load11 = _load(ctypes.c_int32, self.component._core_memory0, caller, base9, 4)
                ptr12 = load10
                len13 = load11
                list14 = _decode_utf8(self.component._core_memory0, caller, ptr12, len13)
                result.append(list14)
            expected = Err(core.Error(result))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return1(caller, ret)
        return expected
    def oauth2_without_profiler(self, caller: wasmtime.Store, service_name: str, scopes: str) -> Result[str, Error]:
        ptr, len0 = _encode_utf8(service_name, self.component._realloc0, self.component._core_memory0, caller)
        ptr1, len2 = _encode_utf8(scopes, self.component._realloc0, self.component._core_memory0, caller)
        ret = self.component.lift_callee69(caller, ptr, len0, ptr1, len2)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[str, Error]
        if load == 0:
            load3 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load4 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr5 = load3
            len6 = load4
            list = _decode_utf8(self.component._core_memory0, caller, ptr5, len6)
            expected = Ok(list)
        elif load == 1:
            load7 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load8 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr15 = load7
            len16 = load8
            result: List[str] = []
            for i17 in range(0, len16):
                base9 = ptr15 + i17 * 8
                load10 = _load(ctypes.c_int32, self.component._core_memory0, caller, base9, 0)
                load11 = _load(ctypes.c_int32, self.component._core_memory0, caller, base9, 4)
                ptr12 = load10
                len13 = load11
                list14 = _decode_utf8(self.component._core_memory0, caller, ptr12, len13)
                result.append(list14)
            expected = Err(core.Error(result))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return1(caller, ret)
        return expected
    def oauth2_with_extended_profiler(self, caller: wasmtime.Store, service_name: str, scopes: str, extension: str) -> Result[str, Error]:
        ptr, len0 = _encode_utf8(service_name, self.component._realloc0, self.component._core_memory0, caller)
        ptr1, len2 = _encode_utf8(scopes, self.component._realloc0, self.component._core_memory0, caller)
        ptr3, len4 = _encode_utf8(extension, self.component._realloc0, self.component._core_memory0, caller)
        ret = self.component.lift_callee70(caller, ptr, len0, ptr1, len2, ptr3, len4)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[str, Error]
        if load == 0:
            load5 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load6 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr7 = load5
            len8 = load6
            list = _decode_utf8(self.component._core_memory0, caller, ptr7, len8)
            expected = Ok(list)
        elif load == 1:
            load9 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load10 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr17 = load9
            len18 = load10
            result: List[str] = []
            for i19 in range(0, len18):
                base11 = ptr17 + i19 * 8
                load12 = _load(ctypes.c_int32, self.component._core_memory0, caller, base11, 0)
                load13 = _load(ctypes.c_int32, self.component._core_memory0, caller, base11, 4)
                ptr14 = load12
                len15 = load13
                list16 = _decode_utf8(self.component._core_memory0, caller, ptr14, len15)
                result.append(list16)
            expected = Err(core.Error(result))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return1(caller, ret)
        return expected
    def oauth2_with_custom_profiler(self, caller: wasmtime.Store, service_name: str, scopes: str, profiler: TypeId) -> Result[str, Error]:
        ptr, len0 = _encode_utf8(service_name, self.component._realloc0, self.component._core_memory0, caller)
        ptr1, len2 = _encode_utf8(scopes, self.component._realloc0, self.component._core_memory0, caller)
        ret = self.component.lift_callee71(caller, ptr, len0, ptr1, len2, _clamp(profiler, 0, 4294967295))
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[str, Error]
        if load == 0:
            load3 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load4 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr5 = load3
            len6 = load4
            list = _decode_utf8(self.component._core_memory0, caller, ptr5, len6)
            expected = Ok(list)
        elif load == 1:
            load7 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load8 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr15 = load7
            len16 = load8
            result: List[str] = []
            for i17 in range(0, len16):
                base9 = ptr15 + i17 * 8
                load10 = _load(ctypes.c_int32, self.component._core_memory0, caller, base9, 0)
                load11 = _load(ctypes.c_int32, self.component._core_memory0, caller, base9, 4)
                ptr12 = load10
                len13 = load11
                list14 = _decode_utf8(self.component._core_memory0, caller, ptr12, len13)
                result.append(list14)
            expected = Err(core.Error(result))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return1(caller, ret)
        return expected
    def gen_gqlquery(self, caller: wasmtime.Store, params: QueryBodyParams) -> Result[str, Error]:
        record = params
        field = record.tg
        field0 = record.cli_version
        field1 = record.secrets
        ptr, len2 = _encode_utf8(field, self.component._realloc0, self.component._core_memory0, caller)
        ptr3, len4 = _encode_utf8(field0, self.component._realloc0, self.component._core_memory0, caller)
        if field1 is None:
            variant = 0
            variant14 = 0
            variant15 = 0
        else:
            payload5 = field1
            vec = payload5
            len12 = len(vec)
            result = self.component._realloc0(caller, 0, 0, 4, len12 * 16)
            assert(isinstance(result, int))
            for i13 in range(0, len12):
                e = vec[i13]
                base6 = result + i13 * 16
                (tuplei,tuplei7,) = e
                ptr8, len9 = _encode_utf8(tuplei, self.component._realloc0, self.component._core_memory0, caller)
                _store(ctypes.c_uint32, self.component._core_memory0, caller, base6, 4, len9)
                _store(ctypes.c_uint32, self.component._core_memory0, caller, base6, 0, ptr8)
                ptr10, len11 = _encode_utf8(tuplei7, self.component._realloc0, self.component._core_memory0, caller)
                _store(ctypes.c_uint32, self.component._core_memory0, caller, base6, 12, len11)
                _store(ctypes.c_uint32, self.component._core_memory0, caller, base6, 8, ptr10)
            variant = 1
            variant14 = result
            variant15 = len12
        ret = self.component.lift_callee72(caller, ptr, len2, ptr3, len4, variant, variant14, variant15)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[str, Error]
        if load == 0:
            load16 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load17 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr18 = load16
            len19 = load17
            list = _decode_utf8(self.component._core_memory0, caller, ptr18, len19)
            expected = Ok(list)
        elif load == 1:
            load20 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load21 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr28 = load20
            len29 = load21
            result30: List[str] = []
            for i31 in range(0, len29):
                base22 = ptr28 + i31 * 8
                load23 = _load(ctypes.c_int32, self.component._core_memory0, caller, base22, 0)
                load24 = _load(ctypes.c_int32, self.component._core_memory0, caller, base22, 4)
                ptr25 = load23
                len26 = load24
                list27 = _decode_utf8(self.component._core_memory0, caller, ptr25, len26)
                result30.append(list27)
            expected = Err(core.Error(result30))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return1(caller, ret)
        return expected
