##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.900767                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.parameters
    import metaflow.exception
    import metaflow.metaflow_current
    import metaflow.decorators

current: metaflow.metaflow_current.Current

JSONType: metaflow.parameters.JSONTypeClass

SERVICE_VERSION_CHECK: bool

SFN_STATE_MACHINE_PREFIX: None

UI_URL: None

class MetaflowException(Exception, metaclass=type):
    def __init__(self, msg = "", lineno = None):
        ...
    def __str__(self):
        ...
    ...

class MetaflowInternalError(metaflow.exception.MetaflowException, metaclass=type):
    ...

class BatchDecorator(metaflow.decorators.StepDecorator, metaclass=type):
    def __init__(self, attributes = None, statically_defined = False):
        ...
    def step_init(self, flow, graph, step, decos, environment, flow_datastore, logger):
        ...
    def runtime_init(self, flow, graph, package, run_id):
        ...
    def runtime_task_created(self, task_datastore, task_id, split_index, input_paths, is_cloned, ubf_context):
        ...
    def runtime_step_cli(self, cli_args, retry_count, max_user_code_retries, ubf_context):
        ...
    def task_pre_step(self, step_name, task_datastore, metadata, run_id, task_id, flow, graph, retry_count, max_retries, ubf_context, inputs):
        ...
    def task_finished(self, step_name, flow, graph, is_task_ok, retry_count, max_retries):
        ...
    ...

def validate_tags(tags, existing_tags = None):
    """
    Raises MetaflowTaggingError if invalid based on these rules:
    
    Tag set size is too large. But it's OK if tag set is not larger
    than an existing tag set (if provided).
    
    Then, we validate each tag.  See validate_tag()
    """
    ...

class StepFunctions(object, metaclass=type):
    def __init__(self, name, graph, flow, code_package_sha, code_package_url, production_token, metadata, flow_datastore, environment, event_logger, monitor, tags = None, namespace = None, username = None, max_workers = None, workflow_timeout = None, is_project = False):
        ...
    def to_json(self):
        ...
    def trigger_explanation(self):
        ...
    def deploy(self, log_execution_history):
        ...
    def schedule(self):
        ...
    @classmethod
    def delete(cls, name):
        ...
    @classmethod
    def terminate(cls, flow_name, name):
        ...
    @classmethod
    def trigger(cls, name, parameters):
        ...
    @classmethod
    def list(cls, name, states):
        ...
    @classmethod
    def get_existing_deployment(cls, name):
        ...
    @classmethod
    def get_execution(cls, state_machine_name, name):
        ...
    ...

def load_token(token_prefix):
    ...

def store_token(token_prefix, token):
    ...

def new_token(token_prefix, prev_token = None):
    ...

class IncorrectProductionToken(metaflow.exception.MetaflowException, metaclass=type):
    ...

class RunIdMismatch(metaflow.exception.MetaflowException, metaclass=type):
    ...

class IncorrectMetadataServiceVersion(metaflow.exception.MetaflowException, metaclass=type):
    ...

class StepFunctionsStateMachineNameTooLong(metaflow.exception.MetaflowException, metaclass=type):
    ...

def check_metadata_service_version(obj):
    ...

def resolve_state_machine_name(obj, name):
    ...

def make_flow(obj, token, name, tags, namespace, max_workers, workflow_timeout, is_project):
    ...

def resolve_token(name, token_prefix, obj, authorize, given_token, generate_new_token, is_project):
    ...

def validate_run_id(state_machine_name, token_prefix, authorize, run_id, instructions_fn = None):
    ...

def validate_token(name, token_prefix, authorize, instruction_fn = None):
    """
    Validate that the production token matches that of the deployed flow.
    
    In case both the user and token do not match, raises an error.
    Optionally outputs instructions on token usage via the provided instruction_fn(flow_name, prev_user)
    """
    ...

