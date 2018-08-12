# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2018 SnowyLuma

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import collections

from ruamel import yaml


class Config(collections.Mapping):
    """
    Mousey's Configuration.

    Parameters
    ----------
    config : dict
        The configuration as a dictionary.
    """

    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = {k: Config(v) if isinstance(v, dict) else v for k, v in config.items()}

    def __getattr__(self, item):
        try:
            return self._config[item]
        except KeyError as e:
            raise AttributeError from e

    def __getitem__(self, item):
        return self._config[item]

    def __contains__(self, item):
        return item in self._config

    def __iter__(self):
        return iter(self._config)

    def __len__(self):
        return len(self._config)

    @classmethod
    def from_file(cls, path='config.yaml'):
        """
        Create a Config from a file at a specified path.

        Parameters
        ----------
        path : Optional[str]
            The path to the configuration file. Defaults to 'config.yaml'.
        """

        with open(path, 'rb') as f:
            loaded = yaml.safe_load(f)

        return cls(loaded)
