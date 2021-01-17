#coding:utf8

def _parse_size(value):
    try:
        if isinstance(value, (int, float)):
            assert value > 0
            value = str(value) + 'px'
        else:
            value = float(value.strip('%'))
            assert 0 <= value <= 100
            value = str(value) + '%'
    except Exception:
        msg = 'Cannot parse value {!r} as {!r}'.format
        raise ValueError(msg(value))
    return value

def camelize(key):
    """Convert a python_style_variable_name to lowerCamelCase.

    Examples
    --------
    >>> camelize('variable_name')
    'variableName'
    >>> camelize('variableName')
    'variableName'
    """
    return ''.join(x.capitalize() if i > 0 else x
                   for i, x in enumerate(key.split('_')))

def parse_options(**kwargs):
    """Return a dict with lower-camelcase keys and non-None values.."""
    return {camelize(key): value
            for key, value in kwargs.items()
            if value is not None}