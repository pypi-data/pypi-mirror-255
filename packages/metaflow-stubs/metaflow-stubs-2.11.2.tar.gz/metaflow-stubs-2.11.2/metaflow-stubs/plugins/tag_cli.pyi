##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.847871                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.exception
    import metaflow.metaflow_current
    import metaflow.client.core
    import metaflow.events
    import datetime

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

class Flow(metaflow.client.core.MetaflowObject, metaclass=type):
    def __init__(self, *args, **kwargs):
        ...
    @property
    def latest_run(self) -> typing.Optional[metaflow.client.core.Run]:
        """
        Returns the latest run (either in progress or completed) of this flow.
        
        Note that an in-progress run may be returned by this call. Use latest_successful_run
        to get an object representing a completed successful run.
        
        Returns
        -------
        Run, optional
            Latest run of this flow
        """
        ...
    @property
    def latest_successful_run(self) -> typing.Optional[metaflow.client.core.Run]:
        """
        Returns the latest successful run of this flow.
        
        Returns
        -------
        Run, optional
            Latest successful run of this flow
        """
        ...
    def runs(self, *tags: str) -> typing.Iterator[metaflow.client.core.Run]:
        """
        Returns an iterator over all `Run`s of this flow.
        
        An optional filter is available that allows you to filter on tags.
        If multiple tags are specified, only runs that have all the
        specified tags are returned.
        
        Parameters
        ----------
        tags : str
            Tags to match.
        
        Yields
        ------
        Run
            `Run` objects in this flow.
        """
        ...
    def __iter__(self) -> typing.Iterator[metaflow.client.core.Task]:
        """
        Iterate over all children Run of this Flow.
        
        Note that only runs in the current namespace are returned unless
        _namespace_check is False
        
        Yields
        ------
        Run
            A Run in this Flow
        """
        ...
    def __getitem__(self, run_id: str) -> metaflow.client.core.Run:
        """
        Returns the Run object with the run ID 'run_id'
        
        Parameters
        ----------
        run_id : str
            Run OD
        
        Returns
        -------
        Run
            Run for this run ID in this Flow
        
        Raises
        ------
        KeyError
            If the run_id does not identify a valid Run object
        """
        ...
    def __getstate__(self):
        ...
    def __setstate__(self, state):
        ...
    ...

