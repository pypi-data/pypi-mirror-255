##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.828211                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.plugins.cards.card_modules.basic
    import metaflow
    import typing
    import metaflow.plugins.cards.card_client
    import metaflow.plugins.cards.card_modules.components
    import metaflow.plugins.cards.card_modules.card

def get_cards(task: typing.Union[str, "metaflow.Task"], id: typing.Optional[str] = None, type: typing.Optional[str] = None, follow_resumed: bool = True) -> metaflow.plugins.cards.card_client.CardContainer:
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

class Artifact(metaflow.plugins.cards.card_modules.components.UserComponent, metaclass=type):
    def update(self, artifact):
        ...
    def __init__(self, artifact: typing.Any, name: typing.Optional[str] = None, compressed: bool = True):
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class Table(metaflow.plugins.cards.card_modules.components.UserComponent, metaclass=type):
    def update(self, *args, **kwargs):
        ...
    def __init__(self, data: typing.Optional[typing.List[typing.List[typing.Union[str, metaflow.plugins.cards.card_modules.card.MetaflowCardComponent]]]] = None, headers: typing.Optional[typing.List[str]] = None, disable_updates: bool = False):
        ...
    @classmethod
    def from_dataframe(cls, dataframe = None, truncate: bool = True):
        """
        Create a `Table` based on a Pandas dataframe.
        
        Parameters
        ----------
        dataframe : Optional[pandas.DataFrame]
            Pandas dataframe.
        truncate : bool, default: True
            Truncate large dataframe instead of showing all rows (default: True).
        """
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class Image(metaflow.plugins.cards.card_modules.components.UserComponent, metaclass=type):
    @staticmethod
    def render_fail_headline(msg):
        ...
    def __init__(self, src = None, label = None, disable_updates: bool = True):
        ...
    @classmethod
    def from_pil_image(cls, pilimage, label: typing.Optional[str] = None, disable_updates: bool = False):
        """
        Create an `Image` from a PIL image.
        
        Parameters
        ----------
        pilimage : PIL.Image
            a PIL image object.
        label : str, optional
            Optional label for the image.
        """
        ...
    @classmethod
    def from_matplotlib(cls, plot, label: typing.Optional[str] = None, disable_updates: bool = False):
        """
        Create an `Image` from a Matplotlib plot.
        
        Parameters
        ----------
        plot :  matplotlib.figure.Figure or matplotlib.axes.Axes or matplotlib.axes._subplots.AxesSubplot
            a PIL axes (plot) object.
        label : str, optional
            Optional label for the image.
        """
        ...
    def render(self, *args, **kwargs):
        ...
    def update(self, image, label = None):
        """
        Update the image.
        
        Parameters
        ----------
        image : PIL.Image or matplotlib.figure.Figure or matplotlib.axes.Axes or matplotlib.axes._subplots.AxesSubplot or bytes or str
            The updated image object
        label : str, optional
            Optional label for the image.
        """
        ...
    ...

class Error(metaflow.plugins.cards.card_modules.components.UserComponent, metaclass=type):
    def __init__(self, exception, title = None):
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class Markdown(metaflow.plugins.cards.card_modules.components.UserComponent, metaclass=type):
    def update(self, text = None):
        ...
    def __init__(self, text = None):
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class VegaChart(metaflow.plugins.cards.card_modules.components.UserComponent, metaclass=type):
    def __init__(self, spec: dict, show_controls: bool = False):
        ...
    def update(self, spec = None):
        """
        Update the chart.
        
        Parameters
        ----------
        spec : dict or altair.Chart
            The updated chart spec or an altair Chart Object.
        """
        ...
    @classmethod
    def from_altair_chart(cls, altair_chart):
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class ProgressBar(metaflow.plugins.cards.card_modules.components.UserComponent, metaclass=type):
    def __init__(self, max: int = 100, label: str = None, value: int = 0, unit: str = None, metadata: str = None):
        ...
    def update(self, new_value: int, metadata: str = None):
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class DefaultCard(metaflow.plugins.cards.card_modules.card.MetaflowCard, metaclass=type):
    def __init__(self, options = {"only_repr": True}, components = [], graph = None):
        ...
    def render(self, task, runtime = False):
        ...
    def render_runtime(self, task, data):
        ...
    def refresh(self, task, data):
        ...
    def reload_content_token(self, task, data):
        """
        The reload token will change when the component array has changed in the Metaflow card.
        The change in the component array is signified by the change in the component_update_ts.
        """
        ...
    ...

class PageComponent(metaflow.plugins.cards.card_modules.basic.DefaultComponent, metaclass=type):
    def __init__(self, title = None, subtitle = None, contents = []):
        ...
    def render(self):
        ...
    ...

class ErrorCard(metaflow.plugins.cards.card_modules.card.MetaflowCard, metaclass=type):
    def __init__(self, options = {}, components = [], graph = None):
        ...
    def render(self, task, stack_trace = None):
        ...
    ...

class BlankCard(metaflow.plugins.cards.card_modules.card.MetaflowCard, metaclass=type):
    def __init__(self, options = {"title": ""}, components = [], graph = None):
        ...
    def render(self, task, components = [], runtime = False):
        ...
    def render_runtime(self, task, data):
        ...
    def refresh(self, task, data):
        ...
    def reload_content_token(self, task, data):
        """
        The reload token will change when the component array has changed in the Metaflow card.
        The change in the component array is signified by the change in the component_update_ts.
        """
        ...
    ...

