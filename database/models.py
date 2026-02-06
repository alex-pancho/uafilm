from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass
class UkinoModel:
    _id: Optional[int] = None
    title_ua: Optional[str] = None
    title_or: Optional[str] = None
    type_src: Optional[str] = None
    year: Optional[str] = None
    director: Optional[str] = None
    description: Optional[str] = None
    poster: Optional[str] = None
    imdb: Optional[str] = None
    m3u_links: List[str] = field(default_factory=list)
    json: Dict = field(default_factory=dict)

    # @classmethod
    # def from_model(cls, model: UkinoModel):
    #     return cls(**model.__dict__)
