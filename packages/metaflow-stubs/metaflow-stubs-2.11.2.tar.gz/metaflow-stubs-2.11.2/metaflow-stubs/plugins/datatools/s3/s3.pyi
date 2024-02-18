##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.822033                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import typing
    import metaflow.plugins.datatools.s3.s3
    import io
    import metaflow.metaflow_current
    import metaflow.datastore.inputs
    import metaflow.exception

TYPE_CHECKING: bool

class FlowSpec(object, metaclass=type):
    def __init__(self, use_cli = True):
        """
        Construct a FlowSpec
        
        Parameters
        ----------
        use_cli : bool, default True
            Set to True if the flow is invoked from __main__ or the command line
        """
        ...
    @property
    def script_name(self) -> str:
        """
        [Legacy function - do not use. Use `current` instead]
        
        Returns the name of the script containing the flow
        
        Returns
        -------
        str
            A string containing the name of the script
        """
        ...
    def __iter__(self):
        """
        [Legacy function - do not use]
        
        Iterate over all steps in the Flow
        
        Returns
        -------
        Iterator[graph.DAGNode]
            Iterator over the steps in the flow
        """
        ...
    def __getattr__(self, name: str):
        ...
    def cmd(self, cmdline, input = {}, output = []):
        """
        [Legacy function - do not use]
        """
        ...
    @property
    def index(self) -> typing.Optional[int]:
        """
        The index of this foreach branch.
        
        In a foreach step, multiple instances of this step (tasks) will be executed,
        one for each element in the foreach. This property returns the zero based index
        of the current task. If this is not a foreach step, this returns None.
        
        If you need to know the indices of the parent tasks in a nested foreach, use
        `FlowSpec.foreach_stack`.
        
        Returns
        -------
        int, optional
            Index of the task in a foreach step.
        """
        ...
    @property
    def input(self) -> typing.Optional[typing.Any]:
        """
        The value of the foreach artifact in this foreach branch.
        
        In a foreach step, multiple instances of this step (tasks) will be executed,
        one for each element in the foreach. This property returns the element passed
        to the current task. If this is not a foreach step, this returns None.
        
        If you need to know the values of the parent tasks in a nested foreach, use
        `FlowSpec.foreach_stack`.
        
        Returns
        -------
        object, optional
            Input passed to the foreach task.
        """
        ...
    def foreach_stack(self) -> typing.Optional[typing.List[typing.Tuple[int, int, typing.Any]]]:
        """
        Returns the current stack of foreach indexes and values for the current step.
        
        Use this information to understand what data is being processed in the current
        foreach branch. For example, considering the following code:
        ```
        @step
        def root(self):
            self.split_1 = ['a', 'b', 'c']
            self.next(self.nest_1, foreach='split_1')
        
        @step
        def nest_1(self):
            self.split_2 = ['d', 'e', 'f', 'g']
            self.next(self.nest_2, foreach='split_2'):
        
        @step
        def nest_2(self):
            foo = self.foreach_stack()
        ```
        
        `foo` will take the following values in the various tasks for nest_2:
        ```
            [(0, 3, 'a'), (0, 4, 'd')]
            [(0, 3, 'a'), (1, 4, 'e')]
            ...
            [(0, 3, 'a'), (3, 4, 'g')]
            [(1, 3, 'b'), (0, 4, 'd')]
            ...
        ```
        where each tuple corresponds to:
        
        - The index of the task for that level of the loop.
        - The number of splits for that level of the loop.
        - The value for that level of the loop.
        
        Note that the last tuple returned in a task corresponds to:
        
        - 1st element: value returned by `self.index`.
        - 3rd element: value returned by `self.input`.
        
        Returns
        -------
        List[Tuple[int, int, Any]]
            An array describing the current stack of foreach steps.
        """
        ...
    def merge_artifacts(self, inputs: metaflow.datastore.inputs.Inputs, exclude: typing.Optional[typing.List[str]] = None, include: typing.Optional[typing.List[str]] = None):
        """
        Helper function for merging artifacts in a join step.
        
        This function takes all the artifacts coming from the branches of a
        join point and assigns them to self in the calling step. Only artifacts
        not set in the current step are considered. If, for a given artifact, different
        values are present on the incoming edges, an error will be thrown and the artifacts
        that conflict will be reported.
        
        As a few examples, in the simple graph: A splitting into B and C and joining in D:
        ```
        A:
          self.x = 5
          self.y = 6
        B:
          self.b_var = 1
          self.x = from_b
        C:
          self.x = from_c
        
        D:
          merge_artifacts(inputs)
        ```
        In D, the following artifacts are set:
          - `y` (value: 6), `b_var` (value: 1)
          - if `from_b` and `from_c` are the same, `x` will be accessible and have value `from_b`
          - if `from_b` and `from_c` are different, an error will be thrown. To prevent this error,
            you need to manually set `self.x` in D to a merged value (for example the max) prior to
            calling `merge_artifacts`.
        
        Parameters
        ----------
        inputs : Inputs
            Incoming steps to the join point.
        exclude : List[str], optional, default None
            If specified, do not consider merging artifacts with a name in `exclude`.
            Cannot specify if `include` is also specified.
        include : List[str], optional, default None
            If specified, only merge artifacts specified. Cannot specify if `exclude` is
            also specified.
        
        Raises
        ------
        MetaflowException
            This exception is thrown if this is not called in a join step.
        UnhandledInMergeArtifactsException
            This exception is thrown in case of unresolved conflicts.
        MissingInMergeArtifactsException
            This exception is thrown in case an artifact specified in `include` cannot
            be found.
        """
        ...
    def next(self, *dsts: typing.Callable[..., None], **kwargs):
        """
        Indicates the next step to execute after this step has completed.
        
        This statement should appear as the last statement of each step, except
        the end step.
        
        There are several valid formats to specify the next step:
        
        - Straight-line connection: `self.next(self.next_step)` where `next_step` is a method in
          the current class decorated with the `@step` decorator.
        
        - Static fan-out connection: `self.next(self.step1, self.step2, ...)` where `stepX` are
          methods in the current class decorated with the `@step` decorator.
        
        - Foreach branch:
          ```
          self.next(self.foreach_step, foreach='foreach_iterator')
          ```
          In this situation, `foreach_step` is a method in the current class decorated with the
          `@step` decorator and `foreach_iterator` is a variable name in the current class that
          evaluates to an iterator. A task will be launched for each value in the iterator and
          each task will execute the code specified by the step `foreach_step`.
        
        Parameters
        ----------
        dsts : Callable[..., None]
            One or more methods annotated with `@step`.
        
        Raises
        ------
        InvalidNextException
            Raised if the format of the arguments does not match one of the ones given above.
        """
        ...
    def __str__(self):
        ...
    def __getstate__(self):
        ...
    ...

