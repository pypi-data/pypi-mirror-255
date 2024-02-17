# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Container(Component):
    """A Container component.
Container Component

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Component Id.

- centerContent (boolean; default False):
    Center content.

- colorScheme (string; optional):
    ColorScheme  Not implemented in the default theme.

- size (string; optional):
    Component size  Not implemented in the default theme.

- styleProps (dict; optional):
    StyleProp object.

- variant (string; optional):
    Component variant  Not implemented in the default theme."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'eqi_dash_chakra_ui'
    _type = 'Container'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, centerContent=Component.UNDEFINED, colorScheme=Component.UNDEFINED, size=Component.UNDEFINED, variant=Component.UNDEFINED, styleProps=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'centerContent', 'colorScheme', 'size', 'styleProps', 'variant']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'centerContent', 'colorScheme', 'size', 'styleProps', 'variant']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Container, self).__init__(children=children, **args)
