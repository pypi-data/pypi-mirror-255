##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.864952                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow
    import metaflow.metaflow_current
    import metaflow.decorators
    import metaflow.events

current: metaflow.metaflow_current.Current

class Trigger(object, metaclass=type):
    def __init__(self, _meta = None):
        ...
    @classmethod
    def from_runs(cls, run_objs: typing.List["metaflow.Run"]):
        ...
    @property
    def event(self) -> typing.Optional[metaflow.events.MetaflowEvent]:
        """
        The `MetaflowEvent` object corresponding to the triggering event.
        
        If multiple events triggered the run, this property is the latest event.
        
        Returns
        -------
        MetaflowEvent, optional
            The latest event that triggered the run, if applicable.
        """
        ...
    @property
    def events(self) -> typing.Optional[typing.List[metaflow.events.MetaflowEvent]]:
        """
        The list of `MetaflowEvent` objects correspondings to all the triggering events.
        
        Returns
        -------
        List[MetaflowEvent], optional
            List of all events that triggered the run
        """
        ...
    @property
    def run(self) -> typing.Optional["metaflow.Run"]:
        """
        The corresponding `Run` object if the triggering event is a Metaflow run.
        
        In case multiple runs triggered the run, this property is the latest run.
        Returns `None` if none of the triggering events are a `Run`.
        
        Returns
        -------
        Run, optional
            Latest Run that triggered this run, if applicable.
        """
        ...
    @property
    def runs(self) -> typing.Optional[typing.List["metaflow.Run"]]:
        """
        The list of `Run` objects in the triggering events.
        Returns `None` if none of the triggering events are `Run` objects.
        
        Returns
        -------
        List[Run], optional
            List of runs that triggered this run, if applicable.
        """
        ...
    def __getitem__(self, key: str) -> typing.Union["metaflow.Run", metaflow.events.MetaflowEvent]:
        """
        If triggering events are runs, `key` corresponds to the flow name of the triggering run.
        Otherwise, `key` corresponds to the event name and a `MetaflowEvent` object is returned.
        
        Returns
        -------
        Union[Run, MetaflowEvent]
            `Run` object if triggered by a run. Otherwise returns a `MetaflowEvent`.
        """
        ...
    def __iter__(self):
        ...
    def __contains__(self, ident: str) -> bool:
        ...
    ...

class MetaDatum(tuple, metaclass=type):
    @staticmethod
    def __new__(_cls, field, value, type, tags):
        """
        Create new instance of MetaDatum(field, value, type, tags)
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

ARGO_EVENTS_WEBHOOK_URL: None

class ArgoEvent(object, metaclass=type):
    def __init__(self, name, url = None, payload = None, access_token = None):
        ...
    def add_to_payload(self, key, value):
        """
        Add a key-value pair in the payload. This is typically used to set parameters
        of triggered flows. Often, `key` is the parameter name you want to set to
        `value`. Overrides any existing value of `key`.
        
        Parameters
        ----------
        key : str
            Key
        value : str
            Value
        """
        ...
    def safe_publish(self, payload = None, ignore_errors = True):
        """
        Publishes an event when called inside a deployed workflow. Outside a deployed workflow
        this function does nothing.
        
        Use this function inside flows to create events safely. As this function is a no-op
        for local runs, you can safely call it during local development without causing unintended
        side-effects. It takes effect only when deployed on Argo Workflows.
        
        Parameters
        ----------
        payload : dict
            Additional key-value pairs to add to the payload.
        ignore_errors : bool, default True
            If True, events are created on a best effort basis - errors are silently ignored.
        """
        ...
    def publish(self, payload = None, force = True, ignore_errors = True):
        """
        Publishes an event.
        
        Note that the function returns immediately after the event has been sent. It
        does not wait for flows to start, nor it guarantees that any flows will start.
        
        Parameters
        ----------
        payload : dict
            Additional key-value pairs to add to the payload.
        ignore_errors : bool, default True
            If True, events are created on a best effort basis - errors are silently ignored.
        """
        ...
    ...

class ArgoWorkflowsInternalDecorator(metaflow.decorators.StepDecorator, metaclass=type):
    def task_pre_step(self, step_name, task_datastore, metadata, run_id, task_id, flow, graph, retry_count, max_user_code_retries, ubf_context, inputs):
        ...
    def task_finished(self, step_name, flow, graph, is_task_ok, retry_count, max_user_code_retries):
        ...
    ...

