# import uuid
# from datetime import datetime, date
# from dataclasses import dataclass
# from decimal import Decimal
# from typing import cast, Type, Any
#
# import pytest  # noqa: pycharm
#
# from kaiju_tools.encoding import ENCODERS, SerializerInterface, Serializable
# from kaiju_tools.rpc import RPCRequest, RPCResponse, RPCError
# from kaiju_tools.exceptions import InternalError
#
#
# @pytest.fixture(params=tuple(ENCODERS.keys()))
# def encoder(request) -> SerializerInterface:
#     return ENCODERS[request.param]()
#
#
# @dataclass
# class _Serialized(Serializable):
#
#     a: int
#     b: int
#
#     def getstate(self) -> dict:
#         return {'a': self.a, 'b': self.b}
#
#
# @pytest.mark.parametrize('value, result', [
#     (42, 42),
#     (1.917, 1.917),
#     (True, True),
#     ('уникоде', 'уникоде'),
#     (None, None),
#     (['some', 3, 'value'], ['some', 3, 'value']),
#     (('some', 3, 'value'), ['some', 3, 'value']),
#     ({'some'}, ['some']),
#     (frozenset({'some'}), ['some']),
#     ({'key': 'value'}, {'key': 'value'}),
#     (uuid.UUID(int=1), str(uuid.UUID(int=1))),
#     (Decimal(1.0), 1.0),
#     (date(year=2012, month=1, day=1), '2012-01-01'),
#     (datetime(year=2012, month=1, day=1, hour=1, minute=1, second=1), '2012-01-01T01:01:01'),
#     (_Serialized(a=1, b=2), {'a': 1, 'b': 2}),
#     ([(_Serialized(a=1, b=2),), _Serialized(a=1, b=2)], [[{'a': 1, 'b': 2}], {'a': 1, 'b': 2}]),
#     (
#         RPCRequest(id=1, method='do.echo', params={'data': True}),
#         {'jsonrpc': '2.0', 'id': 1, 'method': 'do.echo', 'params': {'data': True}}
#     ),
#     (
#         RPCResponse(id=1, result={'data': True}),
#         {'jsonrpc': '2.0', 'id': 1, 'result': {'data': True}}
#     ),
#     (
#         RPCError(id=1, error=InternalError('Test', base_exc=ValueError('!'))),
#         {'jsonrpc': '2.0', 'id': 1, 'error': {'code': -32603, 'message': 'Test', 'data': {'type': 'InternalError'}}}
#     ),
# ], ids=[
#     'int',
#     'float',
#     'bool',
#     'unicode',
#     'null',
#     'list',
#     'tuple',
#     'set',
#     'frozenset',
#     'dict',
#     'uuid',
#     'decimal',
#     'date',
#     'datetime',
#     'serialized',
#     'nested types',
#     'rpc request',
#     'rpc result',
#     'rpc error'
# ])
# def test_encoding(encoder, value, result, logger):
#     value = encoder.dumps(value)
#     logger.debug(value)
#     value = encoder.loads(value)
#     assert value == result
