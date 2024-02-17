def clear_none_values_dict(d: dict) -> dict:
    c = dict()
    for k, v in d.items():
        if v is not None:
            c[k] = v
    return c
