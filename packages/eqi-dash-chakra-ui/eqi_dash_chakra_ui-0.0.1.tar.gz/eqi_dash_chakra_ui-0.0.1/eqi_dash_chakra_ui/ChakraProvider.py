# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class ChakraProvider(Component):
    """A ChakraProvider component.
Chakra UI context provider

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- resetCSS (boolean; default True):
    Reset CSS inside provider.

- themeExtension (dict; optional):
    Object to extend Chakra UI theme."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'eqi_dash_chakra_ui'
    _type = 'ChakraProvider'
    @_explicitize_args
    def __init__(self, children=None, themeExtension=Component.UNDEFINED, resetCSS=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'resetCSS', 'themeExtension']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'resetCSS', 'themeExtension']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(ChakraProvider, self).__init__(children=children, **args)
