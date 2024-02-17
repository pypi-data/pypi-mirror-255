# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class GridItem(Component):
    """A GridItem component.
GridItem component
To be used as child of Grid component
See: https://chakra-ui.com/docs/layout/grid#spanning-columns

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Component Id.

- colEnd (number; optional):
    Column number that grid item should end.

- colSpan (number; optional):
    Number of columns that the item should span.

- colStart (number; optional):
    Column number that grid item should start.

- rowEnd (number; optional):
    Row number that grid item should end.

- rowSpan (number; optional):
    Number of rows that the item should span.

- rowStart (number; optional):
    Row number that grid item should start.

- styleProps (dict; optional):
    StyleProp object."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'eqi_dash_chakra_ui'
    _type = 'GridItem'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, colSpan=Component.UNDEFINED, colStart=Component.UNDEFINED, colEnd=Component.UNDEFINED, rowSpan=Component.UNDEFINED, rowStart=Component.UNDEFINED, rowEnd=Component.UNDEFINED, styleProps=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'colEnd', 'colSpan', 'colStart', 'rowEnd', 'rowSpan', 'rowStart', 'styleProps']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'colEnd', 'colSpan', 'colStart', 'rowEnd', 'rowSpan', 'rowStart', 'styleProps']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(GridItem, self).__init__(children=children, **args)
