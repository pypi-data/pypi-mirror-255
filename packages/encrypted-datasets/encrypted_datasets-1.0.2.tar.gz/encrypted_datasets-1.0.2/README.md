## Installation

```bash
pip install encrypted-datasets
```

## Usage

### Raw string key

```python
from datasets import load_dataset
from encrypted_datasets import encrypt_dataset, decrypt_dataset

huggingface_api_token = 'API_TOKEN'
downloaded_dataset = load_dataset('organization/dataset_repo', token=huggingface_api_token)
key = 'Your Symetric encryption key'

decrypted_dataset = decrypt_dataset(downloaded_dataset, key)

# Make modifications to decrypted_dataset...

re_encrypted_dataset = encrypt_dataset(decrypted_dataset, key)

re_encrypted_dataset.push_to_hub('organization/dataset_repo',token=huggingface_api_token)
```

### AWS Key management service key

In this method, you use an AWS KMS key to encrypt data keys that are stored in huggingface with the data.

#### Create new encryped dataset and upload it to huggingface hub

```python
from encrypted_datasets import UnencryptedDatasetWrapper
import boto3

kms_client = boto3.client('kms')
kms_key_id = '<KMS_KEY_ID>'

dataset = Dataset.from_pandas(...)

unencrypted_wrapper = UnencryptedDatasetWrapper.new(dataset)

encrypted_wrapper = unencrypted.encrypt(
    kms_client=kms_client,
    kms_key_id=kms_key_id
)

encrypted_wrapper.push_to_hub('organization/repo_id', token='<ACCESS_TOKEN>')
```

#### Load encrypted dataset, modify it, and reupload

```python
from encrypted_datasets import EncryptedDatasetWrapper
import boto3

kms_client = boto3.client('kms')
kms_key_id = '<KMS_KEY_ID>'

encrypted_wrapper = EncryptedDatasetWrapper.load('cyvidia/test_32', token='')

decrypted_wrapper = encrypted_wrapper.decrypt(
    kms_client=kms_client,
    kms_key_id=kms_key_id
)

dataset = decrypted_wrapper.ds

# Make modifications to decrypted_dataset...

decrypted_wrapper= decrypted_wrapper.copy_with(new_dataset)

encrypted_wrapper = decrypted_wrapper.encrypt(
    kms_client=kms_client,
    kms_key_id=kms_key_id
)

encrypted_wrapper.push_to_hub('organization/repo_id', token='<ACCESS_TOKEN>')

```
