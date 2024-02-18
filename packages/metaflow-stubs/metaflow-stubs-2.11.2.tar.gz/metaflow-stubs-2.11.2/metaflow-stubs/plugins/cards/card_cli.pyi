##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.881280                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import typing
    import metaflow.exception
    import metaflow.parameters
    import metaflow.client.core
    import datetime

class Task(metaflow.client.core.MetaflowObject, metaclass=type):
    def __init__(self, *args, **kwargs):
        ...
    @property
    def metadata(self) -> typing.List[metaflow.client.core.Metadata]:
        """
        Metadata events produced by this task across all attempts of the task
        *except* if you selected a specific task attempt.
        
        Note that Metadata is different from tags.
        
        Returns
        -------
        List[Metadata]
            Metadata produced by this task
        """
        ...
    @property
    def metadata_dict(self) -> typing.Dict[str, str]:
        """
        Dictionary mapping metadata names (keys) and their associated values.
        
        Note that unlike the metadata() method, this call will only return the latest
        metadata for a given name. For example, if a task executes multiple times (retries),
        the same metadata name will be generated multiple times (one for each execution of the
        task). The metadata() method returns all those metadata elements whereas this call will
        return the metadata associated with the latest execution of the task.
        
        Returns
        -------
        Dict[str, str]
            Dictionary mapping metadata name with value
        """
        ...
    @property
    def index(self) -> typing.Optional[int]:
        """
        Returns the index of the innermost foreach loop if this task is run inside at least
        one foreach.
        
        The index is what distinguishes the various tasks inside a given step.
        This call returns None if this task was not run in a foreach loop.
        
        Returns
        -------
        int, optional
            Index in the innermost loop for this task
        """
        ...
    @property
    def data(self) -> metaflow.client.core.MetaflowData:
        """
        Returns a container of data artifacts produced by this task.
        
        You can access data produced by this task as follows:
        ```
        print(task.data.my_var)
        ```
        
        Returns
        -------
        MetaflowData
            Container of all artifacts produced by this task
        """
        ...
    @property
    def artifacts(self) -> typing.NamedTuple:
        """
        Returns a container of DataArtifacts produced by this task.
        
        You can access each DataArtifact by name like so:
        ```
        print(task.artifacts.my_var)
        ```
        This method differs from data() because it returns DataArtifact objects
        (which contain additional metadata) as opposed to just the data.
        
        Returns
        -------
        MetaflowArtifacts
            Container of all DataArtifacts produced by this task
        """
        ...
    @property
    def successful(self) -> bool:
        """
        Indicates whether or not the task completed successfully.
        
        This information is always about the latest task to have completed (in case
        of retries).
        
        Returns
        -------
        bool
            True if the task completed successfully and False otherwise
        """
        ...
    @property
    def finished(self) -> bool:
        """
        Indicates whether or not the task completed.
        
        This information is always about the latest task to have completed (in case
        of retries).
        
        Returns
        -------
        bool
            True if the task completed and False otherwise
        """
        ...
    @property
    def exception(self) -> typing.Optional[typing.Any]:
        """
        Returns the exception that caused the task to fail, if any.
        
        This information is always about the latest task to have completed (in case
        of retries). If successful() returns False and finished() returns True,
        this method can help determine what went wrong.
        
        Returns
        -------
        object
            Exception raised by the task or None if not applicable
        """
        ...
    @property
    def finished_at(self) -> typing.Optional[datetime.datetime]:
        """
        Returns the datetime object of when the task finished (successfully or not).
        
        This information is always about the latest task to have completed (in case
        of retries). This call will return None if the task is not finished.
        
        Returns
        -------
        datetime
            Datetime of when the task finished
        """
        ...
    @property
    def runtime_name(self) -> typing.Optional[str]:
        """
        Returns the name of the runtime this task executed on.
        
        
        Returns
        -------
        str
            Name of the runtime this task executed on
        """
        ...
    @property
    def stdout(self) -> str:
        """
        Returns the full standard out of this task.
        
        If you specify a specific attempt for this task, it will return the
        standard out for that attempt. If you do not specify an attempt,
        this will return the current standard out for the latest *started*
        attempt of the task. In both cases, multiple calls to this
        method will return the most up-to-date log (so if an attempt is not
        done, each call will fetch the latest log).
        
        Returns
        -------
        str
            Standard output of this task
        """
        ...
    @property
    def stdout_size(self) -> int:
        """
        Returns the size of the stdout log of this task.
        
        Similar to `stdout`, the size returned is the latest size of the log
        (so for a running attempt, this value will increase as the task produces
        more output).
        
        Returns
        -------
        int
            Size of the stdout log content (in bytes)
        """
        ...
    @property
    def stderr(self) -> str:
        """
        Returns the full standard error of this task.
        
        If you specify a specific attempt for this task, it will return the
        standard error for that attempt. If you do not specify an attempt,
        this will return the current standard error for the latest *started*
        attempt. In both cases, multiple calls to this
        method will return the most up-to-date log (so if an attempt is not
        done, each call will fetch the latest log).
        
        Returns
        -------
        str
            Standard error of this task
        """
        ...
    @property
    def stderr_size(self) -> int:
        """
        Returns the size of the stderr log of this task.
        
        Similar to `stderr`, the size returned is the latest size of the log
        (so for a running attempt, this value will increase as the task produces
        more output).
        
        Returns
        -------
        int
            Size of the stderr log content (in bytes)
        """
        ...
    @property
    def current_attempt(self) -> int:
        """
        Get the relevant attempt for this Task.
        
        Returns the specific attempt used when
        initializing the instance, or the latest *started* attempt for the Task.
        
        Returns
        -------
        int
            attempt id for this task object
        """
        ...
    @property
    def code(self) -> typing.Optional[metaflow.client.core.MetaflowCode]:
        """
        Returns the MetaflowCode object for this task, if present.
        
        Not all tasks save their code so this call may return None in those cases.
        
        Returns
        -------
        MetaflowCode
            Code package for this task
        """
        ...
    @property
    def environment_info(self) -> typing.Dict[str, typing.Any]:
        """
        Returns information about the environment that was used to execute this task. As an
        example, if the Conda environment is selected, this will return information about the
        dependencies that were used in the environment.
        
        This environment information is only available for tasks that have a code package.
        
        Returns
        -------
        Dict
            Dictionary describing the environment
        """
        ...
    def loglines(self, stream: str, as_unicode: bool = True, meta_dict: typing.Optional[typing.Dict[str, typing.Any]] = None) -> typing.Iterator[typing.Tuple[datetime.datetime, str]]:
        """
        Return an iterator over (utc_timestamp, logline) tuples.
        
        Parameters
        ----------
        stream : str
            Either 'stdout' or 'stderr'.
        as_unicode : bool, default: True
            If as_unicode=False, each logline is returned as a byte object. Otherwise,
            it is returned as a (unicode) string.
        
        Yields
        ------
        Tuple[datetime, str]
            Tuple of timestamp, logline pairs.
        """
        ...
    def __iter__(self) -> typing.Iterator[metaflow.client.core.DataArtifact]:
        """
        Iterate over all children DataArtifact of this Task
        
        Yields
        ------
        DataArtifact
            A DataArtifact in this Step
        """
        ...
    def __getitem__(self, name: str) -> metaflow.client.core.DataArtifact:
        """
        Returns the DataArtifact object with the artifact name 'name'
        
        Parameters
        ----------
        name : str
            Data artifact name
        
        Returns
        -------
        DataArtifact
            DataArtifact for this artifact name in this task
        
        Raises
        ------
        KeyError
            If the name does not identify a valid DataArtifact object
        """
        ...
    def __getstate__(self):
        ...
    def __setstate__(self, state):
        ...
    ...

