##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.841201                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.metaflow_current
    import metaflow.decorators

class MetaflowException(Exception, metaclass=type):
    def __init__(self, msg = "", lineno = None):
        ...
    def __str__(self):
        ...
    ...

current: metaflow.metaflow_current.Current

VALID_NAME_RE: str

VALID_NAME_LEN: int

class ProjectDecorator(metaflow.decorators.FlowDecorator, metaclass=type):
    def flow_init(self, flow, graph, environment, flow_datastore, metadata, logger, echo, options):
        ...
    def get_top_level_options(self):
        ...
    ...

def format_name(flow_name, project_name, deploy_prod, given_branch, user_name):
    ...

