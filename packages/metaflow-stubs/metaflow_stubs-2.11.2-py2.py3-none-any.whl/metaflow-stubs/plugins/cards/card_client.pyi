##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.851788                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow
    import metaflow.exception
    import metaflow.plugins.cards.card_client

TYPE_CHECKING: bool

CARD_SUFFIX: str

def resolve_paths_from_task(flow_datastore, pathspec = None, type = None, hash = None, card_id = None):
    ...

def resumed_info(task):
    ...

class CardDatastore(object, metaclass=type):
    @classmethod
    def get_storage_root(cls, storage_type):
        ...
    def __init__(self, flow_datastore, pathspec = None):
        ...
    @classmethod
    def get_card_location(cls, base_path, card_name, uuid, card_id = None, suffix = "html"):
        ...
    @staticmethod
    def info_from_path(path, suffix = "html"):
        """
        Args:
            path (str): The path to the card
        
        Raises:
            Exception: When the card_path is invalid
        
        Returns:
            CardInfo
        """
        ...
    def save_data(self, uuid, card_type, json_data, card_id = None):
        ...
    def save_card(self, uuid, card_type, card_html, card_id = None, overwrite = True):
        ...
    def create_full_path(self, card_path):
        ...
    def get_card_names(self, card_paths):
        ...
    def get_card_html(self, path):
        ...
    def get_card_data(self, path):
        ...
    def cache_locally(self, path, save_path = None):
        """
        Saves the data present in the `path` the `metaflow_card_cache` directory or to the `save_path`.
        """
        ...
    def extract_data_paths(self, card_type = None, card_hash = None, card_id = None):
        ...
    def extract_card_paths(self, card_type = None, card_hash = None, card_id = None):
        ...
    ...

class CardNameSuffix(object, metaclass=type):
    ...

class UnresolvableDatastoreException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, task):
        ...
    ...

class IncorrectArgumentException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, obj_type):
        ...
    ...

class IncorrectPathspecException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, pthspec):
        ...
    ...

class Card(object, metaclass=type):
    def __init__(self, card_ds, type, path, hash, id = None, html = None, created_on = None, from_resumed = False, origin_pathspec = None):
        ...
    def get_data(self) -> typing.Optional[dict]:
        ...
    def get(self) -> str:
        """
        Retrieves the HTML contents of the card from the
        Metaflow datastore.
        
        Returns
        -------
        str
            HTML contents of the card.
        """
        ...
    @property
    def path(self) -> str:
        """
        The path of the card in the datastore which uniquely
        identifies the card.
        
        Returns
        -------
        str
            Path to the card
        """
        ...
    @property
    def id(self) -> typing.Optional[str]:
        """
        The ID of the card, if specified with `@card(id=ID)`.
        
        Returns
        -------
        Optional[str]
            ID of the card
        """
        ...
    def __str__(self):
        ...
    def view(self):
        """
        Opens the card in a local web browser.
        
        This call uses Python's built-in [`webbrowser`](https://docs.python.org/3/library/webbrowser.html)
        module to open the card.
        """
        ...
    ...

class CardContainer(object, metaclass=type):
    def __init__(self, card_paths, card_ds, origin_pathspec = None):
        ...
    def __len__(self):
        ...
    def __iter__(self):
        ...
    def __getitem__(self, index):
        ...
    ...

def get_cards(task: typing.Union[str, "metaflow.Task"], id: typing.Optional[str] = None, type: typing.Optional[str] = None, follow_resumed: bool = True) -> CardContainer:
    """
    Get cards related to a `Task`.
    
    Note that `get_cards` resolves the cards contained by the task, but it doesn't actually
    retrieve them from the datastore. Actual card contents are retrieved lazily either when
    the card is rendered in a notebook to when you call `Card.get`. This means that
    `get_cards` is a fast call even when individual cards contain a lot of data.
    
    Parameters
    ----------
    task : Union[str, `Task`]
        A `Task` object or pathspec `{flow_name}/{run_id}/{step_name}/{task_id}` that
        uniquely identifies a task.
    id : str, optional, default None
        The ID of card to retrieve if multiple cards are present.
    type : str, optional, default None
        The type of card to retrieve if multiple cards are present.
    follow_resumed : bool, default True
        If the task has been resumed, then setting this flag will resolve the card for
        the origin task.
    
    Returns
    -------
    CardContainer
        A list-like object that holds `Card` objects.
    """
    ...

