##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.857628                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.exception
    import metaflow.metaflow_current

current: metaflow.metaflow_current.Current

class MetaflowException(Exception, metaclass=type):
    def __init__(self, msg = "", lineno = None):
        ...
    def __str__(self):
        ...
    ...

ARGO_EVENTS_EVENT: None

ARGO_EVENTS_EVENT_BUS: str

ARGO_EVENTS_EVENT_SOURCE: None

ARGO_EVENTS_SERVICE_ACCOUNT: None

ARGO_EVENTS_INTERNAL_WEBHOOK_URL: None

AWS_SECRETS_MANAGER_DEFAULT_REGION: None

ARGO_EVENTS_WEBHOOK_AUTH: str

AZURE_STORAGE_BLOB_SERVICE_ENDPOINT: None

CARD_AZUREROOT: None

CARD_GSROOT: None

CARD_S3ROOT: None

DATASTORE_SYSROOT_AZURE: None

DATASTORE_SYSROOT_GS: None

DATASTORE_SYSROOT_S3: None

DATATOOLS_S3ROOT: None

DEFAULT_AWS_CLIENT_PROVIDER: str

DEFAULT_METADATA: str

DEFAULT_SECRETS_BACKEND_TYPE: None

KUBERNETES_FETCH_EC2_METADATA: bool

KUBERNETES_LABELS: str

KUBERNETES_SANDBOX_INIT_SCRIPT: None

S3_ENDPOINT_URL: None

SERVICE_HEADERS: dict

SERVICE_INTERNAL_URL: None

S3_SERVER_SIDE_ENCRYPTION: None

OTEL_ENDPOINT: None

BASH_SAVE_LOGS: str

class KubernetesClient(object, metaclass=type):
    def __init__(self):
        ...
    def get(self):
        ...
    def job(self, **kwargs):
        ...
    ...

LOGS_DIR: str

STDOUT_FILE: str

STDERR_FILE: str

STDOUT_PATH: str

STDERR_PATH: str

class KubernetesException(metaflow.exception.MetaflowException, metaclass=type):
    ...

class KubernetesKilledException(metaflow.exception.MetaflowException, metaclass=type):
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

def validate_kube_labels(labels: typing.Optional[typing.Dict[str, typing.Optional[str]]]) -> bool:
    """
    Validate label values.
    
    This validates the kubernetes label values.  It does not validate the keys.
    Ideally, keys should be static and also the validation rules for keys are
    more complex than those for values.  For full validation rules, see:
    
    https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/#syntax-and-character-set
    """
    ...

def parse_kube_keyvalue_list(items: typing.List[str], requires_both: bool = True):
    ...

