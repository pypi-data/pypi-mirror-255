##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.903597                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.exception

class S3Tail(object, metaclass=type):
    def __init__(self, s3url):
        ...
    def reset_client(self, hard_reset = False):
        ...
    def clone(self, s3url):
        ...
    @property
    def bytes_read(self):
        ...
    @property
    def tail(self):
        ...
    def __iter__(self):
        ...
    def _make_range_request(self, *args, **kwargs):
        ...
    ...

def sanitize_batch_tag(key, value):
    """
    Sanitize a key and value for use as a Batch tag.
    """
    ...

class MetaflowException(Exception, metaclass=type):
    def __init__(self, msg = "", lineno = None):
        ...
    def __str__(self):
        ...
    ...

SERVICE_INTERNAL_URL: None

DATATOOLS_S3ROOT: None

DATASTORE_SYSROOT_S3: None

DEFAULT_METADATA: str

SERVICE_HEADERS: dict

BATCH_EMIT_TAGS: bool

CARD_S3ROOT: None

S3_ENDPOINT_URL: None

DEFAULT_SECRETS_BACKEND_TYPE: None

AWS_SECRETS_MANAGER_DEFAULT_REGION: None

S3_SERVER_SIDE_ENCRYPTION: None

BASH_SAVE_LOGS: str

class BatchClient(object, metaclass=type):
    def __init__(self):
        ...
    def active_job_queues(self):
        ...
    def unfinished_jobs(self):
        ...
    def describe_jobs(self, job_ids):
        ...
    def describe_job_queue(self, job_queue):
        ...
    def job(self):
        ...
    def attach_job(self, job_id):
        ...
    def region(self):
        ...
    ...

LOGS_DIR: str

STDOUT_FILE: str

STDERR_FILE: str

STDOUT_PATH: str

STDERR_PATH: str

class BatchException(metaflow.exception.MetaflowException, metaclass=type):
    ...

class BatchKilledException(metaflow.exception.MetaflowException, metaclass=type):
    ...

class Batch(object, metaclass=type):
    def __init__(self, metadata, environment):
        ...
    def list_jobs(self, flow_name, run_id, user, echo):
        ...
    def kill_jobs(self, flow_name, run_id, user, echo):
        ...
    def create_job(self, step_name, step_cli, task_spec, code_package_sha, code_package_url, code_package_ds, image, queue, iam_role = None, execution_role = None, cpu = None, gpu = None, memory = None, run_time_limit = None, shared_memory = None, max_swap = None, swappiness = None, inferentia = None, efa = None, env = {}, attrs = {}, host_volumes = None, efs_volumes = None, use_tmpfs = None, tmpfs_tempdir = None, tmpfs_size = None, tmpfs_path = None, num_parallel = 0):
        ...
    def launch_job(self, step_name, step_cli, task_spec, code_package_sha, code_package_url, code_package_ds, image, queue, iam_role = None, execution_role = None, cpu = None, gpu = None, memory = None, run_time_limit = None, shared_memory = None, max_swap = None, swappiness = None, inferentia = None, efa = None, host_volumes = None, efs_volumes = None, use_tmpfs = None, tmpfs_tempdir = None, tmpfs_size = None, tmpfs_path = None, num_parallel = 0, env = {}, attrs = {}):
        ...
    def wait(self, stdout_location, stderr_location, echo = None):
        ...
    ...

