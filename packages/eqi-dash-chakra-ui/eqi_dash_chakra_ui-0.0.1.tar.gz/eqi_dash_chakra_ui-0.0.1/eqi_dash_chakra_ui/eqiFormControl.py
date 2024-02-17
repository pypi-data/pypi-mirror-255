# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class eqiFormControl(Component):
    """An eqiFormControl component.


Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Children of the component.

- formProps (dict; optional):
    dict with Input props."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'eqi_dash_chakra_ui'
    _type = 'eqiFormControl'
    @_explicitize_args
    def __init__(self, children=None, formProps=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'formProps']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'formProps']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(eqiFormControl, self).__init__(children=children, **args)
