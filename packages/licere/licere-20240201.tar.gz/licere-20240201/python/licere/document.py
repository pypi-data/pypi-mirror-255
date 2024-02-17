from collections import UserDict
from dataclasses import (
    dataclass,
    field,
)
from pathlib import Path


class Data(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


class Document: #aka License

    name: str

    template: str

    # shorter name for commandline/etc purposes
    aliases: set = field(default_factory=set)

    # list of data names required
    requires: set = field(default_factory=set)

    data: Data = field(default_factory=Data)

    # path to the directory where the license was loaded for relative path resolution
    path: Path = None

    package: str = None

    builtin: bool = False

    def __init__(self, name, template=None, aliases=None, requires=None, data=None):
        self.name = name
        self.template = template
        self.aliases = aliases or {}
        self.requires = requires or {}
        self.data = data or Data()

    def __call__(self, **kwargs) -> "Document":
        d = {
            "name": kwargs.pop("name", None) or self.name, # can inherit
            "template": kwargs.pop("template", None) or self.template, # can inherit
            "aliases": kwargs.pop("aliases", None), # must be unique

            # merge required arguments with base
            "requires": kwargs.pop("requires", set()) if "requires" in kwargs else self.requires,

            # merge data with base
            "data": {
                **self.data, **kwargs.get("data", {})
            },
        }
        return Document(**d)
