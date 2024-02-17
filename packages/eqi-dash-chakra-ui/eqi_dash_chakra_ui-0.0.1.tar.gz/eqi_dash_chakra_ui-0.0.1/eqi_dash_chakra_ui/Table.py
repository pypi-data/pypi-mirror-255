# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Table(Component):
    """A Table component.


Keyword arguments:

- id (string; optional):
    The ID of the Table.

- colorScheme (string; optional):
    Scheme of colors in the Table (ChakraUI).

- layout (a list of or a singular dash component, string or number; optional):
    Type of data in the layout (boolean, string, number...).

- placement (string; optional):
    Position of Table Caption (Chakra UI).

- size (string; optional):
    Size of the Table (sm,md,lg).

- td (dict; optional):
    Table Data.

- th (dict; optional):
    Table Headers.

- variant (string; optional):
    Striped, simple or unstyled."""
    _children_props = ['layout']
    _base_nodes = ['layout', 'children']
    _namespace = 'eqi_dash_chakra_ui'
    _type = 'Table'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, colorScheme=Component.UNDEFINED, layout=Component.UNDEFINED, size=Component.UNDEFINED, variant=Component.UNDEFINED, td=Component.UNDEFINED, th=Component.UNDEFINED, placement=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'colorScheme', 'layout', 'placement', 'size', 'td', 'th', 'variant']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'colorScheme', 'layout', 'placement', 'size', 'td', 'th', 'variant']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Table, self).__init__(**args)
