from abc import abstractmethod
from typing import Any, overload, Generic, TypeVar

from datasets import Dataset,DatasetDict, IterableDataset, IterableDatasetDict,load_dataset
from cryptography.fernet import Fernet
import boto3
from huggingface_hub import HfFileSystem, repo_info, delete_repo, create_repo
from huggingface_hub.utils._errors import RepositoryNotFoundError
import base64
import time

from encrypted_datasets.src.serializer import BytesConverter


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
        return {k: f.encrypt(BytesConverter.from_deserialized(v).serialize(v)) for k, v in row.items()}
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
    
    def decrypt_item(item: Any):
        decrypted= f.decrypt(item)
        return BytesConverter.from_serialized(decrypted).deserialize(decrypted)
    
    def decrypt_row(row: dict[str, Any]):
        return {k: decrypt_item(v) for k, v in row.items()}
    
    return dataset.map(decrypt_row)


class UnencryptedDatasetWrapper():
    def __init__(self, data_key:bytes, dataset: DatasetDict | Dataset):
        self.data_key= data_key
        self.ds= dataset


    @staticmethod
    def new(hf_dataset: DatasetDict | Dataset ):
        return UnencryptedDatasetWrapper(
            data_key=Fernet.generate_key(),
            dataset=hf_dataset,
        )
    
    def copy_with(self, new_datset: DatasetDict | Dataset):
        return UnencryptedDatasetWrapper(
            data_key=self.data_key,
            dataset=new_datset,
        )

    def __encrypt_data_key(self, kms_key_id:str, kms_client):
        response= kms_client.encrypt(
            KeyId=kms_key_id,
            Plaintext=self.data_key
        )

        return response['CiphertextBlob']

    def encrypt(self,kms_key_id:str, kms_client):
        encrypted_dataset= encrypt_dataset(self.ds, self.data_key)

        encrypted_key= self.__encrypt_data_key(
            kms_key_id=kms_key_id,
            kms_client=kms_client,
        )
        return EncryptedDatasetWrapper(
            encrypted_data_key=encrypted_key,
            ds=encrypted_dataset,
        )

class EncryptedDatasetWrapper():
    def __init__(self, encrypted_data_key:bytes, ds: DatasetDict | Dataset):
        self.encrypted_data_key=encrypted_data_key
        self.__ds=ds


    __data_key_filename= 'data_key'

    @staticmethod
    def __get_data_key_path(hf_repo_id:str):
        return f'datasets/{hf_repo_id}/{EncryptedDatasetWrapper.__data_key_filename}'

    @staticmethod
    def __load_data_key(hf_repo_id:str, token:str|None):
        fs= HfFileSystem(token=token)
        path= EncryptedDatasetWrapper.__get_data_key_path(hf_repo_id)

        if not fs.exists(path):
            return None

        with fs.open(path, 'r') as data_key_file:
            data_key_str= data_key_file.readline()
            return base64.b64decode(bytes.fromhex(str(data_key_str)))

    def __upload_data_key(self, hf_repo_id:str, data_key:bytes, token:str|None):
        fs= HfFileSystem(token=token)
        path= EncryptedDatasetWrapper.__get_data_key_path(hf_repo_id)

        if fs.exists(path):
            raise ValueError('data key already exists')

        dat_key_str= base64.b64encode(data_key).hex()
        
        with fs.open(path, 'w') as data_key_file:
            data_key_file.write(dat_key_str)

    @staticmethod
    def load(hf_repo_id:str, token: str | None):
        ds = load_dataset(hf_repo_id, token=token)
        
        assert(isinstance(ds, DatasetDict) or isinstance(ds, Dataset))
        
        encrypted_data_key= EncryptedDatasetWrapper.__load_data_key(hf_repo_id= hf_repo_id, token=token)

        if encrypted_data_key is None:
            raise ValueError(f'No {EncryptedDatasetWrapper.__data_key_filename} in repo {hf_repo_id}')
        
        return EncryptedDatasetWrapper(
            encrypted_data_key=encrypted_data_key,
            ds=ds,
        )
        
    def __does_repo_exist(self, hf_repo_id:str, token:str|None):
        try:
            repo_info(hf_repo_id, token=token, repo_type='dataset')
            return True
        except RepositoryNotFoundError:
            return False

    def push_to_hub(self,hf_repo_id:str, token:str|None, commit_message:str|None=None):
        if not self.__does_repo_exist(hf_repo_id, token=token):
            create_repo(hf_repo_id, token=token, repo_type='dataset')

        current_remote_data_key= EncryptedDatasetWrapper.__load_data_key(hf_repo_id=hf_repo_id, token=token)

        if current_remote_data_key is not None and current_remote_data_key != self.encrypted_data_key:
            raise ValueError('local data key does not match remote data key')
        
        if current_remote_data_key is None:
            try:
                self.__upload_data_key(
                    hf_repo_id=hf_repo_id,
                    data_key=self.encrypted_data_key,
                    token=token
                )
            except Exception as e:
                raise Exception(f'Failed to upload data key to repo {hf_repo_id}: {e}')

        self.__ds.push_to_hub(hf_repo_id, token=token, commit_message=commit_message)

    
    def __decrypt_data_key(self, kms_key_id:str, kms_client):
        response= kms_client.decrypt(
            KeyId=kms_key_id,
            CiphertextBlob=self.encrypted_data_key
        )

        return response['Plaintext']

    def decrypt(self, kms_key_id:str, kms_client):
        decrypted_key= self.__decrypt_data_key(
            kms_key_id=kms_key_id,
            kms_client=kms_client
        )

        decrypted_dataset= decrypt_dataset(self.__ds, decrypted_key)

        return UnencryptedDatasetWrapper(
            data_key=decrypted_key,
            dataset=decrypted_dataset,
        )
        
    


    
