value_bool = {'true': True, 'false': False}


def make_bool(**kwargs):
    for k, v in kwargs.items():
        if v.lower() in value_bool.keys():
            kwargs[k] = value_bool.get(v.lower())
    return kwargs
