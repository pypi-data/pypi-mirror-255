# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class eqiThemeProvider(Component):
    """An eqiThemeProvider component.


Keyword arguments:

- children (string; optional):
    Components to style with ThemeProvider.

- colorScheme (dict; optional):
    Scheme of colors (eqi | euQueroInvestir | research)."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'eqi_dash_chakra_ui'
    _type = 'eqiThemeProvider'
    @_explicitize_args
    def __init__(self, children=None, colorScheme=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'colorScheme']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'colorScheme']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(eqiThemeProvider, self).__init__(children=children, **args)
