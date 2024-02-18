class DataCollector:
    _COLLECTORS = {}

    async def fetch_data(self):
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        cls._COLLECTORS[kwargs["name"]] = cls

    @classmethod
    def make_collector(cls, name, *args, **kwargs):
        return cls._COLLECTORS[name](*args, **kwargs)


# triggering collectors to register
from unctl.lib.collectors.k8s import *  # noqa
from unctl.lib.collectors.mysql import *  # noqa
from unctl.lib.collectors.base import *  # noqa
