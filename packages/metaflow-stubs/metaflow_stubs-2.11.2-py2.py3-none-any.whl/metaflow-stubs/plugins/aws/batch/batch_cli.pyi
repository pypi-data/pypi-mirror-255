##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.905166                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.exception

class CommandException(metaflow.exception.MetaflowException, metaclass=type):
    ...

METAFLOW_EXIT_DISALLOW_RETRY: int

def sync_local_metadata_from_datastore(metadata_local_dir, task_ds):
    ...

DATASTORE_LOCAL_DIR: str

TASK_LOG_SOURCE: str

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

class BatchKilledException(metaflow.exception.MetaflowException, metaclass=type):
    ...

