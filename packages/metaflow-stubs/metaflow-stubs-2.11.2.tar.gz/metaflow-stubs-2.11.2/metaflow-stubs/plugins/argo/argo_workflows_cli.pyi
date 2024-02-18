##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.872854                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.parameters
    import metaflow.exception
    import metaflow.metaflow_current
    import metaflow.decorators

JSONType: metaflow.parameters.JSONTypeClass

current: metaflow.metaflow_current.Current

class MetaflowException(Exception, metaclass=type):
    def __init__(self, msg = "", lineno = None):
        ...
    def __str__(self):
        ...
    ...

class MetaflowInternalError(metaflow.exception.MetaflowException, metaclass=type):
    ...

ARGO_WORKFLOWS_UI_URL: None

KUBERNETES_NAMESPACE: str

SERVICE_VERSION_CHECK: bool

UI_URL: None

def load_token(token_prefix):
    ...

def new_token(token_prefix, prev_token = None):
    ...

def store_token(token_prefix, token):
    ...

class EnvironmentDecorator(metaflow.decorators.StepDecorator, metaclass=type):
    def runtime_step_cli(self, cli_args, retry_count, max_user_code_retries, ubf_context):
        ...
    ...

class KubernetesDecorator(metaflow.decorators.StepDecorator, metaclass=type):
    def __init__(self, attributes = None, statically_defined = False):
        ...
    def step_init(self, flow, graph, step, decos, environment, flow_datastore, logger):
        ...
    def package_init(self, flow, step_name, environment):
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

class ArgoWorkflows(object, metaclass=type):
    def __init__(self, name, graph, flow, code_package_sha, code_package_url, production_token, metadata, flow_datastore, environment, event_logger, monitor, tags = None, namespace = None, username = None, max_workers = None, workflow_timeout = None, workflow_priority = None, auto_emit_argo_events = False, notify_on_error = False, notify_on_success = False, notify_slack_webhook_url = None, notify_pager_duty_integration_key = None):
        ...
    def __str__(self):
        ...
    def deploy(self):
        ...
    @staticmethod
    def list_templates(flow_name, all = False):
        ...
    @staticmethod
    def delete(name):
        ...
    @classmethod
    def terminate(cls, flow_name, name):
        ...
    @staticmethod
    def get_workflow_status(flow_name, name):
        ...
    @staticmethod
    def suspend(name):
        ...
    @staticmethod
    def unsuspend(name):
        ...
    @classmethod
    def trigger(cls, name, parameters = None):
        ...
    def schedule(self):
        ...
    def trigger_explanation(self):
        ...
    @classmethod
    def get_existing_deployment(cls, name):
        ...
    @classmethod
    def get_execution(cls, name):
        ...
    def list_to_prose(self, items, singular):
        ...
    ...

class IncorrectProductionToken(metaflow.exception.MetaflowException, metaclass=type):
    ...

class RunIdMismatch(metaflow.exception.MetaflowException, metaclass=type):
    ...

class IncorrectMetadataServiceVersion(metaflow.exception.MetaflowException, metaclass=type):
    ...

class ArgoWorkflowsNameTooLong(metaflow.exception.MetaflowException, metaclass=type):
    ...

class UnsupportedPythonVersion(metaflow.exception.MetaflowException, metaclass=type):
    ...

def check_python_version(obj):
    ...

def check_metadata_service_version(obj):
    ...

def resolve_workflow_name(obj, name):
    ...

def make_flow(obj, token, name, tags, namespace, max_workers, workflow_timeout, workflow_priority, auto_emit_argo_events, notify_on_error, notify_on_success, notify_slack_webhook_url, notify_pager_duty_integration_key):
    ...

def resolve_token(name, token_prefix, obj, authorize, given_token, generate_new_token, is_project):
    ...

def validate_token(name, token_prefix, authorize, instructions_fn = None):
    """
    Validate that the production token matches that of the deployed flow.
    In case both the user and token do not match, raises an error.
    Optionally outputs instructions on token usage via the provided instruction_fn(flow_name, prev_user)
    """
    ...

def validate_run_id(workflow_name, token_prefix, authorize, run_id, instructions_fn = None):
    """
    Validates that a run_id adheres to the Argo Workflows naming rules, and
    that it belongs to the current flow (accounting for project branch as well).
    """
    ...

def sanitize_for_argo(text):
    """
    Sanitizes a string so it does not contain characters that are not permitted in Argo Workflow resource names.
    """
    ...

def remap_status(status):
    """
    Group similar Argo Workflow statuses together in order to have similar output to step functions statuses.
    """
    ...

