import importlib


def test_interface_imports():
    # This test ensures interface_gui imports without raising, and exposes map availability flag
    mod = importlib.import_module('interface_gui')
    assert hasattr(mod, 'InterfaceOptimisation')
    app = mod.InterfaceOptimisation()
    # attribute should exist; map_available may be True or False depending on environment
    assert hasattr(app, 'map_available')
    assert hasattr(app, 'map_markers')
    # app should define map-related methods
    assert callable(getattr(app, 'add_map_marker_for_passager'))
    assert callable(getattr(app, 'clear_map_markers'))