JSONType: metaflow.parameters.JSONTypeClass

def namespace(ns: typing.Optional[str]) -> typing.Optional[str]:
    """
    Switch namespace to the one provided.
    
    This call has a global effect. No objects outside this namespace
    will be accessible. To access all objects regardless of namespaces,
    pass None to this call.
    
    Parameters
    ----------
    ns : str, optional
        Namespace to switch to or None to ignore namespaces.
    
    Returns
    -------
    str, optional
        Namespace set (result of get_namespace()).
    """
    ...

class CommandException(metaflow.exception.MetaflowException, metaclass=type):
    ...

class MetaflowNotFound(metaflow.exception.MetaflowException, metaclass=type):
    ...

class MetaflowNamespaceMismatch(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, namespace):
        ...
    ...

class CardDatastore(object, metaclass=type):
    @classmethod
    def get_storage_root(cls, storage_type):
        ...
    def __init__(self, flow_datastore, pathspec = None):
        ...
    @classmethod
    def get_card_location(cls, base_path, card_name, uuid, card_id = None, suffix = "html"):
        ...
    @staticmethod
    def info_from_path(path, suffix = "html"):
        """
        Args:
            path (str): The path to the card
        
        Raises:
            Exception: When the card_path is invalid
        
        Returns:
            CardInfo
        """
        ...
    def save_data(self, uuid, card_type, json_data, card_id = None):
        ...
    def save_card(self, uuid, card_type, card_html, card_id = None, overwrite = True):
        ...
    def create_full_path(self, card_path):
        ...
    def get_card_names(self, card_paths):
        ...
    def get_card_html(self, path):
        ...
    def get_card_data(self, path):
        ...
    def cache_locally(self, path, save_path = None):
        """
        Saves the data present in the `path` the `metaflow_card_cache` directory or to the `save_path`.
        """
        ...
    def extract_data_paths(self, card_type = None, card_hash = None, card_id = None):
        ...
    def extract_card_paths(self, card_type = None, card_hash = None, card_id = None):
        ...
    ...

