##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.873423                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow

class MetaflowCard(object, metaclass=type):
    def __init__(self, options = {}, components = [], graph = None):
        ...
    def render(self, task: "metaflow.Task") -> str:
        """
        Produce custom card contents in HTML.
        
        Subclasses override this method to customize the card contents.
        
        Parameters
        ----------
        task : Task
            A `Task` object that allows you to access data from the finished task and tasks
            preceding it.
        
        Returns
        -------
        str
            Card contents as an HTML string.
        """
        ...
    def render_runtime(self, task, data):
        ...
    def refresh(self, task, data):
        ...
    def reload_content_token(self, task, data):
        ...
    ...

class MetaflowCardComponent(object, metaclass=type):
    @property
    def component_id(self):
        ...
    @component_id.setter
    def component_id(self, value):
        ...
    def update(self, *args, **kwargs):
        """
        #FIXME document
        """
        ...
    def render(self):
        """
        `render` returns a string or dictionary. This class can be called on the client side to dynamically add components to the `MetaflowCard`
        """
        ...
    ...

EXT_PKG: str

def iter_namespace(ns_pkg):
    ...

MF_EXTERNAL_CARDS: list

