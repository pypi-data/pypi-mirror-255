##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.891531                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.exception

class MetaflowAzureAuthenticationError(metaflow.exception.MetaflowException, metaclass=type):
    ...

class MetaflowAzureResourceError(metaflow.exception.MetaflowException, metaclass=type):
    ...

class MetaflowAzurePackageError(metaflow.exception.MetaflowException, metaclass=type):
    ...

class MetaflowInternalError(metaflow.exception.MetaflowException, metaclass=type):
    ...

class MetaflowException(Exception, metaclass=type):
    def __init__(self, msg = "", lineno = None):
        ...
    def __str__(self):
        ...
    ...

def check_azure_deps(func):
    """
    The decorated function checks Azure dependencies (as needed for Azure storage backend). This includes
    various Azure SDK packages, as well as a Python version of >3.6
    
    We also tune some warning and logging configurations to reduce excessive log lines from Azure SDK.
    """
    ...

def parse_azure_full_path(blob_full_uri):
    """
    Parse an Azure Blob Storage path str into a tuple (container_name, blob).
    
    Expected format is: <container_name>/<blob>
    
    This is sometimes used to parse an Azure sys root, in which case:
    
    - <container_name> is the Azure Blob Storage container name
    - <blob> is effectively a blob_prefix, a subpath within the container in which blobs will live
    
    Blob may be None, if input looks like <container_name>. I.e. no slashes present.
    
    We take a strict validation approach, doing no implicit string manipulations on
    the user's behalf.  Path manipulations by themselves are complicated enough without
    adding magic.
    
    We provide clear error messages so the user knows exactly how to fix any validation error.
    """
    ...

def process_exception(*args, **kwargs):
    ...

def handle_exceptions(func):
    """
    This is a decorator leveraging the logic from process_exception()
    """
    ...

def create_cacheable_default_azure_credentials(*args, **kwargs):
    ...

def create_static_token_credential(*args, **kwargs):
    ...

