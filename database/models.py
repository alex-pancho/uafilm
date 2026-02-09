from dataclasses import dataclass
from typing import Optional


@dataclass
class UkinoModel:
    _id: Optional[int] = None
    title_ua: Optional[str] = None
    title_or: Optional[str] = None
    type_src: Optional[str] = None   # movie | series
    year: Optional[str] = None
    director: Optional[str] = None
    description: Optional[str] = None
    poster: Optional[str] = None
    imdb: Optional[str] = None


@dataclass
class Season:
    _id: Optional[int] = None
    content_id: Optional[int] = None   # FK -> UkinoModel._id
    season_number: int = 0             # 0 = фільм
    title_season: Optional[str] = None


@dataclass
class Playlist:
    _id: Optional[int] = None
    content_id: Optional[int] = None   # FK -> UkinoModel._id
    season_id: Optional[int] = None    # FK -> Season._id
    info: Optional[str] = None         # JSON/опис
    source: Optional[str] = None       # uakino / ashdi / local
    m3u_url: Optional[str] = None
    subtitle: Optional[str] = None
    ext_player: Optional[str] = None   # зовнішній плеєр (iframe/link)
