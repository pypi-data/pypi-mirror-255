# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Center(Component):
    """A Center component.
Center component

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Component Id.

- styleProps (dict; optional):
    StyleProp object."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'eqi_dash_chakra_ui'
    _type = 'Center'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, styleProps=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'styleProps']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'styleProps']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Center, self).__init__(children=children, **args)
