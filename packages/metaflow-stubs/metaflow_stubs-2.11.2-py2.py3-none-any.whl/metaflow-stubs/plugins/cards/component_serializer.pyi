##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.875891                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.plugins.cards.card_modules.basic
    import metaflow.plugins.cards.card_modules.card
    import metaflow.plugins.cards.card_modules.components
    import metaflow.exception

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

class ErrorComponent(metaflow.plugins.cards.card_modules.card.MetaflowCardComponent, metaclass=type):
    def __init__(self, headline, error_message):
        ...
    def render(self):
        ...
    ...

class SectionComponent(metaflow.plugins.cards.card_modules.basic.DefaultComponent, metaclass=type):
    def __init__(self, title = None, subtitle = None, columns = None, contents = []):
        ...
    @classmethod
    def render_subcomponents(cls, component_array, additional_allowed_types = [str, dict], allow_unknowns = False):
        ...
    def render(self):
        ...
    ...

class UserComponent(metaflow.plugins.cards.card_modules.card.MetaflowCardComponent, metaclass=type):
    def update(self, *args, **kwargs):
        ...
    ...

def create_component_id(component):
    ...

class StubComponent(metaflow.plugins.cards.card_modules.components.UserComponent, metaclass=type):
    def __init__(self, component_id):
        ...
    def update(self, *args, **kwargs):
        ...
    ...

class ComponentOverwriteNotSupportedException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, component_id, card_id, card_type):
        ...
    ...

RUNTIME_CARD_RENDER_INTERVAL: int

def get_card_class(card_type):
    ...

def warning_message(message, logger = None, ts = False):
    ...

class WarningComponent(metaflow.plugins.cards.card_modules.basic.ErrorComponent, metaclass=type):
    def __init__(self, warning_message):
        ...
    ...

class ComponentStore(object, metaclass=type):
    def __init__(self, logger, card_type = None, components = None, user_set_id = None):
        ...
    @property
    def layout_last_changed_on(self):
        """
        This property helps the CardComponentManager identify when the layout of the card has changed so that it can trigger a re-render of the card.
        """
        ...
    def __iter__(self):
        ...
    def __setitem__(self, key, value):
        ...
    def __getitem__(self, key):
        ...
    def __delitem__(self, key):
        ...
    def __contains__(self, key):
        ...
    def append(self, component, id = None):
        ...
    def extend(self, components):
        ...
    def clear(self):
        ...
    def keys(self):
        ...
    def values(self):
        ...
    def __str__(self):
        ...
    def __len__(self):
        ...
    ...

class CardComponentManager(object, metaclass=type):
    def __init__(self, card_uuid, decorator_attributes, card_creator, components = None, logger = None, no_warnings = False, user_set_card_id = None, runtime_card = False, card_options = None, refresh_interval = 5):
        ...
    def append(self, component, id = None):
        ...
    def extend(self, components):
        ...
    def clear(self):
        ...
    def refresh(self, data = None, force = False):
        ...
    @property
    def components(self):
        ...
    def __iter__(self):
        ...
    ...

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

