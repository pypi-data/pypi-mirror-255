
from dataclasses import dataclass, field, asdict, InitVar

import lxml.html

from .band import BandProfile


@dataclass
class SearchResults:
    url: str
    html: InitVar[str]

    bands: list[BandProfile] = field(init=False)

    def __post_init__(self, search_results_html: bytes):
        search_results_document = lxml.html.document_fromstring(search_results_html)