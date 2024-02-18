##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.826077                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import typing
    import metaflow.plugins.datatools.s3.s3
    import io
    import metaflow._vendor.click.types
    import metaflow.parameters

class MetaflowException(Exception, metaclass=type):
    def __init__(self, msg = "", lineno = None):
        ...
    def __str__(self):
        ...
    ...

class DelayedEvaluationParameter(object, metaclass=type):
    def __init__(self, name, field, fun):
        ...
    def __call__(self, return_str = False):
        ...
    ...

class DeployTimeField(object, metaclass=type):
    def __init__(self, parameter_name, parameter_type, field, fun, return_str = True, print_representation = None):
        ...
    def __call__(self, deploy_time = False):
        ...
    @property
    def description(self):
        ...
    def __str__(self):
        ...
    def __repr__(self):
        ...
    ...

class Parameter(object, metaclass=type):
    def __init__(self, name: str, default: typing.Union[str, float, int, bool, typing.Dict[str, typing.Any], typing.Callable[[], typing.Union[str, float, int, bool, typing.Dict[str, typing.Any]]], None] = None, type: typing.Union[typing.Type[str], typing.Type[float], typing.Type[int], typing.Type[bool], metaflow.parameters.JSONTypeClass, None] = None, help: typing.Optional[str] = None, required: bool = False, show_default: bool = True, **kwargs: typing.Dict[str, typing.Any]):
        ...
    def __repr__(self):
        ...
    def __str__(self):
        ...
    def option_kwargs(self, deploy_mode):
        ...
    def load_parameter(self, v):
        ...
    @property
    def is_string_type(self):
        ...
    def __getitem__(self, x):
        ...
    ...

class ParameterContext(tuple, metaclass=type):
    @staticmethod
    def __new__(_cls, flow_name: str, user_name: str, parameter_name: str, logger: typing.Callable[..., None], ds_type: str):
        """
        Create new instance of ParameterContext(flow_name, user_name, parameter_name, logger, ds_type)
        """
        ...
    def __repr__(self):
        """
        Return a nicely formatted representation string
        """
        ...
    def __getnewargs__(self):
        """
        Return self as a plain tuple.  Used by copy and pickle.
        """
        ...
    def __init__(self, flow_name: str, user_name: str, parameter_name: str, logger: typing.Callable[..., None], ds_type: str):
        ...
    ...

class Local(object, metaclass=type):
    @classmethod
    def get_root_from_config(cls, echo, create_on_absent = True):
        ...
    def __init__(self):
        """
        Initialize a new context for Local file operations. This object is based used as
        a context manager for a with statement.
        """
        ...
    def __enter__(self):
        ...
    def __exit__(self, *args):
        ...
    def get(self, key = None, return_missing = False):
        ...
    def put(self, key, obj, overwrite = True):
        ...
    def info(self, key = None, return_missing = False):
        ...
    ...

