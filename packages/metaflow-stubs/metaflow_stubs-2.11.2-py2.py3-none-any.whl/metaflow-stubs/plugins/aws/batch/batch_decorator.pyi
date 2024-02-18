##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.904490                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.exception
    import metaflow.metaflow_current
    import metaflow.decorators

current: metaflow.metaflow_current.Current

class ResourcesDecorator(metaflow.decorators.StepDecorator, metaclass=type):
    ...

def get_run_time_limit_for_task(step_decos):
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

def sync_local_metadata_to_datastore(metadata_local_dir, task_ds):
    ...

ECS_S3_ACCESS_IAM_ROLE: None

BATCH_JOB_QUEUE: None

BATCH_CONTAINER_IMAGE: None

BATCH_CONTAINER_REGISTRY: None

ECS_FARGATE_EXECUTION_ROLE: None

DATASTORE_LOCAL_DIR: str

UBF_CONTROL: str

class BatchException(metaflow.exception.MetaflowException, metaclass=type):
    ...

def compute_resource_attributes(decos, compute_deco, resource_defaults):
    """
    Compute resource values taking into account defaults, the values specified
    in the compute decorator (like @batch or @kubernetes) directly, and
    resources specified via @resources decorator.
    
    Returns a dictionary of resource attr -> value (str).
    """
    ...

def get_docker_registry(image_uri):
    """
    Explanation:
        (.+?(?:[:.].+?)\/)? - [GROUP 0] REGISTRY
            .+?                  - A registry must start with at least one character
            (?:[:.].+?)\/       - A registry must have ":" or "." and end with "/"
            ?                    - Make a registry optional
        (.*?)                - [GROUP 1] REPOSITORY
            .*?                  - Get repository name until separator
        (?:[@:])?            - SEPARATOR
            ?:                   - Don't capture separator
            [@:]                 - The separator must be either "@" or ":"
            ?                    - The separator is optional
        ((?<=[@:]).*)?       - [GROUP 2] TAG / DIGEST
            (?<=[@:])            - A tag / digest must be preceded by "@" or ":"
            .*                   - Capture rest of tag / digest
            ?                    - A tag / digest is optional
    Examples:
        image
            - None
            - image
            - None
        example/image
            - None
            - example/image
            - None
        example/image:tag
            - None
            - example/image
            - tag
        example.domain.com/example/image:tag
            - example.domain.com/
            - example/image
            - tag
        123.123.123.123:123/example/image:tag
            - 123.123.123.123:123/
            - example/image
            - tag
        example.domain.com/example/image@sha256:45b23dee0
            - example.domain.com/
            - example/image
            - sha256:45b23dee0
    """
    ...

def get_ec2_instance_metadata():
    """
    Fetches the EC2 instance metadata through AWS instance metadata service
    
    Returns either an empty dictionary, or one with the keys
        - ec2-instance-id
        - ec2-instance-type
        - ec2-region
        - ec2-availability-zone
    """
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

