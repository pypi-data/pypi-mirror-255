# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class eqiTable(Component):
    """An eqiTable component.


Keyword arguments:

- id (string; optional):
    The ID of the Table.

- tableProps (dict; optional):
    dict with Table props."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'eqi_dash_chakra_ui'
    _type = 'eqiTable'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, tableProps=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'tableProps']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'tableProps']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(eqiTable, self).__init__(**args)