class S3(object, metaclass=type):
    @classmethod
    def get_root_from_config(cls, echo, create_on_absent = True):
        ...
    def __enter__(self) -> metaflow.plugins.datatools.s3.s3.S3:
        ...
    def __exit__(self, *args):
        ...
    def close(self):
        """
        Delete all temporary files downloaded in this context.
        """
        ...
    def list_paths(self, keys: typing.Optional[typing.Iterable[str]] = None) -> typing.List[metaflow.plugins.datatools.s3.s3.S3Object]:
        """
        List the next level of paths in S3.
        
        If multiple keys are specified, listings are done in parallel. The returned
        S3Objects have `.exists == False` if the path refers to a prefix, not an
        existing S3 object.
        
        For instance, if the directory hierarchy is
        ```
        a/0.txt
        a/b/1.txt
        a/c/2.txt
        a/d/e/3.txt
        f/4.txt
        ```
        The `list_paths(['a', 'f'])` call returns
        ```
        a/0.txt (exists == True)
        a/b/ (exists == False)
        a/c/ (exists == False)
        a/d/ (exists == False)
        f/4.txt (exists == True)
        ```
        
        Parameters
        ----------
        keys : Iterable[str], optional, default None
            List of paths.
        
        Returns
        -------
        List[S3Object]
            S3Objects under the given paths, including prefixes (directories) that
            do not correspond to leaf objects.
        """
        ...
    def list_recursive(self, keys: typing.Optional[typing.Iterable[str]] = None) -> typing.List[metaflow.plugins.datatools.s3.s3.S3Object]:
        """
        List all objects recursively under the given prefixes.
        
        If multiple keys are specified, listings are done in parallel. All objects
        returned have `.exists == True` as this call always returns leaf objects.
        
        For instance, if the directory hierarchy is
        ```
        a/0.txt
        a/b/1.txt
        a/c/2.txt
        a/d/e/3.txt
        f/4.txt
        ```
        The `list_paths(['a', 'f'])` call returns
        ```
        a/0.txt (exists == True)
        a/b/1.txt (exists == True)
        a/c/2.txt (exists == True)
        a/d/e/3.txt (exists == True)
        f/4.txt (exists == True)
        ```
        
        Parameters
        ----------
        keys : Iterable[str], optional, default None
            List of paths.
        
        Returns
        -------
        List[S3Object]
            S3Objects under the given paths.
        """
        ...
    def info(self, key: typing.Optional[str] = None, return_missing: bool = False) -> metaflow.plugins.datatools.s3.s3.S3Object:
        """
        Get metadata about a single object in S3.
        
        This call makes a single `HEAD` request to S3 which can be
        much faster than downloading all data with `get`.
        
        Parameters
        ----------
        key : str, optional, default None
            Object to query. It can be an S3 url or a path suffix.
        return_missing : bool, default False
            If set to True, do not raise an exception for a missing key but
            return it as an `S3Object` with `.exists == False`.
        
        Returns
        -------
        S3Object
            An S3Object corresponding to the object requested. The object
            will have `.downloaded == False`.
        """
        ...
    def info_many(self, keys: typing.Iterable[str], return_missing: bool = False) -> typing.List[metaflow.plugins.datatools.s3.s3.S3Object]:
        """
        Get metadata about many objects in S3 in parallel.
        
        This call makes a single `HEAD` request to S3 which can be
        much faster than downloading all data with `get`.
        
        Parameters
        ----------
        keys : Iterable[str]
            Objects to query. Each key can be an S3 url or a path suffix.
        return_missing : bool, default False
            If set to True, do not raise an exception for a missing key but
            return it as an `S3Object` with `.exists == False`.
        
        Returns
        -------
        List[S3Object]
            A list of S3Objects corresponding to the paths requested. The
            objects will have `.downloaded == False`.
        """
        ...
    def get(self, key: typing.Union[str, metaflow.plugins.datatools.s3.s3.S3GetObject, None] = None, return_missing: bool = False, return_info: bool = True) -> metaflow.plugins.datatools.s3.s3.S3Object:
        """
        Get a single object from S3.
        
        Parameters
        ----------
        key : Union[str, S3GetObject], optional, default None
            Object to download. It can be an S3 url, a path suffix, or
            an S3GetObject that defines a range of data to download. If None, or
            not provided, gets the S3 root.
        return_missing : bool, default False
            If set to True, do not raise an exception for a missing key but
            return it as an `S3Object` with `.exists == False`.
        return_info : bool, default True
            If set to True, fetch the content-type and user metadata associated
            with the object at no extra cost, included for symmetry with `get_many`
        
        Returns
        -------
        S3Object
            An S3Object corresponding to the object requested.
        """
        ...
    def get_many(self, keys: typing.Iterable[typing.Union[str, metaflow.plugins.datatools.s3.s3.S3GetObject]], return_missing: bool = False, return_info: bool = True) -> typing.List[metaflow.plugins.datatools.s3.s3.S3Object]:
        """
        Get many objects from S3 in parallel.
        
        Parameters
        ----------
        keys : Iterable[Union[str, S3GetObject]]
            Objects to download. Each object can be an S3 url, a path suffix, or
            an S3GetObject that defines a range of data to download.
        return_missing : bool, default False
            If set to True, do not raise an exception for a missing key but
            return it as an `S3Object` with `.exists == False`.
        return_info : bool, default True
            If set to True, fetch the content-type and user metadata associated
            with the object at no extra cost, included for symmetry with `get_many`.
        
        Returns
        -------
        List[S3Object]
            S3Objects corresponding to the objects requested.
        """
        ...
    def get_recursive(self, keys: typing.Iterable[str], return_info: bool = False) -> typing.List[metaflow.plugins.datatools.s3.s3.S3Object]:
        """
        Get many objects from S3 recursively in parallel.
        
        Parameters
        ----------
        keys : Iterable[str]
            Prefixes to download recursively. Each prefix can be an S3 url or a path suffix
            which define the root prefix under which all objects are downloaded.
        return_info : bool, default False
            If set to True, fetch the content-type and user metadata associated
            with the object.
        
        Returns
        -------
        List[S3Object]
            S3Objects stored under the given prefixes.
        """
        ...
    def get_all(self, return_info: bool = False) -> typing.List[metaflow.plugins.datatools.s3.s3.S3Object]:
        """
        Get all objects under the prefix set in the `S3` constructor.
        
        This method requires that the `S3` object is initialized either with `run` or
        `s3root`.
        
        Parameters
        ----------
        return_info : bool, default False
            If set to True, fetch the content-type and user metadata associated
            with the object.
        
        Returns
        -------
        Iterable[S3Object]
            S3Objects stored under the main prefix.
        """
        ...
    def put(self, key: typing.Union[str, metaflow.plugins.datatools.s3.s3.S3PutObject], obj: typing.Union[io.RawIOBase, io.BufferedIOBase, str, bytes], overwrite: bool = True, content_type: typing.Optional[str] = None, metadata: typing.Optional[typing.Dict[str, str]] = None) -> str:
        """
        Upload a single object to S3.
        
        Parameters
        ----------
        key : Union[str, S3PutObject]
            Object path. It can be an S3 url or a path suffix.
        obj : PutValue
            An object to store in S3. Strings are converted to UTF-8 encoding.
        overwrite : bool, default True
            Overwrite the object if it exists. If set to False, the operation
            succeeds without uploading anything if the key already exists.
        content_type : str, optional, default None
            Optional MIME type for the object.
        metadata : Dict[str, str], optional, default None
            A JSON-encodable dictionary of additional headers to be stored
            as metadata with the object.
        
        Returns
        -------
        str
            URL of the object stored.
        """
        ...
    def put_many(self, key_objs: typing.List[typing.Union[typing.Tuple[str, typing.Union[io.RawIOBase, io.BufferedIOBase, str, bytes]], metaflow.plugins.datatools.s3.s3.S3PutObject]], overwrite: bool = True) -> typing.List[typing.Tuple[str, str]]:
        """
        Upload many objects to S3.
        
        Each object to be uploaded can be specified in two ways:
        
        1. As a `(key, obj)` tuple where `key` is a string specifying
           the path and `obj` is a string or a bytes object.
        
        2. As a `S3PutObject` which contains additional metadata to be
           stored with the object.
        
        Parameters
        ----------
        key_objs : List[Union[Tuple[str, PutValue], S3PutObject]]
            List of key-object pairs to upload.
        overwrite : bool, default True
            Overwrite the object if it exists. If set to False, the operation
            succeeds without uploading anything if the key already exists.
        
        Returns
        -------
        List[Tuple[str, str]]
            List of `(key, url)` pairs corresponding to the objects uploaded.
        """
        ...
    def put_files(self, key_paths: typing.List[typing.Union[typing.Tuple[str, typing.Union[io.RawIOBase, io.BufferedIOBase, str, bytes]], metaflow.plugins.datatools.s3.s3.S3PutObject]], overwrite: bool = True) -> typing.List[typing.Tuple[str, str]]:
        """
        Upload many local files to S3.
        
        Each file to be uploaded can be specified in two ways:
        
        1. As a `(key, path)` tuple where `key` is a string specifying
           the S3 path and `path` is the path to a local file.
        
        2. As a `S3PutObject` which contains additional metadata to be
           stored with the file.
        
        Parameters
        ----------
        key_paths :  List[Union[Tuple[str, PutValue], S3PutObject]]
            List of files to upload.
        overwrite : bool, default True
            Overwrite the object if it exists. If set to False, the operation
            succeeds without uploading anything if the key already exists.
        
        Returns
        -------
        List[Tuple[str, str]]
            List of `(key, url)` pairs corresponding to the files uploaded.
        """
        ...
    ...

