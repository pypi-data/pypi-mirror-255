##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.891952                                        #
##################################################################################

from __future__ import annotations


class MetaflowException(Exception, metaclass=type):
    def __init__(self, msg = "", lineno = None):
        ...
    def __str__(self):
        ...
    ...

AZURE_STORAGE_BLOB_SERVICE_ENDPOINT: None

def create_cacheable_default_azure_credentials(*args, **kwargs):
    ...

def check_azure_deps(func):
    """
    The decorated function checks Azure dependencies (as needed for Azure storage backend). This includes
    various Azure SDK packages, as well as a Python version of >3.6
    
    We also tune some warning and logging configurations to reduce excessive log lines from Azure SDK.
    """
    ...

AZURE_CLIENT_CONNECTION_DATA_BLOCK_SIZE: int

AZURE_CLIENT_MAX_SINGLE_GET_SIZE_MB: int

AZURE_CLIENT_MAX_SINGLE_PUT_SIZE_MB: int

AZURE_CLIENT_MAX_CHUNK_GET_SIZE_MB: int

BYTES_IN_MB: int

def get_azure_blob_service_client(credential = None, credential_is_cacheable = False, max_single_get_size = 33554432, max_single_put_size = 67108864, max_chunk_get_size = 16777216, connection_data_block_size = 262144):
    """
    Returns a azure.storage.blob.BlobServiceClient.
    
    The value adds are:
    - connection caching (see _ClientCache)
    - auto storage account URL detection
    - auto credential handling (pull SAS token from environment, OR DefaultAzureCredential)
    - sensible default values for Azure SDK tunables
    """
    ...

