##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.818088                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.plugins.cards.card_modules.card
    import metaflow.unbounded_foreach

CLIS_DESC: list

class InternalTestUnboundedForeachInput(metaflow.unbounded_foreach.UnboundedForeachInput, metaclass=type):
    def __init__(self, iterable):
        ...
    def __iter__(self):
        ...
    def __next__(self):
        ...
    def __getitem__(self, key):
        ...
    def __len__(self):
        ...
    def __str__(self):
        ...
    def __repr__(self):
        ...
    ...

STEP_DECORATORS_DESC: list

FLOW_DECORATORS_DESC: list

ENVIRONMENTS_DESC: list

METADATA_PROVIDERS_DESC: list

DATASTORES_DESC: list

SIDECARS_DESC: list

LOGGING_SIDECARS_DESC: list

MONITOR_SIDECARS_DESC: list

AWS_CLIENT_PROVIDERS_DESC: list

SENSOR_FLOW_DECORATORS: list

SECRETS_PROVIDERS_DESC: list

def get_plugin_cli():
    ...

STEP_DECORATORS: list

FLOW_DECORATORS: list

ENVIRONMENTS: list

METADATA_PROVIDERS: list

DATASTORES: list

SIDECARS: dict

LOGGING_SIDECARS: dict

MONITOR_SIDECARS: dict

AWS_CLIENT_PROVIDERS: list

SECRETS_PROVIDERS: list

MF_EXTERNAL_CARDS: list

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

class DefaultCardJSON(metaflow.plugins.cards.card_modules.card.MetaflowCard, metaclass=type):
    def __init__(self, options = {"only_repr": True}, components = [], graph = None):
        ...
    def render(self, task):
        ...
    ...

class ErrorCard(metaflow.plugins.cards.card_modules.card.MetaflowCard, metaclass=type):
    def __init__(self, options = {}, components = [], graph = None):
        ...
    def render(self, task, stack_trace = None):
        ...
    ...

class TaskSpecCard(metaflow.plugins.cards.card_modules.card.MetaflowCard, metaclass=type):
    def render(self, task):
        ...
    ...

class TestEditableCard(metaflow.plugins.cards.card_modules.card.MetaflowCard, metaclass=type):
    def __init__(self, options = {}, components = [], graph = None):
        ...
    def render(self, task):
        ...
    ...

class TestEditableCard2(metaflow.plugins.cards.card_modules.card.MetaflowCard, metaclass=type):
    def __init__(self, options = {}, components = [], graph = None):
        ...
    def render(self, task):
        ...
    ...

class TestErrorCard(metaflow.plugins.cards.card_modules.card.MetaflowCard, metaclass=type):
    def render(self, task):
        ...
    ...

class TestMockCard(metaflow.plugins.cards.card_modules.card.MetaflowCard, metaclass=type):
    def __init__(self, options = {"key": "dummy_key"}, **kwargs):
        ...
    def render(self, task):
        ...
    ...

class TestNonEditableCard(metaflow.plugins.cards.card_modules.card.MetaflowCard, metaclass=type):
    def __init__(self, options = {}, components = [], graph = None):
        ...
    def render(self, task):
        ...
    ...

class TestPathSpecCard(metaflow.plugins.cards.card_modules.card.MetaflowCard, metaclass=type):
    def render(self, task):
        ...
    ...

class TestTimeoutCard(metaflow.plugins.cards.card_modules.card.MetaflowCard, metaclass=type):
    def __init__(self, options = {"timeout": 50}, **kwargs):
        ...
    def render(self, task):
        ...
    ...

class TestRefreshCard(metaflow.plugins.cards.card_modules.card.MetaflowCard, metaclass=type):
    def render(self, task) -> str:
        ...
    def render_runtime(self, task, data):
        ...
    def refresh(self, task, data):
        ...
    ...

class TestRefreshComponentCard(metaflow.plugins.cards.card_modules.card.MetaflowCard, metaclass=type):
    def __init__(self, options = {}, components = [], graph = None):
        ...
    def render(self, task) -> str:
        ...
    def render_runtime(self, task, data):
        ...
    def refresh(self, task, data):
        ...
    def reload_content_token(self, task, data):
        ...
    ...

CARDS: list

