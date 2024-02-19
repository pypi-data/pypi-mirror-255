"""
#
# Mock utilities
#
# Copyright(c) 2021-, Carium, Inc. All rights reserved.
#
"""

from abc import abstractmethod
from typing import Any, Optional, Protocol, Union
from unittest import mock


class _Patchlike(Protocol):
    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        raise NotImplementedError


PatchType = Union[mock._patch, mock._patch_dict, _Patchlike]


class MockManager:
    def __init__(self):
        self._patches = {}
        self.fakes = {}  # return values of starting each patch

    def patch(self, target: str, **kwargs) -> Any:
        _patch = mock.patch(target, **kwargs)
        return self.add(_patch, name=target)

    def patch_dict(self, in_dict: Union[dict, str], *args, **kwargs) -> Any:
        _patch = mock.patch.dict(in_dict, *args, **kwargs)
        return self.add(_patch)

    def patch_object(self, target: Any, attribute: str, **kwargs) -> Any:
        _patch = mock.patch.object(target, attribute, **kwargs)
        return self.add(_patch)

    def add(self, patch: PatchType, name: Optional[str] = None) -> Any:
        """Start a patch and make it managed by the MockManager"""
        name = name or str(id(patch))
        assert name not in self._patches, f"{name} already patched!"  # we don't support a double patch b/c flat dict
        self._patches[name] = patch
        self.fakes[name] = patch.start()
        return self.fakes[name]

    def cleanup(self) -> "MockManager":
        for _patch in self._patches.values():
            _patch.stop()

        self._patches.clear()
        self.fakes.clear()
        return self

    def remove(self, name: str) -> PatchType:
        """remove and stop the patch if exists"""
        patch = self._patches.pop(name, None)
        if patch:
            patch.stop()
            self.fakes.pop(name)

        return patch