current: metaflow.metaflow_current.Current

DATATOOLS_S3ROOT: None

S3_RETRY_COUNT: int

S3_TRANSIENT_RETRY_COUNT: int

S3_SERVER_SIDE_ENCRYPTION: None

TEMPDIR: str

class MetaflowException(Exception, metaclass=type):
    def __init__(self, msg = "", lineno = None):
        ...
    def __str__(self):
        ...
    ...

def get_s3_client(s3_role_arn = None, s3_session_vars = None, s3_client_params = None):
    ...

def read_in_chunks(dst, src, src_sz, max_chunk_size):
    ...

def get_timestamp(dt):
    """
    Python2 compatible way to compute the timestamp (seconds since 1/1/1970)
    """
    ...

TRANSIENT_RETRY_START_LINE: str

TRANSIENT_RETRY_LINE_CONTENT: str

def check_s3_deps(func):
    """
    The decorated function checks S3 dependencies (as needed for AWS S3 storage backend).
    This includes boto3.
    """
    ...

TEST_INJECT_RETRYABLE_FAILURES: int

def ensure_unicode(x):
    ...

class S3GetObject(tuple, metaclass=type):
    @staticmethod
    def __new__(_cls, key: str, offset: int, length: int):
        """
        Create new instance of S3GetObject(key, offset, length)
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
    def __init__(self, key: str, offset: int, length: int):
        ...
    ...

class S3PutObject(tuple, metaclass=type):
    @staticmethod
    def __new__(_cls, key: str, value: typing.Union[io.RawIOBase, io.BufferedIOBase, str, bytes, None] = None, path: typing.Optional[str] = None, content_type: typing.Optional[str] = None, encryption: typing.Optional[str] = None, metadata: typing.Optional[typing.Dict[str, str]] = None):
        """
        Create new instance of S3PutObject(key, value, path, content_type, encryption, metadata)
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
    def __init__(self, key: str, value: typing.Union[io.RawIOBase, io.BufferedIOBase, str, bytes, None], path: typing.Optional[str], content_type: typing.Optional[str], encryption: typing.Optional[str], metadata: typing.Optional[typing.Dict[str, str]]):
        ...
    ...

