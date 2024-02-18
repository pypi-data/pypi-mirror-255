import os
import re
import warnings
import json
from datetime import datetime
from urllib.parse import urlencode

import urllib3


def normalize_keyword_casing(dictionary: dict):
    def normalize_to_snakecase(match: re.Match):
        preceding_text = match.group(1)
        text = match.group(2).lower()

        if preceding_text == '':
            return text

        return f'{preceding_text}_{text}'

    camel_case = re.compile(r'(\b|[a-z])([A-Z])')

    return {camel_case.sub(normalize_to_snakecase, k): v
            for k, v in dictionary.items()}



class DecodeErrorWarning(UserWarning):
    ...



def get_json(endpoint: str, timeout: urllib3.Timeout) -> dict:
    response = urllib3.request('GET', endpoint, timeout=timeout)
    
    try:
        response_text = response.data.decode('utf-8', 'replace')
        response_json = json.loads(response_text)
    except json.decoder.JSONDecodeError as e:
        response_text = response_text[:e.pos] + Constant.ERROR_PLACEHOLDER + response_text[e.pos + 1:]
        response_json = json.loads(response_text)

        error_message = f'JSONDecodeError at char {e.pos} of {endpoint}'
        response_json['error'] = error_message
        warnings.warn(error_message, DecodeErrorWarning)
    
    finally:
        return response_json




class Constant:
    ERROR_PLACEHOLDER = '«error»'


class MetalArchivesDirectory:

    METAL_ARCHIVES_ROOT = 'https://www.metal-archives.com'
    METAL_ARCHIVES_SEARCH = 'https://www.metal-archives.com/search/advanced/searching/bands'
    METAL_ARCHIVES_BAND_LINKS = 'https://www.metal-archives.com/link/ajax-list/type/band/id'
    METAL_ARCHIVES_GENRE = 'https://www.metal-archives.com/browse/ajax-genre/g'

    @classmethod
    def genre(cls, genre: str, echo=0, display_start=0, display_length=100):
        genre_endpoint = f'browse/ajax-genre/g/{genre}/json/1'
        return (f'{os.path.join(cls.METAL_ARCHIVES_ROOT, genre_endpoint)}'
                f'?sEcho={echo}&iDisplayStart={display_start}&iDisplayLength={display_length}')

    @classmethod
    def upcoming_releases(cls, echo=0, display_start=0, display_length=100,
                          from_date=datetime.now().strftime('%Y-%m-%d'), 
                          to_date='0000-00-00'):

        return (f'{os.path.join(cls.METAL_ARCHIVES_ROOT, "release/ajax-upcoming/json/1")}'
                f'?sEcho={echo}&iDisplayStart={display_start}&iDisplayLength={display_length}'
                f'&fromDate={from_date}&toDate={to_date}')

    @classmethod
    def search_query(cls, band_name=None, genre=None, country=None, location=None, 
                     themes=None, label_name=None, notes=None, status=None, 
                     year_from=None, year_to=None):
        """
        ?bandNotes=&status=&themes=&location=&bandLabelName=#bands
        """
        query_params = {'exactBandMatch': 1, 'bandName': band_name, 'genre': genre,
                        'country': country, 'status': status, 'location': location,
                        'bandNotes': notes, 'themes': themes, 'bandLabelName': label_name,
                        'yearCreationFrom': year_from, 'yearCreationTo': year_to}
        
        query_str = urlencode({k: v for k, v in query_params.items() if v is not None})

        return query_str
    
    @classmethod
    def links_query(cls, metallum_id: int) -> str:
        return os.path.join(cls.METAL_ARCHIVES_BAND_LINKS, str(metallum_id))