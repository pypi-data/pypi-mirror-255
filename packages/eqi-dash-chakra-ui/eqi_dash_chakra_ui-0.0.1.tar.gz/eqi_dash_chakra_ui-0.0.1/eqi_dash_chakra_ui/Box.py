# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Box(Component):
    """A Box component.
Box Component

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Component Id.

- asProp (string; default "div"):
    Render element as tag.

- styleProps (dict; optional):
    StyleProp object."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'eqi_dash_chakra_ui'
    _type = 'Box'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, asProp=Component.UNDEFINED, styleProps=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'asProp', 'styleProps']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'asProp', 'styleProps']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Box, self).__init__(children=children, **args)
