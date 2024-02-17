class DataPackage:
    def __init__(self, **kwargs):
        self._data = {}
        for k, v in kwargs.items():
            self._data[str(k)] = DataPackage.__check_value(v)

    def __repr__(self):
        return repr(self._data)

    @staticmethod
    def __check_value(value):
        if isinstance(value, dict):
            return DataPackage(**value)
        if isinstance(value, list):
            return [DataPackage.__check_value(x) for x in value]
        return value

    def _get_value(self, child_key, *keys):
        child = self._data.get(child_key)
        if not keys:
            return child
        if isinstance(child, DataPackage):
            return child._get_value(*keys)
        return NotImplemented

    def _set_value(self, child_key, *keys, value=None):
        if not keys and child_key in self._data:
            self._data[child_key] = value
            return
        child = self._data[child_key]
        if isinstance(child, DataPackage):
            child._set_value(*keys, value=value)
            return
        raise KeyError('Invalid key path:', child_key, keys)

    def __getitem__(self, item):
        keys = str(item).split('.')
        return self._get_value(*keys)

    def __setitem__(self, key, value):
        keys = str(key).split('.')
        return self._set_value(*keys, value=DataPackage.__check_value(value))

    def __getattr__(self, item):
        keys = str(item).split('.')
        return self._get_value(*keys)

    def __setattr__(self, key, value):
        if str(key).startswith('_'):
            self.__dict__[key] = value
        else:
            self._data[str(key)] = DataPackage.__check_value(value)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return self._data.__iter__()

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()