class Run(metaflow.client.core.MetaflowObject, metaclass=type):
    def steps(self, *tags: str) -> typing.Iterator[metaflow.client.core.Step]:
        """
        [Legacy function - do not use]
        
        Returns an iterator over all `Step` objects in the step. This is an alias
        to iterating the object itself, i.e.
        ```
        list(Run(...)) == list(Run(...).steps())
        ```
        
        Parameters
        ----------
        tags : str
            No op (legacy functionality)
        
        Yields
        ------
        Step
            `Step` objects in this run.
        """
        ...
    @property
    def code(self) -> typing.Optional[metaflow.client.core.MetaflowCode]:
        """
        Returns the MetaflowCode object for this run, if present.
        Code is packed if atleast one `Step` runs remotely, else None is returned.
        
        Returns
        -------
        MetaflowCode, optional
            Code package for this run
        """
        ...
    @property
    def data(self) -> typing.Optional[metaflow.client.core.MetaflowData]:
        """
        Returns a container of data artifacts produced by this run.
        
        You can access data produced by this run as follows:
        ```
        print(run.data.my_var)
        ```
        This is a shorthand for `run['end'].task.data`. If the 'end' step has not yet
        executed, returns None.
        
        Returns
        -------
        MetaflowData, optional
            Container of all artifacts produced by this task
        """
        ...
    @property
    def successful(self) -> bool:
        """
        Indicates whether or not the run completed successfully.
        
        A run is successful if its 'end' step is successful.
        
        Returns
        -------
        bool
            True if the run completed successfully and False otherwise
        """
        ...
    @property
    def finished(self) -> bool:
        """
        Indicates whether or not the run completed.
        
        A run completed if its 'end' step completed.
        
        Returns
        -------
        bool
            True if the run completed and False otherwise
        """
        ...
    @property
    def finished_at(self) -> typing.Optional[datetime.datetime]:
        """
        Returns the datetime object of when the run finished (successfully or not).
        
        The completion time of a run is the same as the completion time of its 'end' step.
        If the 'end' step has not completed, returns None.
        
        Returns
        -------
        datetime, optional
            Datetime of when the run finished
        """
        ...
    @property
    def end_task(self) -> typing.Optional[metaflow.client.core.Task]:
        """
        Returns the Task corresponding to the 'end' step.
        
        This returns None if the end step does not yet exist.
        
        Returns
        -------
        Task, optional
            The 'end' task
        """
        ...
    def add_tag(self, tag: str):
        """
        Add a tag to this `Run`.
        
        Note that if the tag is already a system tag, it is not added as a user tag,
        and no error is thrown.
        
        Parameters
        ----------
        tag : str
            Tag to add.
        """
        ...
    def add_tags(self, tags: typing.Iterable[str]):
        """
        Add one or more tags to this `Run`.
        
        Note that if any tag is already a system tag, it is not added as a user tag
        and no error is thrown.
        
        Parameters
        ----------
        tags : Iterable[str]
            Tags to add.
        """
        ...
    def remove_tag(self, tag: str):
        """
        Remove one tag from this `Run`.
        
        Removing a system tag is an error. Removing a non-existent
        user tag is a no-op.
        
        Parameters
        ----------
        tag : str
            Tag to remove.
        """
        ...
    def remove_tags(self, tags: typing.Iterable[str]):
        """
        Remove one or more tags to this `Run`.
        
        Removing a system tag will result in an error. Removing a non-existent
        user tag is a no-op.
        
        Parameters
        ----------
        tags : Iterable[str]
            Tags to remove.
        """
        ...
    def replace_tag(self, tag_to_remove: str, tag_to_add: str):
        """
        Remove a tag and add a tag atomically. Removal is done first.
        The rules for `Run.add_tag` and `Run.remove_tag` also apply here.
        
        Parameters
        ----------
        tag_to_remove : str
            Tag to remove.
        tag_to_add : str
            Tag to add.
        """
        ...
    def replace_tags(self, tags_to_remove: typing.Iterable[str], tags_to_add: typing.Iterable[str]):
        """
        Remove and add tags atomically; the removal is done first.
        The rules for `Run.add_tag` and `Run.remove_tag` also apply here.
        
        Parameters
        ----------
        tags_to_remove : Iterable[str]
            Tags to remove.
        tags_to_add : Iterable[str]
            Tags to add.
        """
        ...
    def __iter__(self) -> typing.Iterator[metaflow.client.core.Step]:
        """
        Iterate over all children Step of this Run
        
        Yields
        ------
        Step
            A Step in this Run
        """
        ...
    def __getitem__(self, name: str) -> metaflow.client.core.Step:
        """
        Returns the Step object with the step name 'name'
        
        Parameters
        ----------
        name : str
            Step name
        
        Returns
        -------
        Step
            Step for this step name in this Run
        
        Raises
        ------
        KeyError
            If the name does not identify a valid Step object
        """
        ...
    def __getstate__(self):
        ...
    def __setstate__(self, state):
        ...
    @property
    def trigger(self) -> typing.Optional[metaflow.events.Trigger]:
        """
        Returns a container of events that triggered this run.
        
        This returns None if the run was not triggered by any events.
        
        Returns
        -------
        Trigger, optional
            Container of triggering events
        """
        ...
    ...

current: metaflow.metaflow_current.Current

class CommandException(metaflow.exception.MetaflowException, metaclass=type):
    ...

class MetaflowNotFound(metaflow.exception.MetaflowException, metaclass=type):
    ...

class MetaflowInternalError(metaflow.exception.MetaflowException, metaclass=type):
    ...

class MetaflowNamespaceMismatch(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, namespace):
        ...
    ...

