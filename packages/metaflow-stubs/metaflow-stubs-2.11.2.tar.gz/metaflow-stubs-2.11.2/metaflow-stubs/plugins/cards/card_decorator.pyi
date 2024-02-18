##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.877080                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.metaflow_current
    import metaflow.decorators

current: metaflow.metaflow_current.Current

class CardComponentCollector(object, metaclass=type):
    def __init__(self, logger = None, card_creator = None):
        ...
    @staticmethod
    def create_uuid():
        ...
    def get(self, type = None):
        """
        `get`
        gets all the components arrays for a card `type`.
        Since one `@step` can have many `@card` decorators, many decorators can have the same type. That is why this function returns a list of lists.
        
        Args:
            type ([str], optional): `type` of MetaflowCard. Defaults to None.
        
        Returns: will return empty `list` if `type` is None or not found
            List[List[MetaflowCardComponent]]
        """
        ...
    def __getitem__(self, key):
        """
        Choose a specific card for manipulation.
        
        When multiple @card decorators are present, you can add an
        `ID` to distinguish between them, `@card(id=ID)`. This allows you
        to add components to a specific card like this:
        ```
        current.card[ID].append(component)
        ```
        
        Parameters
        ----------
        key : str
            Card ID.
        
        Returns
        -------
        CardComponentManager
            An object with `append` and `extend` calls which allow you to
            add components to the chosen card.
        """
        ...
    def __setitem__(self, key, value):
        """
        Specify components of the chosen card.
        
        Instead of adding components to a card individually with `current.card[ID].append(component)`,
        use this method to assign a list of components to a card, replacing the existing components:
        ```
        current.card[ID] = [FirstComponent, SecondComponent]
        ```
        
        Parameters
        ----------
        key: str
            Card ID.
        
        value: List[MetaflowCardComponent]
            List of card components to assign to this card.
        """
        ...
    def append(self, component, id = None):
        """
        Appends a component to the current card.
        
        Parameters
        ----------
        component : MetaflowCardComponent
            Card component to add to this card.
        """
        ...
    def extend(self, components):
        """
        Appends many components to the current card.
        
        Parameters
        ----------
        component : Iterator[MetaflowCardComponent]
            Card components to add to this card.
        """
        ...
    @property
    def components(self):
        ...
    def clear(self):
        ...
    def refresh(self, *args, **kwargs):
        ...
    ...

def get_card_class(card_type):
    ...

class CardCreator(object, metaclass=type):
    def __init__(self, top_level_options):
        ...
    def create(self, card_uuid = None, user_set_card_id = None, runtime_card = False, decorator_attributes = None, card_options = None, logger = None, mode = "render", final = False, sync = False):
        ...
    ...

TYPE_CHECK_REGEX: str

ASYNC_TIMEOUT: int

def warning_message(message, logger = None, ts = False):
    ...

class CardDecorator(metaflow.decorators.StepDecorator, metaclass=type):
    def __init__(self, *args, **kwargs):
        ...
    def step_init(self, flow, graph, step_name, decorators, environment, flow_datastore, logger):
        ...
    def task_pre_step(self, step_name, task_datastore, metadata, run_id, task_id, flow, graph, retry_count, max_user_code_retries, ubf_context, inputs):
        ...
    def task_finished(self, step_name, flow, graph, is_task_ok, retry_count, max_user_code_retries):
        ...
    ...

