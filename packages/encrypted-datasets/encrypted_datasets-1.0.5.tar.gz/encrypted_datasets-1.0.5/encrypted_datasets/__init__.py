from abc import abstractmethod
from typing import Any, overload, Generic, TypeVar

from datasets import Dataset,DatasetDict, IterableDataset, IterableDatasetDict,load_dataset
from cryptography.fernet import Fernet
import boto3
from huggingface_hub import HfFileSystem, repo_info, create_repo
from huggingface_hub.utils._errors import RepositoryNotFoundError
import base64
import time
import pandas as pd

from encrypted_datasets.src.serializer import deserialize_value, serialize_value


@overload
def encrypt_dataset(dataset: Dataset, key:str|bytes) -> Dataset: ...

@overload
def encrypt_dataset(dataset: DatasetDict, key:str|bytes) -> DatasetDict: ...

@overload
def encrypt_dataset(dataset: IterableDatasetDict, key:str|bytes) -> IterableDatasetDict: ...

@overload
def encrypt_dataset(dataset: IterableDataset, key:str|bytes) -> IterableDataset: ...

def encrypt_dataset(dataset:  Dataset | DatasetDict | IterableDatasetDict | IterableDataset, key:str|bytes):
    f= Fernet(key)
    def encrypt_row(row: dict[str, Any]):
        return {k: f.encrypt(serialize_value(v)) for k, v in row.items()}
    return dataset.map(encrypt_row)


@overload
def decrypt_dataset(dataset: Dataset, key:str|bytes) -> Dataset: ...

@overload
def decrypt_dataset(dataset: DatasetDict, key:str|bytes) -> DatasetDict: ...

@overload
def decrypt_dataset(dataset: IterableDatasetDict, key:str|bytes) -> IterableDatasetDict: ...

@overload
def decrypt_dataset(dataset: IterableDataset, key:str|bytes) -> IterableDataset: ...

def decrypt_dataset(dataset: Dataset | DatasetDict | IterableDatasetDict | IterableDataset, key:str|bytes):
    f= Fernet(key)
    
    def decrypt_row(row: dict[str, Any]):
        return {k: deserialize_value(f.decrypt(v)) for k, v in row.items()}
    
    return dataset.map(decrypt_row)

encrypted_data_key_column='encrypted_data_key'


class Cypher:
    @abstractmethod
    def encrypt(self, data:bytes)-> bytes: ...
    
    @abstractmethod    
    def decrypt(self, data:bytes)-> bytes: ...
    
class FernetCypher(Cypher):
    def __init__(self, fernet:Fernet):
        self.f= fernet
        
    @staticmethod
    def from_key(key:str|bytes)-> 'FernetCypher':
        return FernetCypher(Fernet(key))
    
    def encrypt(self, data:bytes)-> bytes:
        return self.f.encrypt(data)
    
    def decrypt(self, data:bytes)-> bytes:
        return self.f.decrypt(data)
    
class KMSCypher(Cypher):
    def __init__(self, key_id:str, client):
        self.key_id= key_id
        self.client= client
    
    def encrypt(self, data:bytes)-> bytes:
        response= self.client.encrypt(
            KeyId=self.key_id,
            Plaintext=data
        )
        return response['CiphertextBlob']
    
    def decrypt(self, data:bytes)-> bytes:
        response= self.client.decrypt(
            KeyId=self.key_id,
            CiphertextBlob=data
        )
        return response['Plaintext']

class EncryptedDataset():
    def __init__(self, encrypted_hf_ds: DatasetDict | Dataset):
        if EncryptedDataset.__get_encrypted_data_key_from_ds(encrypted_hf_ds) is None:
            raise ValueError("Dataset must contain an encrypted data key")
        
        self.__ds=encrypted_hf_ds

    # __data_key_filename= 'data_key'
    
    @staticmethod
    def __add_data_key_to_ds_or_dict(ds_or_dict: Dataset | DatasetDict, data_key:bytes):
        print(f'added data key: {data_key}')
        if isinstance(ds_or_dict, Dataset):
            return EncryptedDataset.__add_data_key_to_ds(ds_or_dict, data_key)
        else:
            return DatasetDict({k: EncryptedDataset.__add_data_key_to_ds(ds, data_key) for k, ds in ds_or_dict.items()})
    @staticmethod
    def __add_data_key_to_ds(ds: Dataset, data_key:bytes)->Dataset:
        # type: ignore
        return ds.add_column(encrypted_data_key_column, [data_key]* len(ds))
    
    @staticmethod
    def encrypt(unencrypted_ds: DatasetDict | Dataset, cypher: Cypher)-> 'EncryptedDataset':
        data_key= Fernet.generate_key()
        print('generated data key: ', data_key)
        encrypted_dataset= encrypt_dataset(unencrypted_ds, data_key)
        
        encrypted_data_key= cypher.encrypt(data_key)
        
        encrypted_dataset_with_key= EncryptedDataset.__add_data_key_to_ds_or_dict(encrypted_dataset, encrypted_data_key)
        return EncryptedDataset(encrypted_dataset_with_key)
    
    @staticmethod
    def __get_encrypted_data_key_from_ds(ds: Dataset | DatasetDict)-> bytes|None:
        if isinstance(ds, DatasetDict):
            if len(ds.keys())==0:
                return None
            
            dataset = ds[list(ds.keys())[0]]
        else:
            dataset= ds
        
        if encrypted_data_key_column not in dataset.column_names:
            return None
        return dataset[encrypted_data_key_column][0]
    
    @property
    def encrypted_data_key(self)-> bytes:
        key= EncryptedDataset.__get_encrypted_data_key_from_ds(self.__ds)
        assert key is not None
        return key


    @staticmethod
    def load(hf_repo_id:str, token: str | None):
        ds = load_dataset(hf_repo_id, token=token)
        assert(isinstance(ds, DatasetDict) or isinstance(ds, Dataset))
        return EncryptedDataset(
            encrypted_hf_ds=ds,
        )
        
    # def __does_repo_exist(self, hf_repo_id:str, token:str|None):
    #     try:
    #         repo_info(hf_repo_id, token=token, repo_type='dataset')
    #         return True
    #     except RepositoryNotFoundError:
    #         return False

    def push_to_hub(self,hf_repo_id:str, token:str|None, commit_message:str|None=None):
        # if not self.__does_repo_exist(hf_repo_id, token=token):
        #     create_repo(hf_repo_id, token=token, repo_type='dataset')


        self.__ds.push_to_hub(hf_repo_id, token=token, commit_message=commit_message)


    def decrypt(self, cypher: Cypher):
        print(f'got data key: {self.encrypted_data_key}')

        decrypted_key= cypher.decrypt(self.encrypted_data_key)
        print('decrypted data key: ', decrypted_key)
        
        ds_without_key= self.__ds.remove_columns(encrypted_data_key_column)

        decrypted_dataset= decrypt_dataset(ds_without_key, decrypted_key)

        return decrypted_dataset
        
    


    
