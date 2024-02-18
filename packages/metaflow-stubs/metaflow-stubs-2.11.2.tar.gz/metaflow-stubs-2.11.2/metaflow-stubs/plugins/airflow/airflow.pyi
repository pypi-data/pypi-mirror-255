##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.886512                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow._vendor.click.types
    import metaflow.metaflow_current
    import metaflow.exception

current: metaflow.metaflow_current.Current

class MetaflowException(Exception, metaclass=type):
    def __init__(self, msg = "", lineno = None):
        ...
    def __str__(self):
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

AIRFLOW_KUBERNETES_CONN_ID: None

AIRFLOW_KUBERNETES_KUBECONFIG_CONTEXT: None

AIRFLOW_KUBERNETES_KUBECONFIG_FILE: None

AIRFLOW_KUBERNETES_STARTUP_TIMEOUT_SECONDS: int

AWS_SECRETS_MANAGER_DEFAULT_REGION: None

AZURE_STORAGE_BLOB_SERVICE_ENDPOINT: None

CARD_AZUREROOT: None

CARD_GSROOT: None

CARD_S3ROOT: None

DATASTORE_SYSROOT_AZURE: None

DATASTORE_SYSROOT_GS: None

DATASTORE_SYSROOT_S3: None

DATATOOLS_S3ROOT: None

DEFAULT_SECRETS_BACKEND_TYPE: None

KUBERNETES_SECRETS: str

KUBERNETES_SERVICE_ACCOUNT: None

S3_ENDPOINT_URL: None

SERVICE_HEADERS: dict

SERVICE_INTERNAL_URL: None

class DelayedEvaluationParameter(object, metaclass=type):
    def __init__(self, name, field, fun):
        ...
    def __call__(self, return_str = False):
        ...
    ...

class JSONTypeClass(metaflow._vendor.click.types.ParamType, metaclass=type):
    def convert(self, value, param, ctx):
        ...
    def __str__(self):
        ...
    def __repr__(self):
        ...
    ...

def deploy_time_eval(value):
    ...

class Kubernetes(object, metaclass=type):
    def __init__(self, datastore, metadata, environment):
        ...
    def launch_job(self, **kwargs):
        ...
    def create_job(self, flow_name, run_id, step_name, task_id, attempt, user, code_package_sha, code_package_url, code_package_ds, step_cli, docker_image, docker_image_pull_policy, service_account = None, secrets = None, node_selector = None, namespace = None, cpu = None, gpu = None, gpu_vendor = None, disk = None, memory = None, use_tmpfs = None, tmpfs_tempdir = None, tmpfs_size = None, tmpfs_path = None, run_time_limit = None, env = None, persistent_volume_claims = None, tolerations = None, labels = None, shared_memory = None):
        ...
    def wait(self, stdout_location, stderr_location, echo = None):
        ...
    ...

def get_run_time_limit_for_task(step_decos):
    ...

class AIRFLOW_MACROS(object, metaclass=type):
    @classmethod
    def create_task_id(cls, is_foreach):
        ...
    @classmethod
    def pathspec(cls, flowname, is_foreach = False):
        ...
    ...

TASK_ID_XCOM_KEY: str

class AirflowTask(object, metaclass=type):
    def __init__(self, name, operator_type = "kubernetes", flow_name = None, is_mapper_node = False, flow_contains_foreach = False):
        ...
    @property
    def is_mapper_node(self):
        ...
    def set_operator_args(self, **kwargs):
        ...
    def to_dict(self):
        ...
    @classmethod
    def from_dict(cls, task_dict, flow_name = None, flow_contains_foreach = False):
        ...
    def to_task(self):
        ...
    ...

class Workflow(object, metaclass=type):
    def __init__(self, file_path = None, graph_structure = None, metadata = None, **kwargs):
        ...
    def set_parameters(self, params):
        ...
    def add_state(self, state):
        ...
    def to_dict(self):
        ...
    def to_json(self):
        ...
    @classmethod
    def from_dict(cls, data_dict):
        ...
    @classmethod
    def from_json(cls, json_string):
        ...
    def compile(self):
        ...
    ...

class AirflowException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, msg):
        ...
    ...

SUPPORTED_SENSORS: list

AIRFLOW_DEPLOY_TEMPLATE_FILE: str

class Airflow(object, metaclass=type):
    def __init__(self, name, graph, flow, code_package_sha, code_package_url, metadata, flow_datastore, environment, event_logger, monitor, production_token, tags = None, namespace = None, username = None, max_workers = None, worker_pool = None, description = None, file_path = None, workflow_timeout = None, is_paused_upon_creation = True):
        ...
    @classmethod
    def get_existing_deployment(cls, name, flow_datastore):
        ...
    @classmethod
    def get_token_path(cls, name):
        ...
    @classmethod
    def save_deployment_token(cls, owner, name, token, flow_datastore):
        ...
    def compile(self):
        ...
    ...

