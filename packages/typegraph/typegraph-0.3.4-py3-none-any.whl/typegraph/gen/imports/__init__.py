from .host import HostHost
from dataclasses import dataclass

@dataclass
class RootImports:
    host: HostHost
