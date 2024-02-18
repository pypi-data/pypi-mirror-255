from abc import abstractmethod
from typing import Any, Generic, TypeVar


INT_PREFIX= bytes([0,0,0,0])
STR_PREFIX= bytes([0,0,0,1])
BOOL_PREFIX= bytes([0,0,1,1])
BYTES_PREFIX= bytes([0,1,0,0])

prefix_length= 4
def split_prefix(value: bytes):
    return value[:prefix_length], value[prefix_length:]

def extract_prefix(value: bytes):
    return value[:prefix_length]

def extract_payload(value: bytes):
    return value[prefix_length:]

T = TypeVar("T")




class BytesConverter(Generic[T]):
    @staticmethod
    def from_serialized(value: bytes) -> 'BytesConverter':
        prefix= extract_prefix(value)
        if prefix == INT_PREFIX:
            return int_serializer
        if prefix == STR_PREFIX:
            return string_serializer
        if prefix == BOOL_PREFIX:
            return bool_serializer
        if prefix == BYTES_PREFIX:
            return bytes_serializer
        raise ValueError(f"Unknonw type prefix: {prefix}")

    @staticmethod
    def from_deserialized(value: Any)-> 'BytesConverter':
        if isinstance(value, bool):
            return bool_serializer        
        if isinstance(value, int):
            return int_serializer
        if isinstance(value, str):
            return string_serializer
        if isinstance(value, bytes):
            return bytes_serializer
        raise ValueError(f"Unsupported type {type(value)}")
    @abstractmethod
    def serialize(self, value: T) -> bytes: ...
    
    @abstractmethod
    def deserialize(self, value: bytes) -> T: ...

class BytesSerializer(BytesConverter[bytes]):
    def serialize(self, value: bytes) -> bytes:
        return BYTES_PREFIX + value
    
    def deserialize(self, value: bytes) -> bytes:
        return extract_payload(value)
    
class IntSerializer(BytesConverter[int]):
    def serialize(self, value: int) -> bytes:
        return INT_PREFIX + value.to_bytes(4, 'big')
    
    def deserialize(self, value: bytes) -> int:
        return int.from_bytes(extract_payload(value), 'big')
    
class StringSerializer(BytesConverter[str]):
    def serialize(self, value: str) -> bytes:
        return STR_PREFIX + value.encode('utf-8')
    
    def deserialize(self, value: bytes) -> str:
        return extract_payload(value).decode('utf-8')
    
class BoolSerializer(BytesConverter[bool]):
    def serialize(self, value: bool) -> bytes:
        return BOOL_PREFIX + value.to_bytes(1, 'big')
    
    def deserialize(self, value: bytes) -> bool:
        return bool.from_bytes(extract_payload(value), 'big')
    
int_serializer= IntSerializer()
string_serializer= StringSerializer()
bool_serializer= BoolSerializer()
bytes_serializer= BytesSerializer()