class Azure(object, metaclass=type):
    @classmethod
    def get_root_from_config(cls, echo, create_on_absent = True):
        ...
    def __init__(self):
        ...
    def __enter__(self):
        ...
    def __exit__(self, *args):
        ...
    def get(self, key = None, return_missing = False):
        """
        Key MUST be a fully qualified path with uri scheme.  azure://<container_name>/b/l/o/b/n/a/m/e
        """
        ...
    def put(self, key, obj, overwrite = True):
        """
        Key MUST be a fully qualified path.  <container_name>/b/l/o/b/n/a/m/e
        """
        ...
    def info(self, key = None, return_missing = False):
        ...
    ...

class GS(object, metaclass=type):
    @classmethod
    def get_root_from_config(cls, echo, create_on_absent = True):
        ...
    def __init__(self):
        ...
    def __enter__(self):
        ...
    def __exit__(self, *args):
        ...
    def get(self, key = None, return_missing = False):
        """
        Key MUST be a fully qualified path.  gs://<bucket_name>/b/l/o/b/n/a/m/e
        """
        ...
    def put(self, key, obj, overwrite = True):
        """
        Key MUST be a fully qualified path.  gs://<bucket_name>/b/l/o/b/n/a/m/e
        """
        ...
    def info(self, key = None, return_missing = False):
        ...
    ...

