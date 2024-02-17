import json
from pathlib import Path

import yaml


class AbcDict(dict):
    __k_keylist__ = [
        'update',
        'pop',
        'merge',
        'deep_merge',
        'dump'
    ]

    def __init__(self, d=None, **kwargs):
        d = self.__load__(d, **kwargs)
        for k, v in d.items():
            setattr(self, k, v)

        for k in self.__class__.__dict__.keys():
            if (
                not (k.startswith('__') and k.endswith('__'))
                and k not in (self.__k_keylist__)
            ):
                setattr(self, k, getattr(self, k))

    def __getattr__(self, name):
        return None

    def __setattr__(self, name, value):
        if isinstance(value, (list, tuple)):
            value = [
                self.__class__(x) if isinstance(x, dict) else x for x in value
            ]
        elif isinstance(value, dict) and not isinstance(value, self.__class__):
            value = self.__class__(value)
        super(AbcDict, self).__setattr__(name, value)
        super(AbcDict, self).__setitem__(name, value)

    __setitem__ = __setattr__

    def __load__(self, d=None, **kwargs):
        if not isinstance(d, dict):
            # d = {} if d is None else self.__load__(d)
            if d:
                assert (
                    (isStr := isinstance(d, str)) or isinstance(d, Path)
                ), f'parameter {d} error'
                _d = Path(d) if isStr else d
                assert _d.exists(), f'{d} not find'
                d = yaml.safe_load(_d.open('r').read())
            else:
                d = {}
        if kwargs:
            d.update(**kwargs)
        return d

    def update(self, e=None, **f):
        d = e or dict()
        d.update(f)
        for k in d:
            setattr(self, k, d[k])

    def pop(self, k, d=None):
        delattr(self, k)
        return super(AbcDict, self).pop(k, d)

    def merge(self, d):
        self.__init__(d)

    def deep_merge(self, d=None, **kwargs):
        # d = self.__load__(d, **kwargs)
        # for k, v in d.items():
        #     setattr(self, k, v)
        # TODO deep merge
        pass

    def dump(self, save_path):
        if isinstance(save_path, str):
            save_path = Path(save_path)
        jsons = json.loads(str(self).replace("'", '"'))
        yaml.safe_dump(jsons, save_path.open('w'))
