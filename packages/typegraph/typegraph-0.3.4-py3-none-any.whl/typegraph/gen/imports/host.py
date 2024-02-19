from ..types import Result
from abc import abstractmethod
from typing import List, Protocol

class HostHost(Protocol):
    @abstractmethod
    def expand_glob(self, root: str, exclude: List[str]) -> Result[List[str], str]:
        raise NotImplementedError
    @abstractmethod
    def read_file(self, path: str) -> Result[bytes, str]:
        raise NotImplementedError
    @abstractmethod
    def get_cwd(self) -> Result[str, str]:
        raise NotImplementedError

