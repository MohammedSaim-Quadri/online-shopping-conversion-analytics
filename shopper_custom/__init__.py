"""A real Dash React component shipped as an unminified, editable JavaScript bundle.

The registration matches Dash's JavaScript component namespace. No external JS build
step is required for this educational project; D3 is loaded as an external script.
"""
from dash.development.base_component import Component

__version__ = "1.1.0"

# Dash discovers resources from the imported component package itself.
# Keep this module-level (not only on the component class).
_js_dist = [{"relative_package_path": "forkprint.js",
             "namespace": "shopper_custom"}]


class ConversionForkprint(Component):
    _type = 'ConversionForkprint'
    _namespace = 'shopper_custom'
    _valid_wildcard_attributes = []
    _prop_names = ['id', 'data', 'selected', 'setProps', 'className']
    available_properties = ['id', 'data', 'selected', 'setProps', 'className']
    available_wildcard_properties = []
    _js_dist = _js_dist

    def __init__(self, id=None, data=None, selected=None, className=None, **kwargs):
        kwargs.update({'id': id, 'data': data or [],
                      'selected': selected, 'className': className})
        super().__init__(**kwargs)