NUM_SHORT_HASH_CHARS: int

class CardClassFoundException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, card_name):
        ...
    ...

class IncorrectCardArgsException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, card_type, args):
        ...
    ...

class UnrenderableCardException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, card_type, args):
        ...
    ...

class CardNotPresentException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, pathspec, card_type = None, card_hash = None, card_id = None):
        ...
    ...

class TaskNotFoundException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, pathspec_query, resolved_from, run_id = None):
        ...
    ...

def resolve_paths_from_task(flow_datastore, pathspec = None, type = None, hash = None, card_id = None):
    ...

def resumed_info(task):
    ...

class CardRenderInfo(tuple, metaclass=type):
    @staticmethod
    def __new__(_cls, mode, is_implemented, data, timed_out, timeout_stack_trace):
        """
        Create new instance of CardRenderInfo(mode, is_implemented, data, timed_out, timeout_stack_trace)
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
    ...

def open_in_browser(card_path):
    ...

def resolve_task_from_pathspec(flow_name, pathspec):
    """
    resolves a task object for the pathspec query on the CLI.
    Args:
        flow_name : (str) : name of flow
        pathspec (str) : can be `stepname` / `runid/stepname` / `runid/stepname/taskid`
    
    Returns:
        metaflow.Task | None
    """
    ...

def resolve_card(ctx, pathspec, follow_resumed = True, hash = None, type = None, card_id = None, no_echo = False):
    """
    Resolves the card path for a query.
    
    Args:
        ctx: click context object
        pathspec: pathspec can be `stepname` or `runid/stepname` or `runid/stepname/taskid`
        hash (optional): This is to specifically resolve the card via the hash. This is useful when there may be many card with same id or type for a pathspec.
        type : type of card
        card_id : `id` given to card
        no_echo : if set to `True` then supress logs about pathspec resolution.
    Raises:
        CardNotPresentException: No card could be found for the pathspec
    
    Returns:
        (card_paths, card_datastore, taskpathspec) : Tuple[List[str], CardDatastore, str]
    """
    ...

def timeout(time):
    ...

def raise_timeout(signum, frame):
    ...

def list_available_cards(ctx, pathspec, card_paths, card_datastore, command = "view", show_list_as_json = False, list_many = False, file = None):
    ...

def make_command(script_name, taskspec, command = "get", hash = None):
    ...

def list_many_cards(ctx, type = None, hash = None, card_id = None, follow_resumed = None, as_json = None, file = None):
    ...

def card_read_options_and_arguments(func):
    ...

def update_card(mf_card, mode, task, data, timeout_value = None):
    """
    This method will be responsible for creating a card/data-update based on the `mode`.
    There are three possible modes taken by this function.
        - render :
            - This will render the "final" card.
            - This mode is passed at task completion.
            - Setting this mode will call the `render` method of a MetaflowCard.
            - It will result in the creation of an HTML page.
        - render_runtime:
            - Setting this mode will render a card during task "runtime".
            - Setting this mode will call the `render_runtime` method of a MetaflowCard.
            - It will result in the creation of an HTML page.
        - refresh:
            - Setting this mode will refresh the data update for a card.
            - We support this mode because rendering a full card can be an expensive operation, but shipping tiny data updates can be cheap.
            - Setting this mode will call the `refresh` method of a MetaflowCard.
            - It will result in the creation of a JSON object.
    
    Parameters
    ----------
    mf_card : MetaflowCard
        MetaflowCard object which will be used to render the card.
    mode : str
        Mode of rendering the card.
    task : Task
        Task object which will be passed to render the card.
    data : dict
        object created and passed down from `current.card._get_latest_data` method.
        For more information on this object's schema have a look at `current.card._get_latest_data` method.
    timeout_value : int
        Timeout value for rendering the card.
    
    Returns
    -------
    CardRenderInfo
        - NamedTuple which will contain:
            - `mode`: The mode of rendering the card.
            - `is_implemented`: whether the function was implemented or not.
            - `data` : output from rendering the card (Can be string/dict)
            - `timed_out` : whether the function timed out or not.
            - `timeout_stack_trace` : stack trace of the function if it timed out.
    """
    ...