DATACLIENTS: dict

class IncludedFile(object, metaclass=type):
    def __init__(self, descriptor: typing.Dict[str, typing.Any]):
        ...
    @property
    def descriptor(self):
        ...
    @property
    def size(self):
        ...
    def decode(self, name, var_type = "Artifact"):
        ...
    ...

class FilePathClass(metaflow._vendor.click.types.ParamType, metaclass=type):
    def __init__(self, is_text, encoding):
        ...
    def convert(self, value, param, ctx):
        ...
    def __str__(self):
        ...
    def __repr__(self):
        ...
    ...

class IncludeFile(metaflow.parameters.Parameter, metaclass=type):
    def __init__(self, name: str, required: bool = False, is_text: bool = True, encoding: str = "utf-8", help: typing.Optional[str] = None, **kwargs: typing.Dict[str, str]):
        ...
    def load_parameter(self, v):
        ...
    ...

class UploaderV1(object, metaclass=type):
    @classmethod
    def encode_url(cls, url_type, url, **kwargs):
        ...
    @classmethod
    def store(cls, flow_name, path, is_text, encoding, handler, echo):
        ...
    @classmethod
    def size(cls, descriptor):
        ...
    @classmethod
    def load(cls, descriptor):
        ...
    ...

class UploaderV2(object, metaclass=type):
    @classmethod
    def encode_url(cls, url_type, url, **kwargs):
        ...
    @classmethod
    def store(cls, flow_name, path, is_text, encoding, handler, echo):
        ...
    @classmethod
    def size(cls, descriptor):
        ...
    @classmethod
    def load(cls, descriptor):
        ...
    ...

UPLOADERS: dict

class CURRENT_UPLOADER(object, metaclass=type):
    @classmethod
    def encode_url(cls, url_type, url, **kwargs):
        ...
    @classmethod
    def store(cls, flow_name, path, is_text, encoding, handler, echo):
        ...
    @classmethod
    def size(cls, descriptor):
        ...
    @classmethod
    def load(cls, descriptor):
        ...
    ...

