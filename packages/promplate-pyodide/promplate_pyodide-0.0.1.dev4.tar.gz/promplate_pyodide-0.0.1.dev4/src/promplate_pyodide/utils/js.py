# type: ignore


def to_js(obj):
    from pyodide.ffi import to_js

    return to_js(obj, dict_converter=Object.fromEntries)
