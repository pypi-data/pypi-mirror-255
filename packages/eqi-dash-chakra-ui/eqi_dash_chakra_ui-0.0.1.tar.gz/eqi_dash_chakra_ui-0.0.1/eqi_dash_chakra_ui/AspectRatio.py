# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class AspectRatio(Component):
    """An AspectRatio component.
Aspect Ratio component

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Component Id.

- ratio (number; optional):
    Element ratio.

- styleProps (dict; optional):
    StyleProp object  Use maxWidth to adjust content width."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'eqi_dash_chakra_ui'
    _type = 'AspectRatio'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, ratio=Component.UNDEFINED, styleProps=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'ratio', 'styleProps']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'ratio', 'styleProps']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(AspectRatio, self).__init__(children=children, **args)
