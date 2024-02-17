# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class eqiInput(Component):
    """An eqiInput component.


Keyword arguments:

- id (string; optional):
    The ID of the Input.

- formProps (dict; optional):
    Dict with FormControl props.

- inputProps (dict; optional):
    Dict with Input props.

- n_submit (number; optional):
    Number of times Enter key was pressed.

- value (string; optional):
    Value of the Input."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'eqi_dash_chakra_ui'
    _type = 'eqiInput'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, formProps=Component.UNDEFINED, inputProps=Component.UNDEFINED, value=Component.UNDEFINED, n_submit=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'formProps', 'inputProps', 'n_submit', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'formProps', 'inputProps', 'n_submit', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(eqiInput, self).__init__(**args)
