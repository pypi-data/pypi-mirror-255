##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.854653                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.plugins.cards.card_modules.basic
    import typing
    import metaflow.plugins.cards.card_modules.card
    import metaflow.plugins.cards.card_modules.components

class LogComponent(metaflow.plugins.cards.card_modules.basic.DefaultComponent, metaclass=type):
    def __init__(self, data = None):
        ...
    def render(self):
        ...
    ...

class ErrorComponent(metaflow.plugins.cards.card_modules.card.MetaflowCardComponent, metaclass=type):
    def __init__(self, headline, error_message):
        ...
    def render(self):
        ...
    ...

class ArtifactsComponent(metaflow.plugins.cards.card_modules.basic.DefaultComponent, metaclass=type):
    def __init__(self, title = None, subtitle = None, data = {}):
        ...
    def render(self):
        ...
    ...

class TableComponent(metaflow.plugins.cards.card_modules.basic.DefaultComponent, metaclass=type):
    def __init__(self, title = None, subtitle = None, headers = [], data = [[]], vertical = False):
        ...
    @classmethod
    def validate(cls, headers, data):
        ...
    def render(self):
        ...
    ...

class ImageComponent(metaflow.plugins.cards.card_modules.basic.DefaultComponent, metaclass=type):
    def __init__(self, src = None, label = None, title = None, subtitle = None):
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

class MarkdownComponent(metaflow.plugins.cards.card_modules.basic.DefaultComponent, metaclass=type):
    def __init__(self, text = None):
        ...
    def render(self):
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

class TaskToDict(object, metaclass=type):
    def __init__(self, only_repr = False, runtime = False):
        ...
    def __call__(self, task, graph = None):
        ...
    def object_type(self, object):
        ...
    def parse_image(self, data_object):
        ...
    def infer_object(self, artifact_object):
        ...
    ...

def render_safely(func):
    """
    This is a decorator that can be added to any `MetaflowCardComponent.render`
    The goal is to render subcomponents safely and ensure that they are JSON serializable.
    """
    ...

def create_component_id(component):
    ...

def with_default_component_id(func):
    ...

class UserComponent(metaflow.plugins.cards.card_modules.card.MetaflowCardComponent, metaclass=type):
    def update(self, *args, **kwargs):
        ...
    ...

class StubComponent(UserComponent, metaclass=type):
    def __init__(self, component_id):
        ...
    def update(self, *args, **kwargs):
        ...
    ...

class Artifact(UserComponent, metaclass=type):
    def update(self, artifact):
        ...
    def __init__(self, artifact: typing.Any, name: typing.Optional[str] = None, compressed: bool = True):
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class Table(UserComponent, metaclass=type):
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

class Image(UserComponent, metaclass=type):
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

class Error(UserComponent, metaclass=type):
    def __init__(self, exception, title = None):
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class Markdown(UserComponent, metaclass=type):
    def update(self, text = None):
        ...
    def __init__(self, text = None):
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class ProgressBar(UserComponent, metaclass=type):
    def __init__(self, max: int = 100, label: str = None, value: int = 0, unit: str = None, metadata: str = None):
        ...
    def update(self, new_value: int, metadata: str = None):
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class VegaChart(UserComponent, metaclass=type):
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

