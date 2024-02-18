import time
import concurrent.futures

import urllib3
from rich.console import Console

from .util import MetalArchivesDirectory, normalize_keyword_casing
from ..interface import Genre, GenrePage, GenrePages


class GenreError(Exception):
    def __init__(self, status_code, url):
        self.status_code = status_code
        self.url = url

    def __repr__(self):
        return self.__name__ + f'<{self.status_code}: {self.url}>'


class GenreBands:

    @staticmethod
    def get_genre(genre: Genre, echo=0, page_size=500, wait=.1, verbose=True) -> GenrePage:
        console = Console()
        data = GenrePages()
        record_cursor = 0
        timeout = urllib3.Timeout(connect=3.0, read=9.0)

        genre_page_metadata = dict(genre=genre.value)

        while True:
            endpoint = MetalArchivesDirectory.genre(genre.value, echo, record_cursor, page_size)

            if verbose:
                console.log('GET', endpoint)

            response = urllib3.request('GET', endpoint, timeout=timeout)
            if response.status == 429:
                if verbose:
                    console.log(f'429: Too Many Requests at {endpoint}')

                time.sleep(10)
                continue
            
            elif response.status != 200:
                raise GenreError(response.status, endpoint)

            kwargs = normalize_keyword_casing(response.json())
            genre_bands = GenrePage(metadata=genre_page_metadata, **kwargs)
            
            data.append(genre_bands)

            record_cursor += genre_bands.count
            echo += 1
            
            if genre_bands.total_records - 1 > record_cursor:
                time.sleep(wait)
                continue
            break

        return data.combine()
    
    @classmethod
    def get_genres(cls, *genres: list[Genre], echo=0, page_size=500, wait=.1, verbose=True) -> GenrePage:
        data = GenrePages()

        if len(genres) == 0:
            genres = [g for g in Genre]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            genre_futures = [executor.submit(cls.get_genre, genre, 
                                             echo=echo, page_size=page_size, 
                                             wait=wait, verbose=verbose) 
                             for genre in genres]
        
            for future in concurrent.futures.as_completed(genre_futures):
                data.append(future.result())

        return data.combine()
