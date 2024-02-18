##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.906739                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.exception
    import metaflow.decorators

class AirflowException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, msg):
        ...
    ...

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

def id_creator(val, hash_len):
    ...

TASK_ID_HASH_LEN: int

class AirflowSensorDecorator(metaflow.decorators.FlowDecorator, metaclass=type):
    def __init__(self, *args, **kwargs):
        ...
    def serialize_operator_args(self):
        """
        Subclasses will parse the decorator arguments to
        Airflow task serializable arguments.
        """
        ...
    def create_task(self):
        ...
    def validate(self):
        """
        Validate if the arguments for the sensor are correct.
        """
        ...
    def flow_init(self, flow, graph, environment, flow_datastore, metadata, logger, echo, options):
        ...
    ...