class RangeInfo(tuple, metaclass=type):
    @staticmethod
    def __new__(_cls, total_size: int, request_offset: int = 0, request_length: int = -1):
        """
        Create new instance of RangeInfo(total_size, request_offset, request_length)
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
    def __init__(self, total_size: int, request_offset: int, request_length: int):
        ...
    ...

class MetaflowS3InvalidObject(metaflow.exception.MetaflowException, metaclass=type):
    ...

class MetaflowS3URLException(metaflow.exception.MetaflowException, metaclass=type):
    ...

class MetaflowS3Exception(metaflow.exception.MetaflowException, metaclass=type):
    ...

class MetaflowS3NotFound(metaflow.exception.MetaflowException, metaclass=type):
    ...

class MetaflowS3AccessDenied(metaflow.exception.MetaflowException, metaclass=type):
    ...

class MetaflowS3InvalidRange(metaflow.exception.MetaflowException, metaclass=type):
    ...

class S3Object(object, metaclass=type):
    def __init__(self, prefix: str, url: str, path: str, size: typing.Optional[int] = None, content_type: typing.Optional[str] = None, metadata: typing.Optional[typing.Dict[str, str]] = None, range_info: typing.Optional[RangeInfo] = None, last_modified: typing.Optional[int] = None, encryption: typing.Optional[str] = None):
        ...
    @property
    def exists(self) -> bool:
        """
        Does this key correspond to an object in S3?
        
        Returns
        -------
        bool
            True if this object points at an existing object (file) in S3.
        """
        ...
    @property
    def downloaded(self) -> bool:
        """
        Has this object been downloaded?
        
        If True, the contents can be accessed through `path`, `blob`,
        and `text` properties.
        
        Returns
        -------
        bool
            True if the contents of this object have been downloaded.
        """
        ...
    @property
    def url(self) -> str:
        """
        S3 location of the object
        
        Returns
        -------
        str
            The S3 location of this object.
        """
        ...
    @property
    def prefix(self) -> str:
        """
        Prefix requested that matches this object.
        
        Returns
        -------
        str
            Requested prefix
        """
        ...
    @property
    def key(self) -> str:
        """
        Key corresponds to the key given to the get call that produced
        this object.
        
        This may be a full S3 URL or a suffix based on what
        was requested.
        
        Returns
        -------
        str
            Key requested.
        """
        ...
    @property
    def path(self) -> typing.Optional[str]:
        """
        Path to a local temporary file corresponding to the object downloaded.
        
        This file gets deleted automatically when a S3 scope exits.
        Returns None if this S3Object has not been downloaded.
        
        Returns
        -------
        str
            Local path, if the object has been downloaded.
        """
        ...
    @property
    def blob(self) -> typing.Optional[bytes]:
        """
        Contents of the object as a byte string or None if the
        object hasn't been downloaded.
        
        Returns
        -------
        bytes
            Contents of the object as bytes.
        """
        ...
    @property
    def text(self) -> typing.Optional[str]:
        """
        Contents of the object as a string or None if the
        object hasn't been downloaded.
        
        The object is assumed to contain UTF-8 encoded data.
        
        Returns
        -------
        str
            Contents of the object as text.
        """
        ...
    @property
    def size(self) -> typing.Optional[int]:
        """
        Size of the object in bytes.
        
        Returns None if the key does not correspond to an object in S3.
        
        Returns
        -------
        int
            Size of the object in bytes, if the object exists.
        """
        ...
    @property
    def has_info(self) -> bool:
        """
        Returns true if this `S3Object` contains the content-type MIME header or
        user-defined metadata.
        
        If False, this means that `content_type`, `metadata`, `range_info` and
        `last_modified` will return None.
        
        Returns
        -------
        bool
            True if additional metadata is available.
        """
        ...
    @property
    def metadata(self) -> typing.Optional[typing.Dict[str, str]]:
        """
        Returns a dictionary of user-defined metadata, or None if no metadata
        is defined.
        
        Returns
        -------
        Dict
            User-defined metadata.
        """
        ...
    @property
    def content_type(self) -> typing.Optional[str]:
        """
        Returns the content-type of the S3 object or None if it is not defined.
        
        Returns
        -------
        str
            Content type or None if the content type is undefined.
        """
        ...
    @property
    def encryption(self) -> typing.Optional[str]:
        """
        Returns the encryption type of the S3 object or None if it is not defined.
        
        Returns
        -------
        str
            Server-side-encryption type or None if parameter is not set.
        """
        ...
    @property
    def range_info(self) -> typing.Optional[RangeInfo]:
        """
        If the object corresponds to a partially downloaded object, returns
        information of what was downloaded.
        
        The returned object has the following fields:
        - `total_size`: Size of the object in S3.
        - `request_offset`: The starting offset.
        - `request_length`: The number of bytes downloaded.
        
        Returns
        -------
        namedtuple
            An object containing information about the partial download. If
            the `S3Object` doesn't correspond to a partially downloaded file,
            returns None.
        """
        ...
    @property
    def last_modified(self) -> typing.Optional[int]:
        """
        Returns the last modified unix timestamp of the object.
        
        Returns
        -------
        int
            Unix timestamp corresponding to the last modified time.
        """
        ...
    def __str__(self):
        ...
    def __repr__(self):
        ...
    ...

class S3Client(object, metaclass=type):
    def __init__(self, s3_role_arn = None, s3_session_vars = None, s3_client_params = None):
        ...
    @property
    def client(self):
        ...
    @property
    def error(self):
        ...
    def reset_client(self):
        ...
    ...

class S3(object, metaclass=type):
    @classmethod
    def get_root_from_config(cls, echo, create_on_absent = True):
        ...
    def __enter__(self) -> S3:
        ...
    def __exit__(self, *args):
        ...
    def close(self):
        """
        Delete all temporary files downloaded in this context.
        """
        ...
    def list_paths(self, keys: typing.Optional[typing.Iterable[str]] = None) -> typing.List[S3Object]:
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
    def list_recursive(self, keys: typing.Optional[typing.Iterable[str]] = None) -> typing.List[S3Object]:
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
    def info(self, key: typing.Optional[str] = None, return_missing: bool = False) -> S3Object:
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
    def info_many(self, keys: typing.Iterable[str], return_missing: bool = False) -> typing.List[S3Object]:
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
    def get(self, key: typing.Union[str, S3GetObject, None] = None, return_missing: bool = False, return_info: bool = True) -> S3Object:
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
    def get_many(self, keys: typing.Iterable[typing.Union[str, S3GetObject]], return_missing: bool = False, return_info: bool = True) -> typing.List[S3Object]:
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
    def get_recursive(self, keys: typing.Iterable[str], return_info: bool = False) -> typing.List[S3Object]:
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
    def get_all(self, return_info: bool = False) -> typing.List[S3Object]:
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
    def put(self, key: typing.Union[str, S3PutObject], obj: typing.Union[io.RawIOBase, io.BufferedIOBase, str, bytes], overwrite: bool = True, content_type: typing.Optional[str] = None, metadata: typing.Optional[typing.Dict[str, str]] = None) -> str:
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
    def put_many(self, key_objs: typing.List[typing.Union[typing.Tuple[str, typing.Union[io.RawIOBase, io.BufferedIOBase, str, bytes]], S3PutObject]], overwrite: bool = True) -> typing.List[typing.Tuple[str, str]]:
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
    def put_files(self, key_paths: typing.List[typing.Union[typing.Tuple[str, typing.Union[io.RawIOBase, io.BufferedIOBase, str, bytes]], S3PutObject]], overwrite: bool = True) -> typing.List[typing.Tuple[str, str]]:
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

