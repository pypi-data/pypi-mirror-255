from dataclasses import dataclass, asdict
from typing import List


@dataclass
class SearchResultEntity:
    text: str = None
    vector: List[float] = None
    score: float = None
    original_entity: dict = None
    metadata: dict = None

    def as_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(dict_object: dict):
        return SearchResultEntity(**dict_object)
