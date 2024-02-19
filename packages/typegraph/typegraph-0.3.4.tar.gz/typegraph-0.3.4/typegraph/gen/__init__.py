from .exports import aws, core, runtimes, utils
from .imports import RootImports
from .intrinsics import _decode_utf8, _encode_utf8, _list_canon_lower, _load, _store
from .types import Err, Ok
import ctypes
import pathlib
from typing import List
import wasmtime

class Root:
    
    def __init__(self, store: wasmtime.Store, import_object: RootImports) -> None:
        path = pathlib.Path(__file__).parent / ('root.core1.wasm')
        module = wasmtime.Module.from_file(store.engine, path)
        instance0 = wasmtime.Instance(store, module, []).exports(store)
        path = pathlib.Path(__file__).parent / ('root.core0.wasm')
        module = wasmtime.Module.from_file(store.engine, path)
        instance1 = wasmtime.Instance(store, module, [
            instance0["0"],
            instance0["1"],
            instance0["2"],
        ]).exports(store)
        def lowering0_callee(caller: wasmtime.Caller, arg0: int, arg1: int, arg2: int, arg3: int, arg4: int) -> None:
            ptr = arg0
            len0 = arg1
            list = _decode_utf8(self._core_memory0, caller, ptr, len0)
            ptr6 = arg2
            len7 = arg3
            result: List[str] = []
            for i8 in range(0, len7):
                base1 = ptr6 + i8 * 8
                load = _load(ctypes.c_int32, self._core_memory0, caller, base1, 0)
                load2 = _load(ctypes.c_int32, self._core_memory0, caller, base1, 4)
                ptr3 = load
                len4 = load2
                list5 = _decode_utf8(self._core_memory0, caller, ptr3, len4)
                result.append(list5)
            ret = import_object.host.expand_glob(list, result)
            if isinstance(ret, Ok):
                payload = ret.value
                _store(ctypes.c_uint8, self._core_memory0, caller, arg4, 0, 0)
                vec = payload
                len13 = len(vec)
                result12 = self._realloc0(caller, 0, 0, 4, len13 * 8)
                assert(isinstance(result12, int))
                for i14 in range(0, len13):
                    e = vec[i14]
                    base9 = result12 + i14 * 8
                    ptr10, len11 = _encode_utf8(e, self._realloc0, self._core_memory0, caller)
                    _store(ctypes.c_uint32, self._core_memory0, caller, base9, 4, len11)
                    _store(ctypes.c_uint32, self._core_memory0, caller, base9, 0, ptr10)
                _store(ctypes.c_uint32, self._core_memory0, caller, arg4, 8, len13)
                _store(ctypes.c_uint32, self._core_memory0, caller, arg4, 4, result12)
            elif isinstance(ret, Err):
                payload15 = ret.value
                _store(ctypes.c_uint8, self._core_memory0, caller, arg4, 0, 1)
                ptr16, len17 = _encode_utf8(payload15, self._realloc0, self._core_memory0, caller)
                _store(ctypes.c_uint32, self._core_memory0, caller, arg4, 8, len17)
                _store(ctypes.c_uint32, self._core_memory0, caller, arg4, 4, ptr16)
            else:
                raise TypeError("invalid variant specified for expected")
        lowering0_ty = wasmtime.FuncType([wasmtime.ValType.i32(), wasmtime.ValType.i32(), wasmtime.ValType.i32(), wasmtime.ValType.i32(), wasmtime.ValType.i32(), ], [])
        trampoline0 = wasmtime.Func(store, lowering0_ty, lowering0_callee, access_caller = True)
        core_memory0 = instance1["memory"]
        assert(isinstance(core_memory0, wasmtime.Memory))
        self._core_memory0 = core_memory0
        realloc0 = instance1["cabi_realloc"]
        assert(isinstance(realloc0, wasmtime.Func))
        self._realloc0 = realloc0
        def lowering1_callee(caller: wasmtime.Caller, arg0: int, arg1: int, arg2: int) -> None:
            ptr = arg0
            len0 = arg1
            list = _decode_utf8(self._core_memory0, caller, ptr, len0)
            ret = import_object.host.read_file(list)
            if isinstance(ret, Ok):
                payload = ret.value
                _store(ctypes.c_uint8, self._core_memory0, caller, arg2, 0, 0)
                ptr1, len2 = _list_canon_lower(payload, ctypes.c_uint8, 1, 1, self._realloc0, self._core_memory0, caller)
                _store(ctypes.c_uint32, self._core_memory0, caller, arg2, 8, len2)
                _store(ctypes.c_uint32, self._core_memory0, caller, arg2, 4, ptr1)
            elif isinstance(ret, Err):
                payload3 = ret.value
                _store(ctypes.c_uint8, self._core_memory0, caller, arg2, 0, 1)
                ptr4, len5 = _encode_utf8(payload3, self._realloc0, self._core_memory0, caller)
                _store(ctypes.c_uint32, self._core_memory0, caller, arg2, 8, len5)
                _store(ctypes.c_uint32, self._core_memory0, caller, arg2, 4, ptr4)
            else:
                raise TypeError("invalid variant specified for expected")
        lowering1_ty = wasmtime.FuncType([wasmtime.ValType.i32(), wasmtime.ValType.i32(), wasmtime.ValType.i32(), ], [])
        trampoline1 = wasmtime.Func(store, lowering1_ty, lowering1_callee, access_caller = True)
        def lowering2_callee(caller: wasmtime.Caller, arg0: int) -> None:
            ret = import_object.host.get_cwd()
            if isinstance(ret, Ok):
                payload = ret.value
                _store(ctypes.c_uint8, self._core_memory0, caller, arg0, 0, 0)
                ptr, len0 = _encode_utf8(payload, self._realloc0, self._core_memory0, caller)
                _store(ctypes.c_uint32, self._core_memory0, caller, arg0, 8, len0)
                _store(ctypes.c_uint32, self._core_memory0, caller, arg0, 4, ptr)
            elif isinstance(ret, Err):
                payload1 = ret.value
                _store(ctypes.c_uint8, self._core_memory0, caller, arg0, 0, 1)
                ptr2, len3 = _encode_utf8(payload1, self._realloc0, self._core_memory0, caller)
                _store(ctypes.c_uint32, self._core_memory0, caller, arg0, 8, len3)
                _store(ctypes.c_uint32, self._core_memory0, caller, arg0, 4, ptr2)
            else:
                raise TypeError("invalid variant specified for expected")
        lowering2_ty = wasmtime.FuncType([wasmtime.ValType.i32(), ], [])
        trampoline2 = wasmtime.Func(store, lowering2_ty, lowering2_callee, access_caller = True)
        path = pathlib.Path(__file__).parent / ('root.core2.wasm')
        module = wasmtime.Module.from_file(store.engine, path)
        instance2 = wasmtime.Instance(store, module, [
            trampoline0,
            trampoline1,
            trampoline2,
            instance0["$imports"],
        ]).exports(store)
        post_return0 = instance1["cabi_post_metatype:typegraph/aws#register-s3-runtime"]
        assert(isinstance(post_return0, wasmtime.Func))
        self._post_return0 = post_return0
        post_return1 = instance1["cabi_post_metatype:typegraph/core#finalize-typegraph"]
        assert(isinstance(post_return1, wasmtime.Func))
        self._post_return1 = post_return1
        post_return2 = instance1["cabi_post_metatype:typegraph/core#get-internal-policy"]
        assert(isinstance(post_return2, wasmtime.Func))
        self._post_return2 = post_return2
        lift_callee0 = instance1["metatype:typegraph/core#init-typegraph"]
        assert(isinstance(lift_callee0, wasmtime.Func))
        self.lift_callee0 = lift_callee0
        lift_callee1 = instance1["metatype:typegraph/core#finalize-typegraph"]
        assert(isinstance(lift_callee1, wasmtime.Func))
        self.lift_callee1 = lift_callee1
        lift_callee2 = instance1["metatype:typegraph/core#with-injection"]
        assert(isinstance(lift_callee2, wasmtime.Func))
        self.lift_callee2 = lift_callee2
        lift_callee3 = instance1["metatype:typegraph/core#refb"]
        assert(isinstance(lift_callee3, wasmtime.Func))
        self.lift_callee3 = lift_callee3
        lift_callee4 = instance1["metatype:typegraph/core#integerb"]
        assert(isinstance(lift_callee4, wasmtime.Func))
        self.lift_callee4 = lift_callee4
        lift_callee5 = instance1["metatype:typegraph/core#floatb"]
        assert(isinstance(lift_callee5, wasmtime.Func))
        self.lift_callee5 = lift_callee5
        lift_callee6 = instance1["metatype:typegraph/core#booleanb"]
        assert(isinstance(lift_callee6, wasmtime.Func))
        self.lift_callee6 = lift_callee6
        lift_callee7 = instance1["metatype:typegraph/core#stringb"]
        assert(isinstance(lift_callee7, wasmtime.Func))
        self.lift_callee7 = lift_callee7
        lift_callee8 = instance1["metatype:typegraph/core#fileb"]
        assert(isinstance(lift_callee8, wasmtime.Func))
        self.lift_callee8 = lift_callee8
        lift_callee9 = instance1["metatype:typegraph/core#listb"]
        assert(isinstance(lift_callee9, wasmtime.Func))
        self.lift_callee9 = lift_callee9
        lift_callee10 = instance1["metatype:typegraph/core#optionalb"]
        assert(isinstance(lift_callee10, wasmtime.Func))
        self.lift_callee10 = lift_callee10
        lift_callee11 = instance1["metatype:typegraph/core#unionb"]
        assert(isinstance(lift_callee11, wasmtime.Func))
        self.lift_callee11 = lift_callee11
        lift_callee12 = instance1["metatype:typegraph/core#eitherb"]
        assert(isinstance(lift_callee12, wasmtime.Func))
        self.lift_callee12 = lift_callee12
        lift_callee13 = instance1["metatype:typegraph/core#structb"]
        assert(isinstance(lift_callee13, wasmtime.Func))
        self.lift_callee13 = lift_callee13
        lift_callee14 = instance1["metatype:typegraph/core#get-type-repr"]
        assert(isinstance(lift_callee14, wasmtime.Func))
        self.lift_callee14 = lift_callee14
        lift_callee15 = instance1["metatype:typegraph/core#funcb"]
        assert(isinstance(lift_callee15, wasmtime.Func))
        self.lift_callee15 = lift_callee15
        lift_callee16 = instance1["metatype:typegraph/core#register-policy"]
        assert(isinstance(lift_callee16, wasmtime.Func))
        self.lift_callee16 = lift_callee16
        lift_callee17 = instance1["metatype:typegraph/core#with-policy"]
        assert(isinstance(lift_callee17, wasmtime.Func))
        self.lift_callee17 = lift_callee17
        lift_callee18 = instance1["metatype:typegraph/core#get-public-policy"]
        assert(isinstance(lift_callee18, wasmtime.Func))
        self.lift_callee18 = lift_callee18
        lift_callee19 = instance1["metatype:typegraph/core#get-internal-policy"]
        assert(isinstance(lift_callee19, wasmtime.Func))
        self.lift_callee19 = lift_callee19
        lift_callee20 = instance1["metatype:typegraph/core#register-context-policy"]
        assert(isinstance(lift_callee20, wasmtime.Func))
        self.lift_callee20 = lift_callee20
        lift_callee21 = instance1["metatype:typegraph/core#rename-type"]
        assert(isinstance(lift_callee21, wasmtime.Func))
        self.lift_callee21 = lift_callee21
        lift_callee22 = instance1["metatype:typegraph/core#expose"]
        assert(isinstance(lift_callee22, wasmtime.Func))
        self.lift_callee22 = lift_callee22
        lift_callee23 = instance1["metatype:typegraph/runtimes#get-deno-runtime"]
        assert(isinstance(lift_callee23, wasmtime.Func))
        self.lift_callee23 = lift_callee23
        lift_callee24 = instance1["metatype:typegraph/runtimes#register-deno-func"]
        assert(isinstance(lift_callee24, wasmtime.Func))
        self.lift_callee24 = lift_callee24
        lift_callee25 = instance1["metatype:typegraph/runtimes#register-deno-static"]
        assert(isinstance(lift_callee25, wasmtime.Func))
        self.lift_callee25 = lift_callee25
        lift_callee26 = instance1["metatype:typegraph/runtimes#get-predefined-deno-func"]
        assert(isinstance(lift_callee26, wasmtime.Func))
        self.lift_callee26 = lift_callee26
        lift_callee27 = instance1["metatype:typegraph/runtimes#import-deno-function"]
        assert(isinstance(lift_callee27, wasmtime.Func))
        self.lift_callee27 = lift_callee27
        lift_callee28 = instance1["metatype:typegraph/runtimes#register-graphql-runtime"]
        assert(isinstance(lift_callee28, wasmtime.Func))
        self.lift_callee28 = lift_callee28
        lift_callee29 = instance1["metatype:typegraph/runtimes#graphql-query"]
        assert(isinstance(lift_callee29, wasmtime.Func))
        self.lift_callee29 = lift_callee29
        lift_callee30 = instance1["metatype:typegraph/runtimes#graphql-mutation"]
        assert(isinstance(lift_callee30, wasmtime.Func))
        self.lift_callee30 = lift_callee30
        lift_callee31 = instance1["metatype:typegraph/runtimes#register-http-runtime"]
        assert(isinstance(lift_callee31, wasmtime.Func))
        self.lift_callee31 = lift_callee31
        lift_callee32 = instance1["metatype:typegraph/runtimes#http-request"]
        assert(isinstance(lift_callee32, wasmtime.Func))
        self.lift_callee32 = lift_callee32
        lift_callee33 = instance1["metatype:typegraph/runtimes#register-python-runtime"]
        assert(isinstance(lift_callee33, wasmtime.Func))
        self.lift_callee33 = lift_callee33
        lift_callee34 = instance1["metatype:typegraph/runtimes#from-python-lambda"]
        assert(isinstance(lift_callee34, wasmtime.Func))
        self.lift_callee34 = lift_callee34
        lift_callee35 = instance1["metatype:typegraph/runtimes#from-python-def"]
        assert(isinstance(lift_callee35, wasmtime.Func))
        self.lift_callee35 = lift_callee35
        lift_callee36 = instance1["metatype:typegraph/runtimes#from-python-module"]
        assert(isinstance(lift_callee36, wasmtime.Func))
        self.lift_callee36 = lift_callee36
        lift_callee37 = instance1["metatype:typegraph/runtimes#from-python-import"]
        assert(isinstance(lift_callee37, wasmtime.Func))
        self.lift_callee37 = lift_callee37
        lift_callee38 = instance1["metatype:typegraph/runtimes#register-random-runtime"]
        assert(isinstance(lift_callee38, wasmtime.Func))
        self.lift_callee38 = lift_callee38
        lift_callee39 = instance1["metatype:typegraph/runtimes#create-random-mat"]
        assert(isinstance(lift_callee39, wasmtime.Func))
        self.lift_callee39 = lift_callee39
        lift_callee40 = instance1["metatype:typegraph/runtimes#register-wasmedge-runtime"]
        assert(isinstance(lift_callee40, wasmtime.Func))
        self.lift_callee40 = lift_callee40
        lift_callee41 = instance1["metatype:typegraph/runtimes#from-wasi-module"]
        assert(isinstance(lift_callee41, wasmtime.Func))
        self.lift_callee41 = lift_callee41
        lift_callee42 = instance1["metatype:typegraph/runtimes#register-prisma-runtime"]
        assert(isinstance(lift_callee42, wasmtime.Func))
        self.lift_callee42 = lift_callee42
        lift_callee43 = instance1["metatype:typegraph/runtimes#prisma-find-unique"]
        assert(isinstance(lift_callee43, wasmtime.Func))
        self.lift_callee43 = lift_callee43
        lift_callee44 = instance1["metatype:typegraph/runtimes#prisma-find-many"]
        assert(isinstance(lift_callee44, wasmtime.Func))
        self.lift_callee44 = lift_callee44
        lift_callee45 = instance1["metatype:typegraph/runtimes#prisma-find-first"]
        assert(isinstance(lift_callee45, wasmtime.Func))
        self.lift_callee45 = lift_callee45
        lift_callee46 = instance1["metatype:typegraph/runtimes#prisma-aggregate"]
        assert(isinstance(lift_callee46, wasmtime.Func))
        self.lift_callee46 = lift_callee46
        lift_callee47 = instance1["metatype:typegraph/runtimes#prisma-count"]
        assert(isinstance(lift_callee47, wasmtime.Func))
        self.lift_callee47 = lift_callee47
        lift_callee48 = instance1["metatype:typegraph/runtimes#prisma-group-by"]
        assert(isinstance(lift_callee48, wasmtime.Func))
        self.lift_callee48 = lift_callee48
        lift_callee49 = instance1["metatype:typegraph/runtimes#prisma-create-one"]
        assert(isinstance(lift_callee49, wasmtime.Func))
        self.lift_callee49 = lift_callee49
        lift_callee50 = instance1["metatype:typegraph/runtimes#prisma-create-many"]
        assert(isinstance(lift_callee50, wasmtime.Func))
        self.lift_callee50 = lift_callee50
        lift_callee51 = instance1["metatype:typegraph/runtimes#prisma-update-one"]
        assert(isinstance(lift_callee51, wasmtime.Func))
        self.lift_callee51 = lift_callee51
        lift_callee52 = instance1["metatype:typegraph/runtimes#prisma-update-many"]
        assert(isinstance(lift_callee52, wasmtime.Func))
        self.lift_callee52 = lift_callee52
        lift_callee53 = instance1["metatype:typegraph/runtimes#prisma-upsert-one"]
        assert(isinstance(lift_callee53, wasmtime.Func))
        self.lift_callee53 = lift_callee53
        lift_callee54 = instance1["metatype:typegraph/runtimes#prisma-delete-one"]
        assert(isinstance(lift_callee54, wasmtime.Func))
        self.lift_callee54 = lift_callee54
        lift_callee55 = instance1["metatype:typegraph/runtimes#prisma-delete-many"]
        assert(isinstance(lift_callee55, wasmtime.Func))
        self.lift_callee55 = lift_callee55
        lift_callee56 = instance1["metatype:typegraph/runtimes#prisma-execute"]
        assert(isinstance(lift_callee56, wasmtime.Func))
        self.lift_callee56 = lift_callee56
        lift_callee57 = instance1["metatype:typegraph/runtimes#prisma-query-raw"]
        assert(isinstance(lift_callee57, wasmtime.Func))
        self.lift_callee57 = lift_callee57
        lift_callee58 = instance1["metatype:typegraph/runtimes#prisma-link"]
        assert(isinstance(lift_callee58, wasmtime.Func))
        self.lift_callee58 = lift_callee58
        lift_callee59 = instance1["metatype:typegraph/runtimes#prisma-migration"]
        assert(isinstance(lift_callee59, wasmtime.Func))
        self.lift_callee59 = lift_callee59
        lift_callee60 = instance1["metatype:typegraph/runtimes#register-temporal-runtime"]
        assert(isinstance(lift_callee60, wasmtime.Func))
        self.lift_callee60 = lift_callee60
        lift_callee61 = instance1["metatype:typegraph/runtimes#generate-temporal-operation"]
        assert(isinstance(lift_callee61, wasmtime.Func))
        self.lift_callee61 = lift_callee61
        lift_callee62 = instance1["metatype:typegraph/runtimes#register-typegate-materializer"]
        assert(isinstance(lift_callee62, wasmtime.Func))
        self.lift_callee62 = lift_callee62
        lift_callee63 = instance1["metatype:typegraph/runtimes#register-typegraph-materializer"]
        assert(isinstance(lift_callee63, wasmtime.Func))
        self.lift_callee63 = lift_callee63
        lift_callee64 = instance1["metatype:typegraph/utils#gen-reduceb"]
        assert(isinstance(lift_callee64, wasmtime.Func))
        self.lift_callee64 = lift_callee64
        lift_callee65 = instance1["metatype:typegraph/utils#add-graphql-endpoint"]
        assert(isinstance(lift_callee65, wasmtime.Func))
        self.lift_callee65 = lift_callee65
        lift_callee66 = instance1["metatype:typegraph/utils#add-auth"]
        assert(isinstance(lift_callee66, wasmtime.Func))
        self.lift_callee66 = lift_callee66
        lift_callee67 = instance1["metatype:typegraph/utils#add-raw-auth"]
        assert(isinstance(lift_callee67, wasmtime.Func))
        self.lift_callee67 = lift_callee67
        lift_callee68 = instance1["metatype:typegraph/utils#oauth2"]
        assert(isinstance(lift_callee68, wasmtime.Func))
        self.lift_callee68 = lift_callee68
        lift_callee69 = instance1["metatype:typegraph/utils#oauth2-without-profiler"]
        assert(isinstance(lift_callee69, wasmtime.Func))
        self.lift_callee69 = lift_callee69
        lift_callee70 = instance1["metatype:typegraph/utils#oauth2-with-extended-profiler"]
        assert(isinstance(lift_callee70, wasmtime.Func))
        self.lift_callee70 = lift_callee70
        lift_callee71 = instance1["metatype:typegraph/utils#oauth2-with-custom-profiler"]
        assert(isinstance(lift_callee71, wasmtime.Func))
        self.lift_callee71 = lift_callee71
        lift_callee72 = instance1["metatype:typegraph/utils#gen-gqlquery"]
        assert(isinstance(lift_callee72, wasmtime.Func))
        self.lift_callee72 = lift_callee72
        lift_callee73 = instance1["metatype:typegraph/aws#register-s3-runtime"]
        assert(isinstance(lift_callee73, wasmtime.Func))
        self.lift_callee73 = lift_callee73
        lift_callee74 = instance1["metatype:typegraph/aws#s3-presign-get"]
        assert(isinstance(lift_callee74, wasmtime.Func))
        self.lift_callee74 = lift_callee74
        lift_callee75 = instance1["metatype:typegraph/aws#s3-presign-put"]
        assert(isinstance(lift_callee75, wasmtime.Func))
        self.lift_callee75 = lift_callee75
        lift_callee76 = instance1["metatype:typegraph/aws#s3-list"]
        assert(isinstance(lift_callee76, wasmtime.Func))
        self.lift_callee76 = lift_callee76
        lift_callee77 = instance1["metatype:typegraph/aws#s3-upload"]
        assert(isinstance(lift_callee77, wasmtime.Func))
        self.lift_callee77 = lift_callee77
        lift_callee78 = instance1["metatype:typegraph/aws#s3-upload-all"]
        assert(isinstance(lift_callee78, wasmtime.Func))
        self.lift_callee78 = lift_callee78
    def aws(self) -> aws.Aws:
        return aws.Aws(self)
    def core(self) -> core.Core:
        return core.Core(self)
    def runtimes(self) -> runtimes.Runtimes:
        return runtimes.Runtimes(self)
    def utils(self) -> utils.Utils:
        return utils.Utils(self)
